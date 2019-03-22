import json
import random

from multiprocessing import Manager, Process
import logging
from time import time

import requests
from django.db.models import Max
from kazoo.client import KazooClient
from demo.settings import ZOOKEEPER
from django.core.cache import cache
# from multiprocessing import Pool
# import threading

err_log = logging.getLogger('error')
logger = logging.getLogger('all')

lock_label = True
top_label = 0


def _acquire_zk_node():
    # logger.debug('zk1')
    try:
        zk = KazooClient(hosts=ZOOKEEPER['HOST'])
        zk.start()
    except Exception as e:
        err_log.error(e)
        zk.stop()
        raise Exception(1910)
    global boxs
    _boxs = []
    _node_list = zk.get_children('/B/')
    for vm in _node_list:
        # logger.debug(vm)
        box_list = zk.get_children('/B/' + vm + '/')
        for box in box_list:
            node = '/B/' + vm + '/' + box
            data, stat = zk.get(node)
            # _dict = json.loads(data)
            tup = (node, eval(data.decode("utf-8"))['Add'])
            _boxs.append(tup)
    zk.stop()
    return _boxs


# 向底层发起请求，并将返回结果写入队列
def _writer(que, kb_id, kb_version, addr, issue, cp_id):
    start_time = time()
    addr = 'http://' + addr
    logger.debug('*****向%s发送请求---开始 ' % addr)
    headers = {'Content_Type': 'application/json'}
    _data = {'kbid': kb_id, 'version': str(kb_version), 'question': issue, 'companyid': cp_id}
    data = json.dumps(_data)
    try:
        res = requests.post(addr, data=data, headers=headers)#, timeout=4)
        logger.info('------post request ---time:%.5f ' % (time() - start_time))

        if res.status_code == 500:
            logger.debug('addr %s Response 500 ' % addr)
        else:
            _ret = json.loads(res.text)
            ret, code = _ret['data'], _ret['code']
            ret['kbId'] = kb_id
            # logger.debug('向%s发送请求---完成 , 响应数据为%s' % (addr, ret))
            if code == 0:
                que.put(ret)
                logger.debug('向%s发送请求成功，向queue写入数据, 写入数据为%s' % (addr, ret))
                # logger.debug(que.empty())
            elif code == 1 and 'score' in ret.keys() and ret['score'] == 0:
                que.put({'not_match': kb_id})
                logger.debug('向%s发送请求未匹配到答案, 知识库为%s, 版本号为%s, 公司id为%s, 问题为%s' % (addr, kb_id, str(kb_version), cp_id, issue))
            else:
                que.put({'fail': kb_id})
                logger.debug('向%s发送请求失败, 知识库为%s, 版本号为%s, 公司id为%s, 问题为%s, 问答结果为:%s ' % (addr, kb_id, str(kb_version), cp_id, issue, ret))
    except requests.exceptions.Timeout:
        logger.debug('Time out in %s' % addr)

