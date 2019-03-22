# -*-coding: utf-8-*-

import json
import os
from time import sleep, time

import logging
# import pymongo
import pymysql
import requests
from multiprocessing import Manager, Process
from multiprocessing import Pool as prpo
from datetime import datetime
from django.shortcuts import render
from django.db.utils import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
#from django.shortcuts import render
from django.db.models import Max, Count
from django.core.cache import cache
from functools import reduce

from kazoo.exceptions import ConnectionClosedError
from pymongo import MongoClient
from rest_framework import status, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from app.kazoo_func import get_zk_nodes
from app.kazoo_simplify import query_request, query_request_z
from app.models import LexiconIndexes, Questions, KNOW_BASE, KnowGraphs, UNTRAINED, IN_TRAIN, TrainingMission, \
    TrainPubHistory, TRAIN, DONE, TRAIN_OK
from app.serializers import LexiconIndexesSerializers, QuestionsSerializers, KnowGraphsSerializers, TrainingMissionSerializers
from demo.settings import KG_MONGO, ZOOKEEPER, MANAGE_K, DATABASES
from DBUtils.PooledDB import PooledDB
# from lib.faitest import MyChatBot

err_log = logging.getLogger('error')
logger = logging.getLogger('all')
from pymongo import MongoClient


# mycbot = MyChatBot()


# 接收POST请求数据
def search_post(request):
    pass
    # ctx = {}
    # if request.POST:
    #     ctx['qus'] = '问题:\t'
    #     ctx['rlt'] = request.POST['q']
    #     ctx['ans'] = '答案:\t'
    #     each = mycbot.get_response(request.POST['q'])
    #     #        ctx['rps'] = JsonResponse({each.text: each.confidence})
    #     ctx['rps'] = each.text
    #     ctx['sim'] = '最相似问题:\t'
    #     ctx['sqm'] = str(mycbot.get_similar())
    #     ctx['cof'] = '置信度:\t'
    #     ctx['val'] = each.confidence
    # return render(request, "post.html", ctx)


@csrf_exempt
def get_qa(request):
    # data = request.POST
    # myclient = MongoClient('192.168.30.152', 27017)
    # dbname = data.get('know_base_id')
    # kg_version = data.get("kg_version")
    # if not dbname or not kg_version:
    #     return JsonResponse({"code": 400, "msg": 'know_base_id is needed'})
    # db = myclient["ai_%s_%s" %(dbname, kg_version)]
    # all_statements = db.get_collection("statements").find({},{"_id":0})
    # statements = []
    # for sta in all_statements:
    #     statements.append(sta.get("text"))
    # question = data.get("question", "")
    # if question:
    #     all_statements = db.get_collection("statements").find({}, {"_id": 0})
    #     question = db.get_collection("statements").find_one({"text": question})
    #     for sta in all_statements:
    #         if sta["in_response_to"]:
    #             if sta["in_response_to"][0]["text"] == question["text"]:
    #                 answer = sta["text"].split("@")[0]
    #                 ret = {"code": 200, "msg": 'OK', "answer": answer}
    #                 return JsonResponse(ret)
    # ret = {"code": 200, "msg": 'OK', "data": "ok"}
    # return JsonResponse(ret)
    pass


@csrf_exempt
def qa(request):
    return render(request, "qa.html")


@csrf_exempt
def qus_ans(request):
    """
    function: 正式Q&A
    :param request: question, 
                     kbids, 
                    company_id
    
    :return: code ,msg, data(包含：question ，questionId，answer，score ，kbId)
    """
    question = request.POST.get('question')
    kbids = request.POST.get('kbids')
    company_id = request.POST.get('company_id')

    # ret_ = mycbot.get_qus_ans(question, kbids, company_id)
    ret_ = [{
        "question": '你好',
        "questionId": 'jsdkkldf',
        "answer": "OK",
        "score": '1',
        "kbId": "SDSDDS"
    },
        {
            "question": '你坏',
            "questionId": 'jsdkkldf',
            "answer": "滚",
            "score": '1',
            "kbId": "SDSDDS"
        }]

    def func(each):
        item = {
            "question": each["question"],
            "questionId": each["questionId"],
            "answer": each["answer"],
            "score": each["score"],
            "kbId": each["kbId"],
        }

        return item

    data = list(map(func, ret_))

    ret = {"code": 200, "msg": 'OK', "data": data}
    return JsonResponse(ret)


@csrf_exempt
def test(request):
    """
    function: 多进程请求测试
    :param request: question, 
                    kb_id, 
                    kb_version

    :return: code ,msg, data(包含：question ，questionId，answer，score ，kbId)
    """
    question = request.POST.get('question')
    kbid = request.POST.get('kb_id')
    kb_version = request.POST.get('kb_version')

    ret_ = [{
        "question": question,
        "questionId": 'jsdkkldf',
        "answer": "OK",
        "score": "1",
        "kbId": kbid,
        "kb_version": kb_version
    }]
    logger.debug(ret_)

    def func(each):
        item = {
            "question": each["question"],
            "questionId": each["questionId"],
            "answer": each["answer"],
            "score": each["score"],
            "kbId": each["kbId"],
            "kb_version": each["kb_version"]
        }

        return item

    data = list(map(func, ret_))[0]

    ret = {"code": 0, "msg": 'OK', "data": data}
    err_log.error(data)
    return JsonResponse(ret)


