import json
import random
import threading
import time
from datetime import datetime

from functools import reduce
from math import ceil
from queue import Queue

import logging
from kazoo.client import KazooClient

# from demo.settings import ZOOKEEPER
from demo.settings import ZOOKEEPER

err_log = logging.getLogger('error')
logger = logging.getLogger('all')


def get_zk_nodes(kb_ids):
    """
    requirement: (1)zk中查找/B/节点下的vm 
                 (2)到vm/k/节点下查找是否有 某KBn子节点；
                 (3)若有，查看/vm/k/KBn的子节点，
                    若其数量等于K个，在/B/vm/的子节点中查找这K个节点的对应节点，选择其中空闲节点；无空闲节点时，则等待，循环3次
                    若其数量未达到k个，则先查找/B/vm/下空闲节点，随机选择空闲节点/B/vm/Bj的最后一个标记Bj，创建子节点/vm/k/KBn/Bj，
                    然后为/B/vm/Bj的Target赋值；若/B/vm/下的空闲节点数量不够，则等待，循环3次。
                 (4)并指定空闲的/B/vm/Bj的Target为KBn,同时创建/vm/k/KBn/Bj 子节点
           
    PS: 不存在/vm/k/KBn/Bj 对应的B/vm/Bj的target为Null 
    logic: (1) zk中查找'/B/'节点下的vm
           (2) 到vm/k/节点下查找是否有 某KBn子节点.
                若有,则将其放入该vm对应的KB列表中;
                若没有KBn子节点，则将其放入最低级子节点最少的vm的KB列表中
           (3) 生成queue 
           (4) 为所用到每个vm生成一个进程，参数为：vm,该vm的K值, 属于本vm的KB, queue
           (5) 线程中：查看/vm/k/KBn节点是否存在，若存在，则查看它的子节点数量，等于K,则放在该vm 的键full的value字典中（KB:节点的结尾值），
                            否则，放入not_full的value列表中；不存在，则创建/vm/k/KBn子节点，并放在not_full的value中
                      遍历 B/vm 下的节点：
                        a: target为full中元素,且status为0的，取{target:地址}放入列表;
                        b: target为null,则从not_full中删除一个，指定为其target，取{target:地址}放入列表，并创建vm/k/KB/Bj节点
                        检查full和not_full是否都为空，都为空则跳出遍历；

                      循环3次，not_full和full为空时跳出；否则3次结束后,将not_full和full的值和addr一起存入queue
           (6) 主线程取出queque中值
           
    
    param: kb_ids 列表 
    return: 
    """
    try:
        zk = KazooClient(hosts=ZOOKEEPER['HOST'])
        zk.start()
    except Exception as e:
        err_log.error(e)
        raise Exception(1910)

    _node_list = zk.get_children('/B/')
    logger.debug('vm:%s' % _node_list)
    # vmk_list的元素为(vm, /vm/k/)
    vmk_list = list(
        map(lambda x: (x, '/' + x + '/' + zk.get_children('/' + x)[0] + '/', zk.get_children('/' + x)[0]), _node_list))
    vm_k_map = dict([(x[0], x[2]) for x in vmk_list])

    # vm_kbs_list的元素为(vm, [KBn, KBh, KBa……])
    vmk_kbs_list = list(map(lambda x: (x[0], zk.get_children(x[1])), vmk_list))
    kbs_in_vms = list(map(lambda x: (x[0], set(x[1]) & set(kb_ids)), vmk_kbs_list))
    vm_kbs_dict = dict(kbs_in_vms)

    kbs_in = []
    if vm_kbs_dict.values():
        kbs_in = reduce(lambda x, y: x + list(y), vm_kbs_dict.values(), [])
    kbs_no = set(kb_ids) - set(kbs_in)

    # 依据children的数量将/vm/k正序排序
    def _vmk_nodes_func(each):
        # zk.get_children(each) 取each('/vm/k/')的子节点 KBn
        ret = reduce(lambda x, y: x + zk.get_children(each[1] + y + '/'), zk.get_children(each[1]), [])
        return each[0], len(ret)

    _vmk_nodes_list = list(map(_vmk_nodes_func, vmk_list))

    # _vmk_nodes_list现有元素为 (vm, len())
    vmk_nodes_list = sorted(_vmk_nodes_list, key=lambda x: x[1])

    # 若没有KBn子节点，则将其放入最低级子节点最少的vm的KB列表中
    enlarge_rate = ceil(len(kbs_no) / len(vmk_nodes_list))
    _create_vm_kbs = list(
        map(lambda x, y: (x, y[0]), kbs_no, (vmk_nodes_list * int(enlarge_rate))))

    for itm in _create_vm_kbs:
        vm = itm[1]
        vm_kbs_dict[vm].add(itm[0])

    q = Queue()

    def _vm_zk_deal(vm, k, kbs, que):
        """
        get_zk_nodes的步骤5
        """
        # 查看/vm/k/KBn节点是否存在，若存在，则查看它的子节点等于K,则放在字典full中（KB:节点的结尾值），
        #  否则，放入not_full列表中；
        # 不存在，则创建/vm/k/KBn子节点，并放在not_full的value中
        not_full = []
        full = []
        address_dict = {}
        for kb in kbs:
            _path = '/' + vm + '/' + k + '/' + kb
            if zk.exists(_path):
                num = len(zk.get_children('/' + vm + '/' + k + '/' + kb))
                if num == int(k):
                    full.append(kb)
                elif num < int(k):
                    not_full.append(kb)
                else:
                    raise Exception('1910')
            else:
                zk.create(_path, None, None, ephemeral=False,
                          sequence=False, makepath=True)
                not_full.append(kb)

        # 取B / vm下的节点，
        # target为full中元素,且status为0的，直接将其status改为1，并取其地址放入列表;
        # target为null,则从not_full中删除一个，指定为其target，取其地址放入列表，并创建vm/k/KB/Bj节点
        box_list = zk.get_children('/B/' + vm + '/')
        logger.debug('full:%s' % full)
        logger.debug('not_full:%s' % not_full)

        i = 0
        while i < 3:
            random.shuffle(box_list)
            for box in box_list:
                # vm = 'zds-virtual-machine'
                node = '/B/' + vm + '/' + box + '/'
                _str, _ = zk.get(node)
                _dict = json.loads(_str)
                if (_dict['Target'] in full) and (_dict['status'] == '0'):
                    address_dict.update({_dict['Target']: _dict['Add']})
                    logger.debug('full.remove:%s, address:%s' % (_dict['Target'], _dict['Add']))
                    full.remove(_dict['Target'])

                elif (_dict['Target'] == 'Null') and not_full:
                    target = not_full.pop()
                    logger.debug('%s:%s'%(target, _dict['Add']))
                    address_dict.update({target: _dict['Add']})
                    logger.debug('not_full.pop:%s, address:%s' % (target, _dict['Add']))

                    _leaf_path = '/' + vm + '/' + k + '/' + target + '/' + box + '/'
                    if not zk.exists(_leaf_path):
                        zk.create(_leaf_path, None, None, ephemeral=False,
                                  sequence=False, makepath=True)

                if (not not_full) and (not full):
                    break

            if (not not_full) and (not full):
                break
            i += 1
        que.put({'address': address_dict, 'full': full, 'not_full': not_full})

    thread_list = []
    for vm in vm_kbs_dict.keys():
        t = threading.Thread(target=_vm_zk_deal, args=(vm, vm_k_map[vm], list(vm_kbs_dict[vm]), q))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

    zk.stop()
    num = 0
    ret = []
    while num < len(vm_kbs_dict):
        ret.append(q.get())
        num += 1
    logger.debug('%s' % ret)

    return ret


if __name__ == '__main__':
    ret = get_zk_nodes(['ku1111111', 'tesgfdsafdas'])
    logger.debug(ret)