def query_request(kb_ids, issue, kb_vers_map):
    """
    requirement: (1)cache中查找知识库的地址，cache中没有的，则为其在cache中没有被其他kb占用的box中选取BOX，并异步写入其TARGET
                 (2)遍历/B/vm/下的子节点，找到空闲节点，为其赋一个知识库，单独起进程发送请求，请求结果放入queue

    param: kb_ids 列表 
    return: 
    """

    # 取cache中已有的kb
    logger.debug('start get add')
    start_get_add = time()

    kb_add_dict = cache.get_many(kb_ids)

    no_kbs = set(kb_ids) - set(kb_add_dict.keys())

    logger.debug('no_kbs:%s' % no_kbs)
    # 为cache中没有的kb赋予box
    boxs = [('/B/83c4ee846cf2/B70/', '192.168.30.187:8000/70'), ('/B/83c4ee846cf2/B74/', '192.168.30.187:8000/74'),
            ('/B/83c4ee846cf2/B73/', '192.168.30.187:8000/73'), ('/B/83c4ee846cf2/B72/', '192.168.30.187:8000/72'),
            ('/B/83c4ee846cf2/B71/', '192.168.30.187:8000/71'), ('/B/83c4ee846cf2/B30/', '192.168.30.187:8000/30'),
            ('/B/83c4ee846cf2/B23/', '192.168.30.187:8000/23'), ('/B/83c4ee846cf2/B22/', '192.168.30.187:8000/22'),
            ('/B/83c4ee846cf2/B21/', '192.168.30.187:8000/21'), ('/B/83c4ee846cf2/B20/', '192.168.30.187:8000/20'),
            ('/B/83c4ee846cf2/B27/', '192.168.30.187:8000/27'), ('/B/83c4ee846cf2/B26/', '192.168.30.187:8000/26'),
            ('/B/83c4ee846cf2/B25/', '192.168.30.187:8000/25'), ('/B/83c4ee846cf2/B24/', '192.168.30.187:8000/24'),
            ('/B/83c4ee846cf2/B66/', '192.168.30.187:8000/66'), ('/B/83c4ee846cf2/B67/', '192.168.30.187:8000/67'),
            ('/B/83c4ee846cf2/B64/', '192.168.30.187:8000/64'), ('/B/83c4ee846cf2/B29/', '192.168.30.187:8000/29'),
            ('/B/83c4ee846cf2/B65/', '192.168.30.187:8000/65'), ('/B/83c4ee846cf2/B28/', '192.168.30.187:8000/28'),
            ('/B/83c4ee846cf2/B68/', '192.168.30.187:8000/68'), ('/B/83c4ee846cf2/B69/', '192.168.30.187:8000/69'),
            ('/B/83c4ee846cf2/B5/', '192.168.30.187:8000/5'), ('/B/83c4ee846cf2/B4/', '192.168.30.187:8000/4'),
            ('/B/83c4ee846cf2/B81/', '192.168.30.187:8000/81'), ('/B/83c4ee846cf2/B3/', '192.168.30.187:8000/3'),
            ('/B/83c4ee846cf2/B80/', '192.168.30.187:8000/80'), ('/B/83c4ee846cf2/B2/', '192.168.30.187:8000/2'),
            ('/B/83c4ee846cf2/B83/', '192.168.30.187:8000/83'), ('/B/83c4ee846cf2/B9/', '192.168.30.187:8000/9'),
            ('/B/83c4ee846cf2/B82/', '192.168.30.187:8000/82'), ('/B/83c4ee846cf2/B8/', '192.168.30.187:8000/8'),
            ('/B/83c4ee846cf2/B85/', '192.168.30.187:8000/85'), ('/B/83c4ee846cf2/B7/', '192.168.30.187:8000/7'),
            ('/B/83c4ee846cf2/B84/', '192.168.30.187:8000/84'), ('/B/83c4ee846cf2/B6/', '192.168.30.187:8000/6'),
            ('/B/83c4ee846cf2/B40/', '192.168.30.187:8000/40'), ('/B/83c4ee846cf2/B41/', '192.168.30.187:8000/41'),
            ('/B/83c4ee846cf2/B32/', '192.168.30.187:8000/32'), ('/B/83c4ee846cf2/B31/', '192.168.30.187:8000/31'),
            ('/B/83c4ee846cf2/B34/', '192.168.30.187:8000/34'), ('/B/83c4ee846cf2/B33/', '192.168.30.187:8000/33'),
            ('/B/83c4ee846cf2/B36/', '192.168.30.187:8000/36'), ('/B/83c4ee846cf2/B35/', '192.168.30.187:8000/35'),
            ('/B/83c4ee846cf2/B38/', '192.168.30.187:8000/38'), ('/B/83c4ee846cf2/B37/', '192.168.30.187:8000/37'),
            ('/B/83c4ee846cf2/B75/', '192.168.30.187:8000/75'), ('/B/83c4ee846cf2/B76/', '192.168.30.187:8000/76'),
            ('/B/83c4ee846cf2/B39/', '192.168.30.187:8000/39'), ('/B/83c4ee846cf2/B77/', '192.168.30.187:8000/77'),
            ('/B/83c4ee846cf2/B78/', '192.168.30.187:8000/78'), ('/B/83c4ee846cf2/B79/', '192.168.30.187:8000/79'),
            ('/B/83c4ee846cf2/B1/', '192.168.30.187:8000/1'), ('/B/83c4ee846cf2/B19/', '192.168.30.187:8000/19'),
            ('/B/83c4ee846cf2/B17/', '192.168.30.187:8000/17'), ('/B/83c4ee846cf2/B18/', '192.168.30.187:8000/18'),
            ('/B/83c4ee846cf2/B90/', '192.168.30.187:8000/90'), ('/B/83c4ee846cf2/B51/', '192.168.30.187:8000/51'),
            ('/B/83c4ee846cf2/B11/', '192.168.30.187:8000/11'), ('/B/83c4ee846cf2/B52/', '192.168.30.187:8000/52'),
            ('/B/83c4ee846cf2/B12/', '192.168.30.187:8000/12'), ('/B/83c4ee846cf2/B50/', '192.168.30.187:8000/50'),
            ('/B/83c4ee846cf2/B10/', '192.168.30.187:8000/10'), ('/B/83c4ee846cf2/B15/', '192.168.30.187:8000/15'),
            ('/B/83c4ee846cf2/B16/', '192.168.30.187:8000/16'), ('/B/83c4ee846cf2/B13/', '192.168.30.187:8000/13'),
            ('/B/83c4ee846cf2/B14/', '192.168.30.187:8000/14'), ('/B/83c4ee846cf2/B49/', '192.168.30.187:8000/49'),
            ('/B/83c4ee846cf2/B48/', '192.168.30.187:8000/48'), ('/B/83c4ee846cf2/B47/', '192.168.30.187:8000/47'),
            ('/B/83c4ee846cf2/B46/', '192.168.30.187:8000/46'), ('/B/83c4ee846cf2/B45/', '192.168.30.187:8000/45'),
            ('/B/83c4ee846cf2/B44/', '192.168.30.187:8000/44'), ('/B/83c4ee846cf2/B43/', '192.168.30.187:8000/43'),
            ('/B/83c4ee846cf2/B42/', '192.168.30.187:8000/42'), ('/B/83c4ee846cf2/B88/', '192.168.30.187:8000/88'),
            ('/B/83c4ee846cf2/B89/', '192.168.30.187:8000/89'), ('/B/83c4ee846cf2/B86/', '192.168.30.187:8000/86'),
            ('/B/83c4ee846cf2/B87/', '192.168.30.187:8000/87'), ('/B/83c4ee846cf2/B60/', '192.168.30.187:8000/60'),
            ('/B/83c4ee846cf2/B61/', '192.168.30.187:8000/61'), ('/B/83c4ee846cf2/B62/', '192.168.30.187:8000/62'),
            ('/B/83c4ee846cf2/B63/', '192.168.30.187:8000/63'), ('/B/83c4ee846cf2/B58/', '192.168.30.187:8000/58'),
            ('/B/83c4ee846cf2/B57/', '192.168.30.187:8000/57'), ('/B/83c4ee846cf2/B59/', '192.168.30.187:8000/59'),
            ('/B/83c4ee846cf2/B54/', '192.168.30.187:8000/54'), ('/B/83c4ee846cf2/B53/', '192.168.30.187:8000/53'),
            ('/B/83c4ee846cf2/B56/', '192.168.30.187:8000/56'), ('/B/83c4ee846cf2/B55/', '192.168.30.187:8000/55'),
            ('/B/d204c1d12b8a/B70/', '192.168.30.186:8000/70'), ('/B/d204c1d12b8a/B74/', '192.168.30.186:8000/74'),
            ('/B/d204c1d12b8a/B73/', '192.168.30.186:8000/73'), ('/B/d204c1d12b8a/B72/', '192.168.30.186:8000/72'),
            ('/B/d204c1d12b8a/B71/', '192.168.30.186:8000/71'), ('/B/d204c1d12b8a/B30/', '192.168.30.186:8000/30'),
            ('/B/d204c1d12b8a/B23/', '192.168.30.186:8000/23'), ('/B/d204c1d12b8a/B22/', '192.168.30.186:8000/22'),
            ('/B/d204c1d12b8a/B21/', '192.168.30.186:8000/21'), ('/B/d204c1d12b8a/B20/', '192.168.30.186:8000/20'),
            ('/B/d204c1d12b8a/B27/', '192.168.30.186:8000/27'), ('/B/d204c1d12b8a/B26/', '192.168.30.186:8000/26'),
            ('/B/d204c1d12b8a/B25/', '192.168.30.186:8000/25'), ('/B/d204c1d12b8a/B24/', '192.168.30.186:8000/24'),
            ('/B/d204c1d12b8a/B66/', '192.168.30.186:8000/66'), ('/B/d204c1d12b8a/B67/', '192.168.30.186:8000/67'),
            ('/B/d204c1d12b8a/B64/', '192.168.30.186:8000/64'), ('/B/d204c1d12b8a/B29/', '192.168.30.186:8000/29'),
            ('/B/d204c1d12b8a/B65/', '192.168.30.186:8000/65'), ('/B/d204c1d12b8a/B28/', '192.168.30.186:8000/28'),
            ('/B/d204c1d12b8a/B68/', '192.168.30.186:8000/68'), ('/B/d204c1d12b8a/B69/', '192.168.30.186:8000/69'),
            ('/B/d204c1d12b8a/B5/', '192.168.30.186:8000/5'), ('/B/d204c1d12b8a/B4/', '192.168.30.186:8000/4'),
            ('/B/d204c1d12b8a/B81/', '192.168.30.186:8000/81'), ('/B/d204c1d12b8a/B3/', '192.168.30.186:8000/3'),
            ('/B/d204c1d12b8a/B80/', '192.168.30.186:8000/80'), ('/B/d204c1d12b8a/B2/', '192.168.30.186:8000/2'),
            ('/B/d204c1d12b8a/B83/', '192.168.30.186:8000/83'), ('/B/d204c1d12b8a/B9/', '192.168.30.186:8000/9'),
            ('/B/d204c1d12b8a/B82/', '192.168.30.186:8000/82'), ('/B/d204c1d12b8a/B8/', '192.168.30.186:8000/8'),
            ('/B/d204c1d12b8a/B85/', '192.168.30.186:8000/85'), ('/B/d204c1d12b8a/B7/', '192.168.30.186:8000/7'),
            ('/B/d204c1d12b8a/B84/', '192.168.30.186:8000/84'), ('/B/d204c1d12b8a/B6/', '192.168.30.186:8000/6'),
            ('/B/d204c1d12b8a/B40/', '192.168.30.186:8000/40'), ('/B/d204c1d12b8a/B41/', '192.168.30.186:8000/41'),
            ('/B/d204c1d12b8a/B32/', '192.168.30.186:8000/32'), ('/B/d204c1d12b8a/B31/', '192.168.30.186:8000/31'),
            ('/B/d204c1d12b8a/B34/', '192.168.30.186:8000/34'), ('/B/d204c1d12b8a/B33/', '192.168.30.186:8000/33'),
            ('/B/d204c1d12b8a/B36/', '192.168.30.186:8000/36'), ('/B/d204c1d12b8a/B35/', '192.168.30.186:8000/35'),
            ('/B/d204c1d12b8a/B38/', '192.168.30.186:8000/38'), ('/B/d204c1d12b8a/B37/', '192.168.30.186:8000/37'),
            ('/B/d204c1d12b8a/B75/', '192.168.30.186:8000/75'), ('/B/d204c1d12b8a/B76/', '192.168.30.186:8000/76'),
            ('/B/d204c1d12b8a/B39/', '192.168.30.186:8000/39'), ('/B/d204c1d12b8a/B77/', '192.168.30.186:8000/77'),
            ('/B/d204c1d12b8a/B78/', '192.168.30.186:8000/78'), ('/B/d204c1d12b8a/B79/', '192.168.30.186:8000/79'),
            ('/B/d204c1d12b8a/B1/', '192.168.30.186:8000/1'), ('/B/d204c1d12b8a/B19/', '192.168.30.186:8000/19'),
            ('/B/d204c1d12b8a/B17/', '192.168.30.186:8000/17'), ('/B/d204c1d12b8a/B18/', '192.168.30.186:8000/18'),
            ('/B/d204c1d12b8a/B90/', '192.168.30.186:8000/90'), ('/B/d204c1d12b8a/B51/', '192.168.30.186:8000/51'),
            ('/B/d204c1d12b8a/B11/', '192.168.30.186:8000/11'), ('/B/d204c1d12b8a/B52/', '192.168.30.186:8000/52'),
            ('/B/d204c1d12b8a/B12/', '192.168.30.186:8000/12'), ('/B/d204c1d12b8a/B50/', '192.168.30.186:8000/50'),
            ('/B/d204c1d12b8a/B10/', '192.168.30.186:8000/10'), ('/B/d204c1d12b8a/B15/', '192.168.30.186:8000/15'),
            ('/B/d204c1d12b8a/B16/', '192.168.30.186:8000/16'), ('/B/d204c1d12b8a/B13/', '192.168.30.186:8000/13'),
            ('/B/d204c1d12b8a/B14/', '192.168.30.186:8000/14'), ('/B/d204c1d12b8a/B49/', '192.168.30.186:8000/49'),
            ('/B/d204c1d12b8a/B48/', '192.168.30.186:8000/48'), ('/B/d204c1d12b8a/B47/', '192.168.30.186:8000/47'),
            ('/B/d204c1d12b8a/B46/', '192.168.30.186:8000/46'), ('/B/d204c1d12b8a/B45/', '192.168.30.186:8000/45'),
            ('/B/d204c1d12b8a/B44/', '192.168.30.186:8000/44'), ('/B/d204c1d12b8a/B43/', '192.168.30.186:8000/43'),
            ('/B/d204c1d12b8a/B42/', '192.168.30.186:8000/42'), ('/B/d204c1d12b8a/B88/', '192.168.30.186:8000/88'),
            ('/B/d204c1d12b8a/B89/', '192.168.30.186:8000/89'), ('/B/d204c1d12b8a/B86/', '192.168.30.186:8000/86'),
            ('/B/d204c1d12b8a/B87/', '192.168.30.186:8000/87'), ('/B/d204c1d12b8a/B60/', '192.168.30.186:8000/60'),
            ('/B/d204c1d12b8a/B61/', '192.168.30.186:8000/61'), ('/B/d204c1d12b8a/B62/', '192.168.30.186:8000/62'),
            ('/B/d204c1d12b8a/B63/', '192.168.30.186:8000/63'), ('/B/d204c1d12b8a/B58/', '192.168.30.186:8000/58'),
            ('/B/d204c1d12b8a/B57/', '192.168.30.186:8000/57'), ('/B/d204c1d12b8a/B59/', '192.168.30.186:8000/59'),
            ('/B/d204c1d12b8a/B54/', '192.168.30.186:8000/54'), ('/B/d204c1d12b8a/B53/', '192.168.30.186:8000/53'),
            ('/B/d204c1d12b8a/B56/', '192.168.30.186:8000/56'), ('/B/d204c1d12b8a/B55/', '192.168.30.186:8000/55')]
    boxs_free = []
    if kb_add_dict:
        boxs_free = set(dict(boxs).keys()) - set(dict(kb_add_dict.values()).keys())
    else:
        boxs_free = set(dict(boxs).keys())

    if len(boxs_free) < len(no_kbs):
        rest_kbs = no_kbs[len(boxs_free):]
        kb_ids = set(kb_ids) - set(rest_kbs)

    # 写入cache
    boxs_free_info = filter(lambda x: x[0] in boxs_free, boxs)
    temp_kb_box_list = list(zip(no_kbs, boxs_free_info))
    cache_ret = map(lambda x: cache.set(x[0], x[1], 30 * 60), temp_kb_box_list)
    logger.debug('cache_ret:%s' % list(cache_ret))

    kb_add_dict = cache.get_many(kb_ids)
    logger.debug('kb_add_dict:%s' % kb_add_dict)
    logger.debug('------get address time:%.5f' % (time() - start_get_add))
    logger.debug('start box-request ')
    start_request = time()
    num = len(kb_ids)
    q = Manager().Queue()
    p_list = []
    for i in range(0, num):
        kb = kb_ids[i]
        version = kb_vers_map[kb]
        add = kb_add_dict[kb][1]
        logger.debug('Target:%s Add:%s' % (kb, add))
        temp_p = Process(target=_writer, args=(q, kb, version, add, issue))
        p_list.append(temp_p)
        temp_p.start()

    for pr in p_list:
        pr.join()
    logger.debug('------box-request time:%.5f' % (time() - start_request))

    start_get_msg = time()
    i = 0
    ret = {'no_box': [], 'ans': [], 'not_match': [], 'fail': []}
    while not q.empty():
        msg = q.get()
        if 'not_match' in msg.keys():
            ret['not_match'].append(msg['not_match'])
        elif 'fail' in msg.keys():
            ret['fail'].append(msg['fail'])
        else:
            ret['ans'].append(msg)
        logger.debug('------%d msg:%s' % (i, msg))
        i += 1
    logger.debug('------get answers time:%.5f' % (time() - start_get_msg))

    # 异步写入zk
    # set_box_zk.delay(temp_kb_box_list)

    return ret

