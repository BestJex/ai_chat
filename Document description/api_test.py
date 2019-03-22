import requests
import json

# IP = "ceshi-v1.ntalker.com/chatbotbox"
# URL = "http://172.23.253.53:31992/api/v1"
# URL = "http://47.107.91.194:1835/api/v1"

# IP = "127.0.0.1"
# IP = "172.21.66.213"

# IP = "192.168.30.214"
# PORT = "8000"
# VERSION = "v1"
URL = "http://127.0.0.1:8088/api/v1"
KBID = "xnbert"
NAME = "bertdemo"
QUESTIONID = "lnn073108"
COMPANDID = "xnai"


def test_create_knowbase(url, kbid, name):
    url = url + "/knowbase/"
    payload = {"kbId": kbid, "name": name}

    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def test_create_qapairs(url, kbid, questionid):
    url = url + "/qapairs/"
    # url = "http://" + ip + "/api/" + version + "/qapairs/"

    payload = {
        "kbId": kbid,
        "questionId": questionid,
        "questions": [
            {
                "question": "沒有那海洋的寬闊"
            },
            {
                "question": "我只要熱情的撫摸"
            },
            {
                "question": "所謂不安全感是我"
            }
        ],
        "answer": "我沒有滿腔的熱火"
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def test_batch_create_qapairs(url):
    url = url + "/qapairs/" + "?batch=True"

    payload = {
        "kbId": "lnn072401",
        "qas": [
            {
                "questionId": "test_q2_by_lnn",
                "questions": [
                    {
                        "question": "你好123"
                    },
                    {
                        "question": "您好123"
                    },
                    {
                        "question": "nihao123"
                    }
                ],
                "answer": "bsfe4b25-3ddf0-4114-92bd-7c254d145d96"
            },
            {
                "questionId": "test_q3_by_lnn",
                "questions": [
                    {
                        "question": "在1"
                    },
                    {
                        "question": "在吗1"
                    },
                    {
                        "question": "zaima1"
                    }
                ],
                "answer": "bsfdsb25-3ddf0-3323-92fd-7c252dfsf97"
            }
        ]
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def update_qapairs(url, id):
    url = url + "/qapairs/" + id + "/"

    payload = {
        "kbId": "lnn071602",
        "questions": [
            {
                "question": "你好96"
            },
            {
                "question": "您好96"
            },
            {
                "question": "nihaonihao96"
            }
        ],
        "answer": "bsfe4b25-3ddf0-4114-92bd-7c254d145d39"
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("PUT", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def train_prepub(url, kbid, companyid):
    url = url + "/train/prepub/"

    payload = {
        "companyId": companyid,
        "kbIds": [{"kbId": kbid}]
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def train_inspect(url, kbid):
    url = url + "/train/inspect/"

    payload = {
        "kbIds": [{"kbId": kbid}]
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def online_test(url, kbid):
    url = url + "/train/online/"

    payload = {
        "kbIds": [{"kbId": kbid}]
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def train_status_test(url, kbid):
    url = url + "/train/status/"

    payload = {
        "kbIds": [{"kbId": kbid}]
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def qas_prepub_test(url, kbid, companyid):
    url = url + "/qas/prepub/"

    payload = {
        "companyId": companyid,
        "kbIds": [{"kbId": kbid}],
        "question": "有沒有的那样海洋的寬光",
        "top": 1
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def qas_formal_test(url, kbid, companyid):
    url = url + "/qas/formal/"
    payload = {
        "companyId": companyid,
        "kbIds": [{"kbId": kbid}],
        "question": "我只要熱情的撫摸",
        "top": 1
    }
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


def delete_knowbase(url, id):
    url = url + "/knowbase/" + id + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    print(response.text)


def delete_qa(url, id):
    url = url + "/qapairs/" + id + "/"
    headers = {
        'Content-Type': "application/json",
        'Accept-Charset': "utf-8",
    }
    response = requests.request("DELETE", url, headers=headers)
    print(response.text)


if __name__ == '__main__':
    # test_create_knowbase(URL, KBID, NAME)
    # test_create_qapairs(URL, KBID, QUESTIONID)
    # train_prepub(URL, KBID, COMPANDID)
    # train_inspect(URL, KBID)
    # online_test(URL, KBID)
    # train_status_test(URL, KBID)
    # qas_prepub_test(URL, KBID, COMPANDID) #false
    # qas_formal_test(URL, KBID, COMPANDID)
    test_batch_create_qapairs(URL)
    # update_qapairs(URL, QUESTIONID)
    # delete_qa(URL, 'test_q2_by_lnn')
    # delete_knowbase(URL, KBID)

payload = {
    "kbId": "xnbert",
    "qas": [
        {
            "questionId": "test_q1_by_lnn",
            "questions": [
                {
                    "question": "数据如何拷入公司"
                },
                {
                    "question": "拷出公司数据"
                },
                {
                    "question": "拷贝数据"
                },
                {
                    "question": "怎么拷数据啊"
                },
                {
                    "question": "如何在公司拷数据"
                },
                {
                    "question": "导入公司"
                },
                {
                    "question": "拷入资料"
                },
                {
                    "question": "拷出资料"
                },
                {
                    "question": "文件拷入公司"
                },
            ],
            "answer": "数据拷入或者拷出公司的政策"
        },
        {
            "questionId": "test_q2_by_lnn",
            "questions": [
                {
                    "question": "几个G大大文件怎么拷到公司内网啊"
                },
                {
                    "question": "很大的数据文件怎么拷到内网"
                },
                {
                    "question": "大数据文件如何拷入内网"
                },
                {
                    "question": "大文件怎么才能拷贝到公司的内网啊"
                },
                {
                    "question": "有一个大文件不知道怎么拷入公司的内网里面"
                },
                {
                    "question": "有哪些文件是可以拷入公司的啊"
                }
            ],
            "answer": "如何将大文件拷入公司内网？"
        },
        {
            "questionId": "test_q3_by_lnn",
            "questions": [
                {
                    "question": "能把本地的文件夹的内存扩大嘛"
                },
                {
                    "question": "能扩大本地的文件的存储空间吗"
                },
                {
                    "question": "怎么加大本地文件的内存空间"
                },
                {
                    "question": "怎么才能把本地文档的空间扩大"
                },
                {
                    "question": "本地的文件文档的空间太小，要扩大"
                },
                {
                    "question": "本地文件夹空间大一点"
                }
            ],
            "answer": "如何申请扩大本地文件夹"
        },
        {
            "questionId": "test_q4_by_lnn",
            "questions": [
                {
                    "question": "程序入口账号锁定"
                },
                {
                    "question": "我的电脑账号被锁了"
                },
                {
                    "question": "给我看一下，我的电脑程序入口好像是锁定了"
                },
                {
                    "question": "我的账号被锁定了，怎么办"
                },
                {
                    "question": "电脑账号锁定了怎么办"
                },
            ],
            "answer": "电脑账号被锁定"
        },
        {
            "questionId": "test_q5_by_lnn",
            "questions": [
                {
                    "question": "电脑的密码失效了"
                },
                {
                    "question": "账号密码失效过期"
                },
                {
                    "question": "我的账号密码过期显示失效了"
                },
                {
                    "question": "登录账号密码过期"
                },
                {
                    "question": "账号密码显示过期，现在没有办法登录"
                },
            ],
            "answer": "电脑密码过期"
        },
        {
            "questionId": "test_q6_by_lnn",
            "questions": [
                {
                    "question": "程序入口密码丢失"
                },
                {
                    "question": "忘记密码了"
                },
                {
                    "question": "我忘记我的程序入口密码了"
                },
                {
                    "question": "忘记我的电脑密码怎么办"
                },
                {
                    "question": "我忘记我的密码了"
                },
            ],
            "answer": "电脑密码忘记了"
        },

    ]
}
