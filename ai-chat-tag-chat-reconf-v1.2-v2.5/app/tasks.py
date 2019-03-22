import json
import logging
from celery.task import task

# @task()
from django.core.cache import cache
from kazoo.client import KazooClient

from demo.settings import ZOOKEEPER

err_log = logging.getLogger('error')
logger = logging.getLogger('all')


def set_box_zk(kb_box_list):
    pass


def func_temp():
    """
    requirement: (1)zk中查找/B/节点下的vm 
                 (2)遍历/B/vm/下的子节点，找到空闲节点，为其赋一个知识库，单独起进程发送请求，请求结果放入queue

    param: kb_ids 列表 
    return: 
    """
    try:
        # zk = KazooClient(hosts=ZOOKEEPER['HOST'])
        zk = KazooClient(hosts='192.168.31.236:2181')
        zk.start()
    except Exception as e:
        err_log.error(e)
        raise Exception(1910)

    _node_list = zk.get_children('/B/')
    logger.debug('vm:%s' % _node_list)

    ret = []
    for vm in _node_list:

        box_list = zk.get_children('/B/' + vm + '/')

        for box in box_list:
            node = '/B/' + vm + '/' + box + '/'
            _str, _ = zk.get(node)
            _dict = json.loads(_str)
            ret.append((node, _dict['Add']))
            logger.debug('node:%s, Add:%s' %(node,_dict['Add']))
    cache.set('boxs', ret, 30 * 60)
    print(ret)

    zk.stop()