def query_request_z(kb_ids, issue, kb_vers_map, cp_id):
    """
    requirement: (1)cache中查找知识库的地址，cache中没有的，则为其在cache中没有被其他kb占用的box中选取BOX，并异步写入其TARGET
                 (2)遍历/B/vm/下的子节点，找到空闲节点，为其赋一个知识库，单独起进程发送请求，请求结果放入queue

    param: kb_ids 列表
    return:
    """

    # 取cache中已有的kb
    # start_get_add = time()

    # kb_add_dict = cache.get_many(kb_ids)

    # no_kbs = set(kb_ids) - set(kb_add_dict.keys())

    # logger.debug('no_kbs:%s' % no_kbs)
    # 为cache中没有的kb赋予box

    if cache.ttl("boxs") == 0:
        cache.set("boxs", str(_acquire_zk_node()), timeout=1209600)

    boxs = eval(cache.get("boxs"))
    add_dict = list(dict(boxs).values())
    # logger.debug(add_dict)

    start_request = time()
    num = len(kb_ids)
    global lock_label
    while True:
        if lock_label:
            lock_label = False
            break

    global top_label
    seed = int(top_label)
    temp = (seed + num) % len(boxs)
    top_label = temp

    lock_label = True

    logger.debug('Question: %s' % issue)
    q = Manager().Queue()
    p_list = []
    for i in range(0, num):
        kb = kb_ids[i]
        version = kb_vers_map[kb]
        # add = kb_add_dict[kb][1]
        add = add_dict[(seed + i)%len(boxs)]
        logger.debug('Target:%s Add:%s version:%s' % (kb, add, str(version)))
        temp_p = Process(target=_writer, args=(q, kb, version, add, issue, cp_id))
        p_list.append(temp_p)
        temp_p.start()

    for pr in p_list:
        pr.join()

    # logger.debug('test.q is ' + q.empty())
    logger.debug('------box-request time:%.5f' % (time() - start_request))

    # start_get_msg = time()
    i = 0
    ret = {'no_box': [], 'ans': [], 'not_match': [], 'fail': []}
    while not q.empty():
        msg = q.get()
        if 'not_match' in msg.keys():
            ret['not_match'].append(msg['not_match'])
        elif 'fail' in msg.keys():
            ret['fail'].append(msg['fail'])
        else:
            ret['ans'].append(msg)
        logger.debug('------%d msg:%s' % (i, msg))
        i += 1
    # logger.debug('------get answers time:%.5f' % (time() - start_get_msg))
    return ret

