# -*- coding: utf-8 -*-
import requests
import json
import os
from time import sleep
from datetime import datetime
from multiprocessing import Pool, Manager

num = 5
addr_dict = {'kb_0': "192.168.90.237:8000/0",
             'kb_1': "192.168.90.237:8000/1",
             'kb_2': "192.168.90.237:8000/2",
             'kb_3': "192.168.90.237:8000/3",
             'kb_4': "192.168.90.237:8000/4"}
question = '你是谁'


def request_writer(q, index, kb_id, kb_version, addr, question):
    addr = 'http://' + addr
    print('进程%d向%s发送请求---开始 at %s' % (index, addr, datetime.now()))
    headers = {'Content-Type': 'application/json'}
    _data = {'kbid': kb_id, 'version': kb_version, 'question': question}
    data = json.dumps(_data)
    r = requests.post(addr, data=data, headers=headers)
    res = json.loads(r.text)
    print('进程%d向%s发送请求---完成 at %s, 响应数据为%s' % (index, addr, datetime.now(), res))
    q.put(res['data'])
    print('进程%d向queue写入数据---at %s, 写入数据为%s' % (index, datetime.now(), res))


def reader(q, num, answers):
    for i in range(0, num):
        try:
            msg = q.get()
            answers.append(msg)
        except Exception as e:
            print('%d ans wrong' % i)
            raise e
    if not q.empty():
        print('there is too many ans in queue')
        raise Exception('there is too many ans in queue')


def _multipath_request(num, addr_dict, question):
    print(" [%s] start" % os.getpid())
    po = Pool(num)
    q = Manager().Queue()
    answers = []
    kbs = list(addr_dict.keys())
    kb_vers_map = dict([(x, int(x[-1]) * 3) for x in kbs])
    print(kb_vers_map)
    for i in range(0, num):
        _kb_id = kbs[i]
        _addr = addr_dict[_kb_id]
        _kb_version = kb_vers_map[_kb_id]
        po.apply(request_writer, (q, i, _kb_id, _kb_version, _addr, question))

    reader(q, num, answers)
    # sleep(1)
    print(answers)
    po.close()
    po.join()
    return answers


if __name__ == '__main__':
    ret = _multipath_request(num, addr_dict, question)
    print(ret)