class LexiconIndexesSet(ModelViewSet):
    queryset = LexiconIndexes.objects.all().order_by('-updated_at')
    serializer_class = LexiconIndexesSerializers

    @staticmethod
    def _create_v1(request, *args, **kwargs):
        start_time = time()
        data = {
            'id': request.data.get('kbId', ''),
            'lexicon_type': KNOW_BASE
        }
        if not data['id']:
            logger.info("传入参数错误, 请传入要创建的知识库id")
            return Response({"code": 1907, "msg": "参数错误"}, status=status.HTTP_200_OK)
        try:
            logger.info("开始创建知识库: ")
            logger.info(data)
            LexiconIndexes.objects.create(**data)
        except IntegrityError as e:
            if e.args[0] == 1062:
                logger.info("知识库ID重复")
                return Response({"code": 1901, "msg": "知识库ID重复"}, status=status.HTTP_200_OK)
            else:
                logger.info("创建知识库ID失败")
                return Response({"code": 500, "msg": "创建知识库ID失败"}, status=status.HTTP_200_OK)
        else:
            logger.info("创建知识库%s成功" % (data["id"], ))
            cache.set(str(data['id']), "0", timeout=1209600)
            logger.info('create Lexicon----time:%.5fs' % (time() - start_time))
            return Response({"code": 0, "msg": "创建成功"}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if request.version == 'v1':
            return self._create_v1(request, *args, **kwargs)
        else:
            pass

    def destroy(self, request, *args, **kwargs):
        start_time = time()
        if request.version == 'v1':
            std_id = kwargs['pk']
            logger.info("要删除的知识库id是: %s" % (std_id, ))
            try:
                LexiconIndexes.objects.all().filter(id__startswith=std_id).delete()
            except Exception as e:
                logger.info(e)
                ret = {'code': 1094,
                       'msg': "知识库删除失败"}
            else:
                ret = {'code': 0,
                       'msg': '删除成功'}
                cache.delete_pattern(str(std_id))
                # logger.debug("id status = %s" % cache.ttl(str(std_id)))
            logger.info("删除知识库成功")
            logger.info('destroy Lexicon----time:%.5fs' % (time() - start_time))
            return Response(ret, status=status.HTTP_200_OK)
        else:
            pass


class QuestionsSet(ModelViewSet):
    queryset = Questions.objects.all().order_by('-id')
    serializer_class = QuestionsSerializers

    @staticmethod
    def _format_qa(data, kb_id):
        qa_ins_list = []
        qa_info_list = []
        num = len(data['questions'])
        for i in range(0, num):
            if i:
                question_id = data['questionId'] + '_' + str(i)
                is_subordinate = 1
            else:  # 第0个为标准问题
                question_id = data['questionId']
                is_subordinate = 0

            qa_dict = {
                'id': question_id,
                'kb_id': kb_id,
                # 'standard_id':data['questionId'],
                'is_subordinate': is_subordinate,
                'content': data['questions'][i]['question'],
                'answer': data['answer']
            }
            qa_ins_list.append(Questions(**qa_dict))
            qa_info_list.append(qa_dict)

        return qa_ins_list, qa_info_list

    @staticmethod
    def _restrct_data(src):
        kb = src['kbId']
        LexiconIndexes.objects.get(id=kb)
        objs = []
        infos = []
        if 'qas' in src.keys():  # 批量
            qa_info = src['qas']
            for item in qa_info:
                _qa_objs, _qa_infos = QuestionsSet._format_qa(item, kb)
                objs.extend(_qa_objs)
                infos.extend(_qa_infos)

        else:  # 单个
            objs, infos = QuestionsSet._format_qa(src, kb)
        return objs, infos

    def create(self, request, *args, **kwargs):
        start_time = time()
        if request.version == 'v1':
            _data = request.data
            logger.info("创建问答对参数：")
            logger.info(_data)
            try:
                _objs, _infos = self._restrct_data(_data)
                items = Questions.objects.bulk_create(_objs)

                # map(lambda item: cache.set(str(item['id']), str(item['content']), timeout=None), _infos)
                # logger.debug("redis " + _infos)

            except IntegrityError as i:
                if i.args[0] == 1062:
                    if 'PRIMARY' in i.args[1]:
                        ret = {'code': 1902,
                               'msg': '问答对ID重复'}
                    logger.info("问答对ID重复")
            except KeyError:
                ret = {'code': 1907,
                       'msg': '参数错误'}
                logger.info("要创建问答对的参数错误")
            except LexiconIndexes.DoesNotExist:
                ret = {'code': 1903,
                       'msg': '知识库不存在'}
                logger.info("要创建问答对的知识库不存在")
            else:
                ret = {'code': 0,
                       'msg': '创建成功'}
                logger.info("创建问答对成功")
            finally:
                logger.info('create Questions----time:%.5fs' % (time() - start_time))
                return Response(ret, status=status.HTTP_200_OK)

        else:
            pass

    def update(self, request, *args, **kwargs):
        start_time = time()
        if request.version == 'v1':
            _data = request.data
            try:
                _data.update({'questionId': kwargs['pk']})
                _, _infos = self._restrct_data(_data)

                for item in _infos:
                    defaults = {"kb_id": item['kb_id'],
                                "content": item['content'],
                                "answer": item['answer'],
                                "is_subordinate": item['is_subordinate']}

                    Questions.objects.update_or_create(defaults=defaults, id=item['id'])

                    ## cache.set(str(item['id']), str(item['content']), timeout=1209600)

            except LexiconIndexes.DoesNotExist:
                ret = {'code': 1903,
                       'msg': '知识库不存在'}
            except KeyError:
                ret = {'code': 1907,
                       'msg': '参数错误'}
            else:
                ret = {'code': 0,
                       'msg': '更新成功'}
            finally:
                logger.info('update Questions----time:%.5fs' % (time() - start_time))
                return Response(ret, status=status.HTTP_200_OK)

        else:
            pass

    def destroy(self, request, *args, **kwargs):
        start_time = time()
        if request.version == 'v1':
            std_id = kwargs['pk']
            logger.info("删除问答对id: %s" % (std_id, ))
            try:
                Questions.objects.all().filter(id__startswith=std_id).delete()
            except Exception as e:
                logger.debug(e)
                ret = {'code': 1094,
                       'msg': "问答对删除失败"}
                logger.info("问答对%s删除失败" % (std_id, ))
            else:
                ret = {'code': 0,
                       'msg': '删除成功'}
                # cache.delete_pattern(str(std_id))
            logger.info("问答对%s删除成功" % (std_id,))
            logger.info('destroy Questions----time:%.5fs' % (time() - start_time))
            return Response(ret, status=status.HTTP_200_OK)
        else:
            pass


class TrainSet(ModelViewSet):
    queryset = KnowGraphs.objects.all().order_by('-updated_at')
    serializer_class = KnowGraphsSerializers
    filter_backends = (filters.SearchFilter,)
    search_fields = ('know_base__id', 'kg_version')

    @staticmethod
    def _conf_kg(kb_ver):
        kb_id, kg_version, com_id = kb_ver
        kg_version += 1
        kg_id = 'ai_' + kb_id + '_' + str(kg_version)
        cache.set("ai_%s" % kb_id, str(kg_version), timeout=1209600)
        ret = (
            KnowGraphs(know_base_id=kb_id, kg_version=kg_version, id=kg_id),
            TrainingMission(know_base_id=kb_id, kg_version=kg_version, company_id=com_id),
            TrainPubHistory(kb_id=kb_id, kg_id=kg_id, action=TRAIN)
        )
        return ret

    @staticmethod
    def _delete_mongo_kgs(del_list):
        client = MongoClient(KG_MONGO['HOST'], KG_MONGO['PORT'])
        for x in del_list:
            logger.debug('删除mongo库中%s---开始' % x)
            client.drop_database(x)
            logger.debug('删除mongo库中%s---完成' % x)
        client.close()

    @list_route(methods=['post'])
    def prepub(self, request):
        """
        logic:  
                1.查看训练任务表，请求中的知识库是否有未训练完成的版本；
                    若某知识库有未训练完成的版本，则对其的操作完成，其余知识库继续向下；
                2.创建KG对象，赋予其版本号 ；
                3.创建训练任务对象；
                4.更新发布历史记录表
                5.若某知识库版本数量超过10条，则保留最新的10条，删除MONGO中老版本及其在KG对应表中的记录
        param:      "kbIds": [
                                {"kbId": "b8aa4b25-7de0-4114-92bd-7c254d145d31"},
                                {"kbId": "b8aa4b25-7de0-4114-92bd-72223323d31"}],
                    "companyId": "25-7de0-4114-92bd-7"
        return :
                 "code": 0,
                 "msg": "发布成功"
        
        """
        ret = {}
        start_time = time()
        try:
            logger.info("训练知识库传入参数：")
            logger.info(request.data)
            kb_id_list = request.data['kbIds']
            comp_id = (request.data['companyId'], )
            logger.info('------需要训练的知识库：%s' % kb_id_list)
            kb_ids = [x['kbId'] for x in kb_id_list]
        except KeyError:
            ret = {'code': 1907, 'msg': "参数错误"}
            logger.info("训练知识库参数错误: ")
            logger.info(request.data)
            return Response(ret, status=status.HTTP_200_OK)

        kb_exist_list = list(LexiconIndexes.objects.all().filter(id__in=kb_ids).values_list('id', flat=True))
        absent_kbs = set(kb_ids) - set(kb_exist_list)
        if absent_kbs:
            logger.info('------知识库不存在, id是: ')
            logger.info(absent_kbs)
            ret = {'code': 1903, 'msg': "包含不存在的知识库"}
            return Response(ret, status=status.HTTP_200_OK)

        # 查看训练任务表，请求中的知识库是否有未训练完成的版本；
        # 筛选出已经训练完成得知识库，进行下一步
        kb_state_list = list(
            TrainingMission.objects.all().filter(know_base_id__in=kb_ids).values_list('know_base_id', 'status'))

        # logger.debug('------需要训练的知识库：%s' % kb_state_list)

        _kbs = list(filter(lambda x: x[1] == DONE, kb_state_list))
        kbs = [each[0] for each in _kbs]
        # 加上没有训练记录的知识库
        kbs_has_mission = [it[0] for it in kb_state_list]
        kbs_no_mission = set(kb_ids) - set(kbs_has_mission)
        kbs += kbs_no_mission
        # logger.debug('------需要训练的知识库：%s' % kbs)

        # 创建KG对象，赋予其版本号
        # 创建训练任务对象
        # 更新发布历史记录表；
        kb_vers_queryset = KnowGraphs.objects.all().filter(know_base_id__in=kbs). \
            values('know_base_id').annotate(lastest_version=Max('kg_version')). \
            values_list('know_base_id', 'lastest_version')
        kb_vers_map = list(kb_vers_queryset)
        kbs_has_kg = [item[0] for item in kb_vers_map]

        kbs_no_kg = filter(lambda it: it not in kbs_has_kg, kbs)
        kbs_vers_add = list(map(lambda x: (x, 0), kbs_no_kg))
        kb_vers_map.extend(kbs_vers_add)
        kb_vers_map1 = [x + comp_id for x in kb_vers_map]
        logger.debug(kb_vers_map1)

        kg_mission_objs = list(map(self._conf_kg, kb_vers_map1))
        kg_objs = [x[0] for x in kg_mission_objs]
        mission_objs = [x[1] for x in kg_mission_objs]
        history_objs = [x[2] for x in kg_mission_objs]

        logger.info('*' * 20)
        logger.info('创建kg对象---开始')
        logger.info(kg_objs)
        KnowGraphs.objects.bulk_create(kg_objs)
        logger.info('创建kg对象---完成')

        logger.info('*' * 20)
        logger.info('创建训练任务对象---开始')
        logger.info(mission_objs)
        TrainingMission.objects.bulk_create(mission_objs)
        logger.info('创建训练任务对象---完成')

        logger.info('*' * 20)
        logger.info('创建训练历史记录---开始')
        logger.info(history_objs)
        TrainPubHistory.objects.bulk_create(history_objs)
        logger.info('创建训练历史记录---完成')

        # 若某知识库版本数量超过10条，则保留最新的10条，删除MONGO中老版本及其在KG对应表中的记录
        kg_num_queryset = KnowGraphs.objects.all().filter(know_base_id__in=kbs).values('know_base_id'). \
            annotate(kg_num=Count('id')).values_list('know_base_id', 'kg_num')
        _kg_num_list = list(kg_num_queryset)

        kg_num_list = list(filter(lambda x: x[1] > 10, _kg_num_list))
        kb_list = [x[0] for x in kg_num_list]  # 需用来过滤的kb列表
        kg_del_list = []

        if kg_num_list:
            temp_kg_list = list(KnowGraphs.objects.all().filter(know_base_id__in=kb_list).order_by('-kg_version'). \
                                values_list('know_base_id', 'id'))
            temp_dict = {}
            for kb, kg in temp_kg_list:
                temp_dict.setdefault(kb, [])
                temp_dict[kb].append(kg)

            for kb, kg_list in temp_dict.items():
                kg_del_list.extend(kg_list[10:])

            # logger.debug('------改变训练任务表中冗余KB的状态---')
            # 去MONGO库删除需删除的kg
            logger.info('------Mongo库中删除冗余KG---开始 at %s' % datetime.now())
            self._delete_mongo_kgs(kg_del_list)
            logger.info('------Mongo库中删除冗余KG---结束 at %s' % datetime.now())

            # 删除kg表中多余记录
            KnowGraphs.objects.all().filter(id__in=kg_del_list).delete()
            # update the is_delete of training sheet
            map(lambda x: TrainingMission.objects.all().filter(know_base_id__in=x.split('_')[1], kg_version=x.split('_')[-1], is_delete=0).update(is_delete=1), kg_del_list)
        logger.info('prepub ------------------time:%.5fs' % (time() - start_time))
        logger.info("训练知识库成功")
        ret = {'code': 0, 'msg': '训练成功'}
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def online(self, request):
        """
        logic: 更改KG对应关系表中发布状态，将最新版本标1
        param :"kbIds": [
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-7c254d145d31"
                        },
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-72223323d31"
                        }
                    ]
        return: {
                    "code": 0,
                    "msg": "发布成功"
                }
        """
        start_time = time()
        try:
            kb_ids = request.data['kbIds']
            logger.info("online 参数：")
            logger.info(kb_ids)
            kb_ids = [x['kbId'] for x in kb_ids]
        except KeyError:
            logger.info("online参数错误")
            return Response({'code': 1907, 'msg': '参数错误'}, status=status.HTTP_200_OK)

        last_vers_state = list(
            KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values('know_base_id').annotate(
                last_vers=Max('kg_version')).values_list('know_base_id', 'last_vers'))
        kb_has_vers = list(map(lambda x: x[0], last_vers_state))
        kb_no_vers = set(kb_ids) - set(kb_has_vers)
        if kb_no_vers:
            msg = '知识库%s没有训练完成kg版本' % kb_no_vers
            logger.info(msg)
            return Response({'code': 1905, 'msg': msg}, status=status.HTTP_200_OK)
        # 将次新的版本 in_use置为0
        KnowGraphs.objects.all().filter(know_base_id__in=kb_ids, in_use=1).update(in_use=0)

        # map(lambda x: cache.delete_pattern("inuse_%s" % str(x)), kb_ids)
        # map(lambda x:logger.debug(str(x)), kb_ids)

        # 将最新的版本 in_use置为1
        kg_ids_new = list(map(lambda x: 'ai_' + x[0] + '_' + str(x[1]), last_vers_state))
        KnowGraphs.objects.all().filter(id__in=kg_ids_new).update(in_use=1)

        # map(lambda x: cache.set("inuse_%s" % str(x[0]), str(x[1]), timeout=1209600), last_vers_state)
        for x in last_vers_state:
            cache.set("inuse_%s" % str(x[0]), str(x[1]), timeout=1209600)
        logger.info("online（发布）成功")
        logger.info('online ----------------time:%.5fs' % (time() - start_time))
        return Response({'code': 0, 'msg': '发布成功'}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def inspect(self, request):
        """
        logic: 训练（预发布)状态检测：检查指定知识库最新KG的训练状态：全为2，则返回2；全为0，则返回0；其余为1
        param: 
                    "kbIds": [
                                {
                                    "kbId": "b8aa4b25-7de0-4114-92bd-7c254d145d31"
                                },
                                {
                                    "kbId": "b8aa4b25-7de0-4114-92bd-72223323d31"
                                }
                            ]  
                
        return: "code": 0,
                "msg": "",
                "data": [
                    {
                        "status": "1"
                    }
                ]
        """
        start_time = time()
        try:
            logger.info("inspect 参数：")
            kb_ids = request.data['kbIds']
            logger.info(kb_ids)
            kb_ids = [x['kbId'] for x in kb_ids]
        except KeyError:
            logger.info("inspect 参数错误")
            return Response({'code': 1907, 'msg': '参数错误'}, status=status.HTTP_200_OK)

        last_vers_state = list(
            KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values('know_base_id').annotate(
                last_vers=Max('kg_version')).values_list('know_base_id', 'last_vers'))
        kb_has_vers = list(map(lambda x: x[0], last_vers_state))
        kb_no_vers = set(kb_ids) - set(kb_has_vers)
        if kb_no_vers:
            msg = '知识库%s没有训练完成的kg版本' % kb_no_vers
            logger.info(msg)
            return Response({'code': 1905, 'msg': msg}, status=status.HTTP_200_OK)

        # map(lambda x: cache.delete_pattern("ai_%s" % str(x)), kb_ids)

        last_kg_ids = list(map(lambda x: 'ai_' + x[0] + '_' + str(x[1]), last_vers_state))
        last_kg_states = KnowGraphs.objects.all().filter(id__in=last_kg_ids).values_list('train_state', flat=True)

        # map(lambda x: cache.set("ai_%s" % str(x[0]), str(x[1]), timeout=1209600), last_vers_state)
        for x in last_vers_state:
            cache.set("inuse_%s" % str(x[0]), str(x[1]), timeout=1209600)

        states = set(last_kg_states)
        _status = IN_TRAIN
        if len(states) == 1:
            # 如果全都为未训练
            if states == {UNTRAINED}:
                _status = UNTRAINED
            elif states == {TRAIN_OK}:
                _status = TRAIN_OK
        data = {'status': _status}
        logger.info("inspect 成功")
        logger.info('inspect -------------time:%.5fs' % (time() - start_time))
        return Response({'code': 0, 'msg': '操作成功', 'data': data}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def status(self, request):
        """
        logic: 发布状态检测：检查指定知识库最新版本的发布状态是否为1

        param:  "kbIds": [
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-7c254d145d31"
                        },
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-72223323d31"
                        }
                    ]
        return: "code": 0,
                "msg": "",
                "data": [
                    {
                        "status": "1"
                    }
                ]
        """
        start_time = time()
        try:
            logger.info("status 参数：")
            kb_ids = request.data['kbIds']
            logger.info(kb_ids)
            kb_ids = [x['kbId'] for x in kb_ids]
        except KeyError:
            logger("status参数错误")
            return Response({'code': 1907, 'msg': '参数错误'}, status=status.HTTP_200_OK)
        last_vers_use = list(
            KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values('know_base_id').annotate(
                last_vers=Max('kg_version')).values_list('know_base_id', 'last_vers'))
        kb_has_vers = list(map(lambda x: x[0], last_vers_use))
        kb_no_vers = set(kb_ids) - set(kb_has_vers)
        if kb_no_vers:
            msg = '知识库%s没有训练完成的kg版本' % kb_no_vers
            logger.info(msg)
            return Response({'code': 1905, 'msg': msg}, status=status.HTTP_200_OK)

        # map(lambda x: cache.delete_pattern("inuse_%s" % str(x)), kb_ids)
        # map(lambda x: logger.debug(str(x)), kb_ids)

        last_kg_ids = list(map(lambda x: 'ai_' + x[0] + '_' + str(x[1]), last_vers_use))
        last_kg_use = KnowGraphs.objects.all().filter(id__in=last_kg_ids).values_list('in_use', flat=True)


        # for x in last_vers_use:
            # cache.set("inuse_%s" % str(x[0]), str(x[1]), timeout=1209600)

        uses = set(last_kg_use)
        _status = 0
        if len(uses) == 1 and uses == {1}:
            _status = 1

        data = {'status': _status}
        logger.info("status 成功")
        logger.info('status -------------time:%.5fs' % (time() - start_time))
        return Response({'code': 0, 'msg': '操作成功', 'data': data}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def inipub(self, request):
        """
        logic: 发布状态检测：检查指定知识库最新版本的发布状态是否为1

        param:  "kbIds": [
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-7c254d145d31"
                        },
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-72223323d31"
                        }
                    ]
        return: "code": 0,
                "msg": "",
        """
        try:
            kb_ids = request.data['kbIds']
            kb_ids = [x['kbId'] for x in kb_ids]
        except KeyError:
            return Response({'code': 1907, 'msg': '参数错误'}, status=status.HTTP_200_OK)
        last_vers_use = list(
            KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values('know_base_id').annotate(
                last_vers=Max('kg_version')).values_list('know_base_id', 'last_vers'))
        kb_has_vers = list(map(lambda x: x[0], last_vers_use))
        kb_no_vers = set(kb_ids) - set(kb_has_vers)
        if kb_no_vers:
            msg = '知识库%s没有训练完成的kg版本' % kb_no_vers
            return Response({'code': 1905, 'msg': msg}, status=status.HTTP_200_OK)

        # 将最新版本的知识图的训练状态改为 0:未训练
        for kb_id, last_version in last_vers_use:
            KnowGraphs.objects.all().filter(know_base_id=kb_id, kg_version=last_version).update(train_state=0)
            TrainingMission.objects.all().filter(know_base_id=kb_id, kg_version=last_version).update(status=0)
        return Response({'code': 0, 'msg': 'test'}, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def delete_kb(self, request):
        """
        logic: 发布状态检测：检查指定知识库最新版本的发布状态是否为1

        param:  "kbIds": [
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-7c254d145d31"
                        },
                        {
                            "kbId": "b8aa4b25-7de0-4114-92bd-72223323d31"
                        }
                    ]
        return: "code": 0,
                "msg": "",
        """
        try:
            kb_ids = request.data['kbIds']
            kb_ids = [x['kbId'] for x in kb_ids]
        except KeyError:
            return Response({'code': 1907, 'msg': '参数错误'}, status=status.HTTP_200_OK)
        last_vers_use = list(
            KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values('know_base_id').annotate(
                last_vers=Max('kg_version')).values_list('know_base_id', 'last_vers'))
        kb_has_vers = list(map(lambda x: x[0], last_vers_use))
        kb_no_vers = set(kb_ids) - set(kb_has_vers)
        if kb_no_vers:
            msg = '知识库%s没有训练完成的kg版本' % kb_no_vers
            return Response({'code': 1905, 'msg': msg}, status=status.HTTP_200_OK)
        # 刪除訓練任務
        TrainingMission.objects.all().filter(know_base_id__in=kb_ids).phys_delete()
        # 刪除歷史記錄
        TrainPubHistory.objects.all().filter(kb_id__in=kb_ids).delete()
        # 删除monogodb 数据库
        del_kg_list = list(KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values_list('id'))
        # logger.debug('------改变训练任务表中冗余KB的状态---')
        # 去MONGO库删除需删除的kg
        logger.debug('------Mongo库中删除冗余KG---开始 at %s' % datetime.now())
        self._delete_mongo_kgs(del_kg_list)
        logger.debug('------Mongo库中删除冗余KG---结束 at %s' % datetime.now())
        # 删除知识图
        KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).delete()
        # 删除问题库
        Questions.objects.all().filter(kb_id__in=kb_ids).phys_delete()
        # 删除知识库
        LexiconIndexes.objects.all().filter(id__in=kb_ids).phys_delete()


class QasSet(ModelViewSet):
    queryset = KnowGraphs.objects.all()
    # conn = None
    #cursor = None
    db_config = {
        "host": DATABASES['default']['HOST'],
        "port": DATABASES['default']['PORT'],
        "user": DATABASES['default']['USER'],
        "passwd": DATABASES['default']['PASSWORD'],
        "db": DATABASES['default']['NAME'],
        "charset": "utf8"
    }

    pool = PooledDB(pymysql, 5, **db_config)

    # @staticmethod
    # def initmysqlconnect():
    # QasSet.cursor = QasSet.conn.cursor()

    # 向底层发起请求，并将返回结果写入队列
    def _writer(que, index, kb_id, kb_version, addr, issue):
        addr = 'http://' + addr
        logger.info('进程%d向%s发送请求---开始' % (index, addr))
        headers = {'Content_Type': 'application/json'}
        _data = {'kbid': kb_id, 'version': str(kb_version), 'question': issue}
        data = json.dumps(_data)
        res = requests.post(addr, data=data, headers=headers)
        if res.status_code == 500:
            logger.info('addr %s Response 500 ' % addr)

        else:
            _ret = json.loads(res.text)
            ret, code = _ret['data'], _ret['code']
            ret['kbId'] = kb_id
            # logger.debug('进程%d向%s发送请求---完成, 响应数据为%s' % (index, addr, ret))
            if code == 0:
                que.put(ret)
                logger.info('进程%d向%s发送请求成功，向queue写入数据:%s' % (index, addr, ret))
            elif code == 1 and 'score' in ret.keys() and ret['score'] == 0:
                que.put({'not_match': kb_id})
                logger.info('进程%d向%s发送请求未匹配到答案, 知识库为%s, 问题为%s' % (index, addr, kb_id, issue))
            else:
                que.put({'fail': kb_id})
                logger.info('进程%d向%s发送请求失败, 知识库为%s, 问题为%s, 问答结果为:%s ' % (index, addr, kb_id, issue, ret))

    # 从队列中读取消息，并写入结果列表
    def _read(que, count, ans, not_match, fail):
        i = 0
        while not que.empty():
            msg = que.get()
            if 'not_match' in msg.keys():
                not_match.append(msg['not_match'])
            elif 'fail' in msg.keys():
                fail.append(msg['fail'])
            else:
                ans.append(msg)
            logger.debug('%dmsg:' % i, msg)
            i += 1
        logger.info('get answers finished')

    @staticmethod
    def _multipath_request(num, addr_dict, kb_vers_map, question):

        logger.debug("multipath_request QA start")

        po = prpo(num)
        q = Manager().Queue()

        kbs = list(addr_dict.keys())
        for i in range(0, num):
            _kb = kbs[i]
            _version = kb_vers_map[_kb]
            _addr = addr_dict[_kb]
            po.apply(QasSet._writer, (q, i, _kb, _version, _addr, question))
        po.close()
        po.join()

        not_match = []  # 匹配不到请求中问题的知识库
        fail = []  # 底层响应code为1的知识库
        answers = []
        i = 0
        while not q.empty():
            msg = q.get()
            if 'not_match' in msg.keys():
                not_match.append(msg['not_match'])
            elif 'fail' in msg.keys():
                fail.append(msg['fail'])
            else:
                answers.append(msg)
            logger.debug('%d msg:%s' % (i, msg))
            i += 1
        logger.debug('get answers finished')
        logger.debug("multipath_request QA end")
        return answers, not_match, fail

    @list_route(methods=['post'])
    def prepub(self, request, *args, **kwargs):
        if request.version == 'v1':
            return self._prepub_v1(request)

    @list_route(methods=['post'])
    def formal(self, request, *args, **kwargs):
        if request.version == 'v1':
            return self._formal_v1(request)

    # @staticmethod
    # def close_mysql(conn, cursor):
    #     QasSet.conn.commit()
    #     #QasSet.cursor.close()
    #     QasSet.conn.close()

    def _qa_base_v1_optimize(self, request, formal):
        """
        logic: 1.查询KG对应关系表，请求中是否包含未被训练过的KB;
                    若是，则返回QA错误
               2.去zk中查找target为KB的节点，
               3.若找到，则向该节点的地址发送请求；
                    未找到，则寻找空闲节点，为其指定KB，取其地址，向改地址发送请求；
       
        """
        # 取请求中 question
        start_query_kbs = time()
        logger.info('start qa_base ---time:%.5f ' % (time() - start_query_kbs))
        try:
            logger.info("qa 问题：")
            question = request.data['question']
            logger.info(question)
            top = int(request.data.get('top', 3))

            # 取请求中KB
            li = request.data['kbIds']
            li = [x['kbId'] for x in li]
            logger.info("知识库id: ")
            logger.info(li)
            cp_id = request.data['companyId']
            logger.info("company id is %s" % (cp_id, ))
        except KeyError:
            logger.info("参数错误")
            ret = {'code': 1907, 'msg': "参数错误"}
            return Response(ret, status=status.HTTP_200_OK)
        if not li:
            ret = {'code': 1907, 'msg': "参数错误"}
            return Response(ret, status=status.HTTP_200_OK)
        # 若请求中包含不存在的知识库直接返回
        logger.debug('end 1st check ---time:%.5f ' % (time() - start_query_kbs))
        kbs_exist = 0
        for y in li:
            if cache.ttl(str(y)) == 0:
                logger.debug('enter redis for all kb id --time: %.5f' % (time()-start_query_kbs))
                sql_1 = "select id from app_lexiconindexes where app_lexiconindexes.is_delete = False"
                conn = QasSet.pool.connection()
                cur = conn.cursor()
                cur.execute(sql_1)
                qs_content = cur.fetchall()
                cur.close()
                conn.close()
                for key in qs_content:
                    cache.set(str(key[0]), "0", timeout=1209600)
                if cache.ttl(str(y)) == 0:
                    break
                #pass
            # else:
            kbs_exist = kbs_exist + 1

        logger.info('end 2nd check ---time:%.5f ' % (time() - start_query_kbs))
        if len(li) > kbs_exist:
            # cursor.close()
            logger.info('------error:no kbs ---time:%.5f ' % (time() - start_query_kbs))
            logger.info("请求中包含不存在的知识库")
            return Response({'code': 1903, 'msg': '请求中包含不存在的知识库'}, status=status.HTTP_200_OK)
        logger.info('------query kbs ---time:%.5f ' % (time() - start_query_kbs))

        """
        1.查询请求中的各知识库，是否有符合需求的知识图版本；
        """
        start_query_vers = time()

        if not formal:  # 预发布QA
            # 查询请求中的知识库有没有已训练完成的kg版本
            for y in li:
                if cache.ttl("ai_"+str(y)) == 0:
                    sql_2 = "select know_base_id, MAX(kg_version) as last_vers from app_knowgraphs where train_state = 2 group by know_base_id"
                    conn = QasSet.pool.connection()
                    cur = conn.cursor()
                    cur.execute(sql_2)
                    kb_vers = cur.fetchall()
                    cur.close()
                    conn.close()
                    ##logger.debug(kb_vers)
                    kb_content = dict(kb_vers)
                    for key, value in kb_content.items():
                       cache.set("ai_%s" % str(key), str(value), timeout=1209600)
                    break
            kb_vers_list =[(str(y), cache.get("ai_"+str(y))) for y in li]
            kbs_has_vers = [x[0] for x in kb_vers_list]
        else:  # 正式QA
            # 查询请求中的知识库有没有使用中的kg版本
            for y in li:
                if cache.ttl("inuse_" + str(y)) == 0:
                    sql_3 = "select know_base_id, kg_version from app_knowgraphs where in_use = True"
                    conn = QasSet.pool.connection()
                    cur = conn.cursor()
                    cur.execute(sql_3)
                    kb_vers = cur.fetchall()
                    cur.close()
                    conn.close()
                    #logger.debug(kb_vers)
                    kb_content = dict(kb_vers)
                    for key, value in kb_content.items():
                       cache.set("inuse_%s" % str(key), str(value), timeout=1209600)
                    break
            kb_vers_list = [(str(y), cache.get("inuse_" + str(y))) for y in li]
            kbs_has_vers = [x[0] for x in kb_vers_list]

        if set(li) != set(kbs_has_vers):
            if not formal:
                msg = '知识库%s没有训练完成kg版本' % (set(li) - set(kbs_has_vers))
                logger.info(msg)
            else:
                msg = '知识库%s没有使用中kg版本' % (set(li) - set(kbs_has_vers))
                logger.info(msg)
            # cursor.close()
            ret = {'code': 1905, 'msg': msg}
            return Response(ret, status=status.HTTP_200_OK)
        logger.info('------query version ---time:%.5f ' % (time() - start_query_vers))

        """
        2.去zk中取请求地址,并向底层发送请求
        """
        start_query_ques = time()

        kb_vers_map = dict(kb_vers_list)
        res_data = []
        try:
            res_data = query_request_z(li, question, kb_vers_map, cp_id)
        except Exception as e:
            if e.args[0] == 1910:
                ret = {'code': 1910, 'msg': 'zk连接失败'}
                logger.info("zk连接失败")
                return Response(ret, status=status.HTTP_200_OK)
        except ConnectionClosedError as c:
            err_log.error(c)
            logger.info("zk连接失败")
            ret = {'code': 1910, 'msg': 'zk连接失败'}
            return Response(ret, status=status.HTTP_200_OK)

        #logger.debug('res_data = %s' % res_data)
        logger.debug('------query question ---time:%.5f ' % (time() - start_query_ques))
        """
        3.解析底层返回的结果，汇总为返回给上层的data
        """

        start_combine = time()
        _data_before = sorted(res_data['ans'], key=lambda x: -x['score'])
        # question_ids = [x['questionid'] for x in _data_before]
        # qs_content = {}
        # for y in question_ids:
        #     if cache.ttl(str(y)) == 0:
        #         sql_4 = "select id, content from app_questions where is_delete=False"
        #         QasSet.cursor.execute(sql_4)
        #         qs_content = dict(QasSet.cursor.fetchall())
        #         # QasSet.cursor.close()
        #         for key, value in qs_content.items():
        #            cache.set(str(key), str(value), timeout=None)
        #         break
        #         # pass
        #     else:
        #         qs_content[str(y)] = cache.get(str(y))


        def func(each):
            if '_' in each['questionid']:
                each['questionId'] = each['questionid'].split('_')[0]
            else:
                each['questionId'] = each['questionid']
            # each['question'] = qs_content[each['questionid']]

            del each['questionid']
            return each

        _data = list(map(func, _data_before))

        ret = {'code': 0, 'msg': '操作成功', 'data': _data[0:top],
               'no_ans_kbs': {'no_box': res_data['no_box'], 'not_match': res_data['not_match'],
                              'fail': res_data['fail']}}
        # cursor.close()
        # p.join()
        #logger.debug('p.join')

        # logger.debug("QA结果:%s" % ret)
        logger.info("qa 成功")
        logger.debug('combind answers----time:%.5f' % (time() - start_combine))

        return Response(ret, status=status.HTTP_200_OK)

    def _qa_base_v1(self, request, formal):
        """
        logic: 1.查询KG对应关系表，请求中是否包含未被训练过的KB;
                    若是，则返回QA错误
               2.去zk中查找target为KB的节点，
               3.若找到，则向该节点的地址发送请求；
                    未找到，则寻找空闲节点，为其指定KB，取其地址，向改地址发送请求；

        """
        # 取请求中 question
        try:
            question = request.data['question']
            top = int(request.data.get('top', 3))

            # 取请求中KB
            li = request.data['kbIds']
            li = [x['kbId'] for x in li]
        except KeyError:
            logger.info("qa参数错误")
            ret = {'code': 1907, 'msg': "参数错误"}
            return Response(ret, status=status.HTTP_200_OK)

        # 若请求中包含不存在的知识库直接返回
        kbs_exist = LexiconIndexes.objects.all().filter(id__in=li).values_list('id', flat=True)
        if set(li) != set(kbs_exist):
            return Response({'code': 1903, 'msg': '请求中包含不存在的知识库'}, status=status.HTTP_200_OK)

        """
        1.查询请求中的各知识库，是否有符合需求的知识图版本；
        """

        if not formal:  # 预发布QA
            # 查询请求中的知识库有没有已训练完成的kg版本
            kb_vers_queryset = KnowGraphs.objects.all(). \
                filter(know_base_id__in=li, train_state=TRAIN_OK). \
                values('know_base_id').annotate(last_vers=Max('kg_version')). \
                values_list('know_base_id', 'last_vers')
            kb_vers_list = list(kb_vers_queryset)
            kbs_has_vers = [x[0] for x in kb_vers_list]
        else:  # 正式QA
            # 查询请求中的知识库有没有使用中的kg版本
            kb_vers_queryset = KnowGraphs.objects.all().filter(know_base_id__in=li, in_use=True). \
                values_list('know_base_id', 'kg_version')
            kb_vers_list = list(kb_vers_queryset)
            kbs_has_vers = [x[0] for x in kb_vers_list]

        if set(li) != set(kbs_has_vers):
            if not formal:
                msg = '知识库%s没有训练完成kg版本' % (set(li) - set(kbs_has_vers))
                logger.info(msg)
            else:
                msg = '知识库%s没有使用中kg版本' % (set(li) - set(kbs_has_vers))
                logger.info(msg)
            ret = {'code': 1905, 'msg': msg}
            return Response(ret, status=status.HTTP_200_OK)

        """
        2.去zk中取请求地址
        """
        logger.debug('start query  Target in zk')
        try:
            addr_list = get_zk_nodes(li)
        except ConnectionClosedError as c:
            err_log.error(c)
            logger.info("zk连接失败")
            ret = {'code': 1910, 'msg': 'zk连接失败'}
            return Response(ret, status=status.HTTP_200_OK)
        except Exception as e:
            if e.args[0] == 1910:
                logger.info("zk连接失败")
                ret = {'code': 1910, 'msg': 'zk连接失败'}
                return Response(ret, status=status.HTTP_200_OK)
        else:
            logger.debug('end query  Target in zk')

        # 取各知识库对应的版本
        full = reduce(lambda x, y: x + y['full'], addr_list, [])
        not_full = reduce(lambda x, y: x + y['not_full'], addr_list, [])
        kb_vers_list = filter(lambda x: (x[0] not in full) and (x[0] not in not_full), kb_vers_list)
        kb_vers_dict = dict(kb_vers_list)
        kb_num = len(kb_vers_dict)
        address_dict = dict(reduce(lambda x, y: x + list(y['address'].items()), addr_list, []))
        logger.debug('"address_dict": %s, "kb_num": %d' % (address_dict, kb_num))
        if not address_dict:
            ret = {'code': 1906, 'msg': 'zk无空闲box'}
            logger.info("zk无空闲box")
            return Response(ret, status=status.HTTP_200_OK)

        """
        3.用多进程分别向多个地址发送请求
        """

        ans_list, not_match, fail = self._multipath_request(kb_num, address_dict, kb_vers_dict, question)

        """
        4.解析底层返回的结果，汇总为返回给上层的data
        """
        if not ans_list:
            ret = {'code': 1908, 'msg': '向底层请求无应答'}
            logger.info(ret)
        _data_before = sorted(ans_list, key=lambda x: -x['score'])
        question_ids = [x['questionid'] for x in _data_before]

        qs_content = dict(Questions.objects.all().filter(id__in=question_ids).values_list('id', 'content'))

        def func(each):
            if '_' in each['questionid']:
                each['questionId'] = each['questionid'].split('_')[0]
            else:
                each['questionId'] = each['questionid']
            each['question'] = qs_content[each['questionid']]

            del each['questionid']
            return each

        _data = list(map(func, _data_before))
        logger.info("qa操作成功")
        ret = {'code': 0, 'msg': '操作成功', 'data': _data[0:top],
               'no_ans_kbs': {'full': full, 'not_full': not_full, 'not_match': not_match, 'fail': fail}}
        logger.debug("QA结果:%s" % ret)

        return Response(ret, status=status.HTTP_200_OK)

    def _prepub_v1(self, request):
        start_time = time()
        if MANAGE_K:
            ret = self._qa_base_v1(request, False)
        else:
            ret = self._qa_base_v1_optimize(request, False)
        logger.debug('prepub all-------------time:%.5fs' % (time() - start_time))
        return ret

    def _formal_v1(self, request):
        start_time = time()
        if MANAGE_K:
            ret = self._qa_base_v1(request, True)
        else:
            ret = self._qa_base_v1_optimize(request, True)
        logger.debug('formal all-------------time:%.5fs' % (time() - start_time))
        return ret


class TrainMissionSet(ModelViewSet):
    queryset = TrainingMission.objects.all().order_by('-updated_at')
    serializer_class = TrainingMissionSerializers
    filter_backends = (filters.SearchFilter,)
    search_fields = ('know_base__id',)