def query_request_new(kb_ids, issue, kb_vers_map):
    """
    tips: cache形式：cache.set(box ,(kb, 0/1), 过期时间)
    requirement: (1)查看boxs列表, 对比cache中的boxs, 若有空闲的box，则为其赋一个知识库；
                    若没有空闲box，则在cache中寻找该KB已有的box。
                 (2)取出请求中所有知识库对应的BOX的地址，单独起进程发送请求，请求结果放入queue

    param: kb_ids 列表 
    return: 
    """

    # 取cache中已有的kb
    logger.debug('start get add')
    start_get_add = time()

    kb_add_dict = cache.get_many(kb_ids)

    no_kbs = set(kb_ids) - set(kb_add_dict.keys())
    boxs = cache.get('boxs')
    box_addr_dict = cache.get('box_infos')
    box_kb_dict = cache.get_many(boxs)

    box_kb_rest = list(filter(lambda x: (x[1][0] in boxs) and (not x[1][1]), box_kb_dict.items()))
    boxs_idle = list(filter(lambda x: not cache.get(x), boxs))
    logger.debug('boxs_idle:%s' % boxs_idle)

    # 为cache中没有的kb赋予box
    boxs_free = []
    if kb_add_dict:
        boxs_free = set(dict(boxs).keys()) - set(dict(kb_add_dict.values()).keys())
    else:
        boxs_free = set(dict(boxs).keys())

    if len(boxs_free) < len(no_kbs):
        rest_kbs = no_kbs[len(boxs_free):]
        kb_ids = set(kb_ids) - set(rest_kbs)

    # 写入cache
    boxs_free_info = filter(lambda x: x[0] in boxs_free, boxs)
    temp_kb_box_list = list(zip(no_kbs, boxs_free_info))
    cache_ret = map(lambda x: cache.set(x[0], x[1], 30 * 60), temp_kb_box_list)
    logger.debug('cache_ret:%s' % list(cache_ret))

    kb_add_dict = cache.get_many(kb_ids)
    logger.debug('kb_add_dict:%s' % kb_add_dict)
    logger.debug('------get address time:%.5f' % (time() - start_get_add))
    logger.debug('start box-request ')
    start_request = time()
    num = len(kb_ids)
    q = Manager().Queue()
    p_list = []
    for i in range(0, num):
        kb = kb_ids[i]
        version = kb_vers_map[kb]
        add = kb_add_dict[kb][1]
        logger.debug('Target:%s Add:%s' % (kb, add))
        temp_p = Process(target=_writer, args=(q, kb, version, add, issue))
        p_list.append(temp_p)
        temp_p.start()

    for pr in p_list:
        pr.join()
    logger.debug('------box-request time:%.5f' % (time() - start_request))

    start_get_msg = time()
    i = 0
    ret = {'no_box': [], 'ans': [], 'not_match': [], 'fail': []}
    while not q.empty():
        msg = q.get()
        if 'not_match' in msg.keys():
            ret['not_match'].append(msg['not_match'])
        elif 'fail' in msg.keys():
            ret['fail'].append(msg['fail'])
        else:
            ret['ans'].append(msg)
        logger.debug('------%d msg:%s' % (i, msg))
        i += 1
    logger.debug('------get answers time:%.5f' % (time() - start_get_msg))

    # 异步写入zk
    # set_box_zk.delay(temp_kb_box_list)

    return ret


def query_request_0(kb_ids, issue, kb_vers_map):
    """
    requirement: (1)zk中查找/B/节点下的vm 
                 (2)遍历/B/vm/下的子节点，找到空闲节点，为其赋一个知识库，单独起进程发送请求，请求结果放入queue

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
    q = Manager().Queue()
    ret = {'no_box': [], 'ans': [], 'not_match': [], 'fail': []}

    p_list = []
    random.shuffle(_node_list)
    for vm in _node_list:

        box_list = zk.get_children('/B/' + vm + '/')
        random.shuffle(box_list)

        for box in box_list:
            node = '/B/' + vm + '/' + box + '/'
            _str, _ = zk.get(node)
            _dict = json.loads(_str)
            if _dict['status'] == '0':
                target = kb_ids.pop()
                logger.debug(
                    '------Target:%s Add:%s' % (target, _dict['Add']))

                temp_p = Process(target=_writer, args=(q, target, kb_vers_map[target], _dict['Add'], issue))
                p_list.append(temp_p)
                temp_p.start()

            if not kb_ids:
                break

        if not kb_ids:
            break
    else:
        if kb_ids:
            ret['no_box'] = kb_ids
    for pr in p_list:
        pr.join()
    zk.stop()

    i = 0
    while not q.empty():
        msg = q.get()
        if 'not_match' in msg.keys():
            ret['not_match'].append(msg['not_match'])
        elif 'fail' in msg.keys():
            ret['fail'].append(msg['fail'])
        else:
            ret['ans'].append(msg)
        logger.debug('------%d msg:%s' % (i, msg))
        i += 1
    logger.debug('get answers finished')

    return ret


if __name__ == '__main__':
    li = ['a65d8a49-3ef6-11e8-8ff7-9147af98ebd3',
          'aa05890d-3eef-11e8-8ff7-9147af98ebd3',
          'aaea9113-3c8d-11e8-8a81-7bea23ee40200',
          'aaea9113-3c8d-11e8-8a81-7bea23ee40201',
          'aaea9113-3c8d-11e8-8a81-7bea23ee40211',
          'aaea9113-3c8d-11e8-8a81-7bea23ee40212',
          'aaea9113-3c8d-11e8-8a81-7bea23ee4078',
          'b8aa4b25-7de0-4114-92bd-7c254d145d02',
          'cef1720e-3efe-11e8-8ff7-9147af98ebd3']
    kb_vers_map = {'a65d8a49-3ef6-11e8-8ff7-9147af98ebd3': 1,
                   'aa05890d-3eef-11e8-8ff7-9147af98ebd3': 1,
                   'aaea9113-3c8d-11e8-8a81-7bea23ee40200': 1,
                   'aaea9113-3c8d-11e8-8a81-7bea23ee40201': 1,
                   'aaea9113-3c8d-11e8-8a81-7bea23ee40211': 1,
                   'aaea9113-3c8d-11e8-8a81-7bea23ee40212': 1,
                   'aaea9113-3c8d-11e8-8a81-7bea23ee4078': 1,
                   'b8aa4b25-7de0-4114-92bd-7c254d145d02': 1,
                   'cef1720e-3efe-11e8-8ff7-9147af98ebd3': 1}

    question = '你是谁啊'
    ret = query_request(li, question, kb_vers_map)
    print(ret)
