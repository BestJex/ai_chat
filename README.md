AI_CHAT：
1.知识库逻辑：class LexiconIndexesSet(ModelViewSet)
	新建知识库并存到redis：
		Request:
			url = url+"/knowbase/"
			data = {"kbId": kbid, "name": name}
		Deal:
			LexiconIndexes.objects.create(**data)
			cache.set(str(data['id']), "0", timeout=1209600)
	删除知识库:
		Request:
			url = url + "/knowbase/" + id + "/"
		Deal:
			LexiconIndexes.objects.all().filter(id__startswith=std_id).delete()
			cache.delete_pattern(str(std_id))
2.问答对逻辑：class QuestionsSet(ModelViewSet)
	新建单个问答对：
		Request:
			url = url + "/qapairs/"
			data = {
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
	批量创建问答对：
		Request:
			url = url + "/qapairs/" + "?batch=True"
			data = {
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
		
		Deal:
			1.验证知识库是否存在  LexiconIndexes.objects.get(id=kb)
			2.循环问题列表，将第一个问题作为标准问题id为questionId,其他问题的id使用questionId + '_' + str(i)拼接
			3.objs中存放问答对处理后的对象，用于批量创建 
			  infos存放问答对的dict格式,用于更新操作
				objs = [Questions(**qa_dict)]  infos = [qa_dict]
				Questions.objects.bulk_create(_objs)
				
	更新问答对：
		Request:
			url = url + "/qapairs/" + id + "/"
			data= {
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
		
		Deal:
			1.将问题id更新到data中 request.data.update({'questionId': kwargs['pk']})
			2.对每个问题处理后得到infos
			3.循环infos中的每个问题对象那个,更新对应问题id的数据
				Questions.objects.update_or_create(defaults=defaults, id=item['id'])
				
	删除问答对:
		Request:
			 url = url + "/qapairs/" + id + "/"
			 
		Deal：
			 Questions.objects.all().filter(id__startswith=std_id).delete()

3.知识库训练与发布：class TrainSet(ModelViewSet)
    1.知识库训练：
        Request:
            url = url + "/train/prepub/"
            data = {
                "companyId": companyid,
                "kbIds": [{"kbId": kbid}]
                }
        Deal：
            1.校验传入的知识库是否都存在,若有知识库不存在，不再继续执行
                kb_exist_list = list(LexiconIndexes.objects.all().filter(id__in=kb_ids).values_list('id'))
                absent_kbs = set(kb_ids) - set(kb_exist_list)
            2.找到需要训练的知识库
              查看训练任务表，请求中的知识库是否有未训练完成的版本；任务表中知识库的状态 0:未开始 1:已指派 2：已完成 3：正在执行中
              需要训练的知识库：无训练记录的知识库 + 训练完成的知识库
              1.有训练记录的知识库：
                  kb_state_list = list(
                    TrainingMission.objects.all().filter(know_base_id__in=kb_ids).values_list('know_base_id', 'status')
                   _kbs = list(filter(lambda x: x[1] == 2, kb_state_list))

                   kbs_has_mission = [it[0] for it in kb_state_list]
              2.找出无训练记录的知识库：
                kbs_no_mission = set(kb_ids) - set(kbs_has_mission)
              3.训练记录中已训练完成的知识库：
                   _kbs = list(filter(lambda x: x[1] == 2, kb_state_list))
                    kbs = [each[0] for each in _kbs]
              4.需要训练的知识库： kbs += kbs_no_mission
            3.对待训练的知识库创建KG对象，赋予其版本号，并添加到任务表和历史表中
              KG的训练状态： 0:未训练 1:训练中 2：训练完成（训练完成）
                  是否使用中 0：否（未使用）1：使用中
              对知识库每训练一次,KG中对应该知识库的版本号就会自增1。
              1.从待训练的知识库中取出已有KG记录的知识库对应的最大版本号
                  kb_vers_map = list(KnowGraphs.objects.all().filter(know_base_id__in=kbs). \
                    values('know_base_id').annotate(lastest_version=Max('kg_version')). \
                    values_list('know_base_id', 'lastest_version'))
              2.从待训练的知识库中获得无KG记录的知识库,将其版本号赋予0
                   kbs_has_kg = [item[0] for item in kb_vers_map]
                   kbs_no_kg = filter(lambda it: it not in kbs_has_kg, kbs)
              3.合并有KG记录的知识库和无KG记录的知识库，并加上comp_id
                [(know_base_id,version,comp_id),(know_base_id,version,comp_id),()]
              4.将待训练的知识库的版本(训练次数)均增1,并将训练的知识库加到redis中
                    cache.set("ai_%s" % kb_id, str(kg_version), timeout=1209600)
              5.将数据更新到KG,训练任务表，训练&发布历史表中
                kg_id = 'ai_' + kb_id + '_' + str(kg_version)
                KG表中，知识库的训练状态和使用均为0
                KnowGraphs.objects.bulk_create(kg_objs)
                训练任务表：任务状态 0
                TrainingMission.objects.bulk_create(mission_objs)
                训练&发布历史表：状态为 0，训练
                TrainPubHistory.objects.bulk_create(history_objs)
    2.知识库发布：
         Request:
            url = url + "/train/inspect/"
            data = {
                "kbIds": [{"kbId": kbid}]
            }

          Deal：
            1.校验待发布的知识库在KG中是否都有训练版本，若存在无训练记录的知识库就返回
                last_vers_state = list(
                    KnowGraphs.objects.all().filter(know_base_id__in=kb_ids).values('know_base_id').annotate(
                    last_vers=Max('kg_version')).values_list('know_base_id', 'last_vers'))
                kb_has_vers = list(map(lambda x: x[0], last_vers_state))
                 kb_no_vers = set(kb_ids) - set(kb_has_vers)
            2.修改in_use的状态,将次新的版本 in_use置为0 将最新的版本 in_use置为1
              如上次的版本是5，且已经发布了，状态为1，当前的版本是6，发布当前版本将版本5的状态改为0，版本6的改为1
               # 将KG中次新的版本 in_use置为0 通过知识库id修改
               KnowGraphs.objects.all().filter(know_base_id__in=kb_ids, in_use=1).update(in_use=0)
               # 将KG中最新的版本 in_use置为1  通过KGid修改
                kg_ids_new = list(map(lambda x: 'ai_' + x[0] + '_' + str(x[1]), last_vers_state))
                KnowGraphs.objects.all().filter(id__in=kg_ids_new).update(in_use=1)
            3.将发布后的知识库存到reids中
                cache.set("inuse_%s" % str(know_base_id), str(last_vers), timeout=1209600)
    3.训练状态检测：
     Request:
        url = url + "/train/inspect/"
        data = {
            "kbIds": [{"kbId": kbid}]
        }

     Deal:
         1.校验检测的知识库在KG中是否都有训练版本。取出知识库id和最新的版本号
         2.通过知识库id拼接处其在KG中对应的kg_id,通过kg_id获取到train_state
         3. 如果所有的知识库的最新版本train_state都为2返回为2 都为0返回0，其他的返回1

    4.发布状态检测：检查指定知识库在KG中发布状态是否为1(使用中)
        Request:
            url = url + "/train/status/"
            data = {
                "kbIds": [{"kbId": kbid}]
            }

        Deal:
           1.校验检测的知识库在KG中是否都有训练版本。取出知识库id和最新的版本号
           2.通过知识库id拼接处其在KG中对应的kg_id,通过kg_id获取到in_use
             last_kg_ids = list(map(lambda x: 'ai_' + x[0] + '_' + str(x[1]), last_vers_use))
              last_kg_use = KnowGraphs.objects.all().filter(id__in=last_kg_ids).values_list('in_use')
             如果所有的知识库的最新版本in_use都为1才返回正确的结果，因此需要获得的结果做去重处理
             uses = set(last_kg_use)
             if len(uses) == 1 and uses == {1}:pass

    5.知识库的状态修改
         Request:
                url = url + "/train/inipub/"
                data = {
                    "kbIds": [{"kbId": kbid}]
                }

          Deal:
           1.校验检测的知识库在KG中是否都有训练版本。取出知识库id和最新的版本号
           2.修改KG和训练任务表表中该知识库的训练状态为0
            KnowGraphs.objects.all().filter(know_base_id=kb_id, kg_version=last_version).update(train_state=0)
            TrainingMission.objects.all().filter(know_base_id=kb_id, kg_version=last_version).update(status=0)

	6.删除已训练知识库
	 Request:
                url = url + "/train/delete_kb/"
                data = {
                    "kbIds": [{"kbId": kbid}]
                }

     Deal:
        1.校验检测的知识库在KG中是否都有训练版本。取出知识库id和最新的版本号
        2.刪除訓練任務 刪除歷史記錄 去MONGO库删除需删除的kg 删除知识图 删除问题库 删除知识库

4.QA问答：class TrainSet(ModelViewSet)
    1.预发布qa
         Request:
                url = url + "/qas/prepub/"
                data = {
                    "companyId": companyid,
                    "kbIds": [{"kbId": kbid}],
                    "question": "有沒有的那样海洋的寬光",
                    "top": 1
                }

         Deal:
           1.校验数据中的companyId，kbIds，question是否都存在
           2.校验请求中的知识库在数据库中是否都存在。
                   遍历kbIds,若redis中不存在就去任务表中取出所有的知识库id，全部加到缓存中再去缓存中
                   检测id是否存在，若不存在，返回。存在 kbs_exist自增1，遍历id结束后，对比kbs_exist和len(kbIds)的值
                    if cache.ttl(str(y)) == 0:
                         sql_1 = "select id from app_lexiconindexes where app_lexiconindexes.is_delete = False"
           3.去KG表中查询请求中的知识库有没有已训练完成的版本
                将知识库添加到任务表时已将'ai_kbid'作为key，version作为value存到了redis中，查询是否过期，如果过期，去KG
                表中取出训练完成的所有知识库id和版本号，加到缓存中。通过set(li) - set(kbs_has_vers)找出没有训练完成kg版本的知识库
                 if cache.ttl("ai_"+str(y)) == 0:
                    sql_2 = "select know_base_id, MAX(kg_version) as last_vers from app_knowgraphs where train_state = 2 group by know_base_id"
                    cache.set("ai_%s" % str(key), str(value), timeout=1209600)
           4.去zk中取B类Box的请求地址,
             kb_vers_map = {'ai_id1':version,'ai_id2':version,....}
             li = [id1,id2.....]
             res_data = query_request_z(li, question, kb_vers_map, cp_id)
             去缓存中得到key为'box’的值，若不存在就去ZK中中找到所有B类Box的节点信息，存到redis中
             boxs = [(B/VM1/B1,ip:port/1),(B/VM1/B2,ip:port/2).....]
             if cache.ttl("boxs") == 0:
                cache.set("boxs", str( boxs), timeout=1209600)
             取到所有的Add add_dict = [ip:port/1,ip:port/2....]
           5.分配地址，并向底层发送请求
                第一次qa请求时，N个知识库id，将ip:port/1--ip:port/N的地址分配给这次请求，第二次qa请求时查询范围是M个知识库，
                将ip:port/N+1--ip:port/N+1+M，处理机制：定义全局变量temp，每次有请求来的时候，改变temp的值去分配地址。并发情况情况下
                对这个全局变量需加锁，先来的请求修改完temp值时，第二个请求再处理
                lock_label = True  #起到加锁的作用
                top_label = 0
                global lock_label
                while True:
                    if lock_label:
                        lock_label = False
                        break
                num = len(kb_ids)
                global top_label
                seed = int(top_label)
                temp = (seed + num) % len(boxs)
                top_label = temp
                lock_label = True
                for i in range(0, num):
                    add = add_dict[(seed + i)%len(boxs)]
                    temp_p = Process(target=_writer, args=(q, kb, version, add, issue, cp_id))

                对返回的结果处理后放到队列中q = Manager().Queue()
                     成功匹配到结果：que.put(ret)
                     未匹配到答案：que.put({'not_match':  ret['kbId']})
                     请求失败：que.put({'fail': kb_id})

                所有进程都结束后，从队列中取值，整合结果
                ret = {'no_box': [], 'ans': [], 'not_match': [], 'fail': []}





    2.正式发布qa
        Request:
            url = url + "/qas/formal/"
            data = {
                "companyId": companyid,
                "kbIds": [{"kbId": kbid}],
                "question": "有沒有的那样海洋的寬光",
                "top": 1
            }

        Deal:
        1.校验数据中的companyId，kbIds，question是否都存在
        2.校验请求中的知识库在数据库中是否都存在。
        3.去KG表中查询请求中的知识库有没有使用中的版本
             if cache.ttl("inuse_" + str(y)) == 0:
                 sql_3 = "select know_base_id, kg_version from app_knowgraphs where in_use = True"
        4.去zk中取B类Box的请求地址
        5.分配地址，并向底层发送请求
AI_BOX
    A类Box监控知识库：
        1.创建ChatterBox
            1.创建m个A类，n个B类ChatterBox,并实例化。
                定义type，Name(A1,B1)，VName的host ip port，Zookeeper的host，以num作为ID,path = Type/VName/Name (A/VM1/A1)
            2.实例化后的Box对象连接ZK
            3.在ZK上创建节点信息
                1.创建A类节点信息
                    如果ZK中存在当前path，就删除掉，为当前path创建节点信息address = {'target':'Null'}
                    if self._ZK.exists(self._Path):
                          self._ZK.delete(self._Path, recursive=True)
                    self._ZK.create(self._Path, address, None, ephemeral=False, sequence=False, makepath=True)
                    A/VM1/A1 [Target = Null]
                    A/VM1/A2 [Target = Null]
                2.创建B类节点信息
                    为当前path创建节点信息address = "{"Target":"Null","Add":"%s:%s/%s","status":"0","update_time":"%f"}" % (self._IP, self._Port,self._ID,time.time())
                    B/VM1/B1 [Target = Null,Add = ip:port/id,status = 0,update = 当前开始QA时间]
                    B/VM1/B2 [Target = Null,Add = ip:port/id,status = 0,update = 当前开始QA时间]

        2.将知识库的状态由0--3
            查找空余的A类Box,将未训练的知识库状态改为训练中，并将这些知识库的id分别放入不同的空余box
            1.实例化A类Box A0,并不加入到ZK中，而是利用A类Box的属性去ZK中找到所有的A类Box
                 box_list = self._ZK.get_children("/%s/%s" % (self._Type, self._VName))
                 box_list的值应为[A1,A2,A3....]
            2.找到ZK中每个Box的节点信息，判断Target的值,如果值为NULL，则这个Box就是空闲的，将此Box加到空闲Box列表idle_box中
                if eval(data.decode("utf-8"))['Target'] == 'Null':pass

            3.去任务训练表中取出所有状态为0的知识库id和版本号，将每个待训练的知识库id和版本号拼接加到训练任务列表中
                遍历列表,修改知识库的状态 0-3
                query = "SELECT know_base_id, kg_version FROM app_trainingmission WHERE status = '%d' AND is_delete = '%d'" % param
                train_tasks.append("%s_%s" % (id, version))
                 query = "UPDATE app_trainingmission SET status = '%d' WHERE know_base_id = '%s' AND kg_version = '%s' AND status = '%d'"
            4.从空闲的Box中取值，依次分配给每一个修改完状态的知识库。
                从空闲的Box中拿到Box如拿到A1,去ZK中验证A1的节点信息Target是否为Null，若为Null，就讲当前的知识库作为这个Box的Target值
                    Target = ‘kbid_version’
                若为当前的知识库id分配的Box的节点信息不是Null，就讲此知识库的状态再有3--0
                每取出一个待训练的知识库，就为其分配一个Box，每隔10秒就去任务表中取出待训练的知识库，从当前空闲Box列表中取值
                直到当前此找到的所有空闲Box全部分配完，再退出循环
                 while True:
                    datas = self.startMonitorMySQL()
                    if len(datas):
                        for aboxdata in datas:
                            oneabox = box[0]
                            box.pop(0)
                            if not box:return True
                     time.sleep(10)

            5.当前次找到的空闲Box全部分配完之后，sleep10秒后，发起新一轮的查找空闲Box，再分配给待训练的知识库

        3.将正在训练的知识库下的问答对，调用chatterbot 进行训练，修改状态3--2
            1.实例化m个A类Box
            2.每个Box都去连接ZK,开启ZK服务。开启m个线程，每个Box作为一个独立线程去运行(单例模式)
                如Box A1开启监控，训练工作
                1.判断ZK中是否存在A1的节点信息，如果不存在就在ZK中创建这个Box的节点信息
                2.如存在，就在ZK中取出当前Box的节点信息，取出Target的值。如值不为Null，开启Box的数据库连接属性，连接数据库
                3.取出分配给当前Box的知识库id和版本号，去任务表中查询当前知识库的训练状态，判断状态是否为3
                    query = "SELECT status FROM app_trainingmission WHERE know_base_id = '%s' AND kg_version = '%s' AND is_delete = '%d'" % param
                4.如果当前知识库状态为3，就修改任务表中状态3--1。修改成功后，修改该KG表中该知识库的状态0-1
                    query = "UPDATE app_trainingmission SET status = '%d' WHERE know_base_id = '%s' AND kg_version = '%s' AND status = '%d'"
                    query = "UPDATE app_knowgraphs SET train_state = '%d' WHERE know_base_id = '%s' AND kg_version = '%s' AND train_state = '%d'"
                     若失败，将ZK中当前Box释放,Target为Null
                5.调用chatterbot对该知识库训练
                    if self.trainkb(temp_str):pass
                    1.实例化当前知识库的chatbox对象，chatbox的database_uri属性为为mongodb://{{KG_HOST}}:{{KG_PORT}}/
                      database属性为'ai_id_version'
                       def initcbot(self, kbname, onlyread=False):
                            self._Chatbot = ChatBot(self._Name,
                            storage_adapter=CHATTERBOT['storage_adapter'],
                            filters=['chatterbot.filters.RepetitiveResponseFilter'],
                            database_uri=KGDATABASES['database_uri'],
                            database='ai_%s' % kbname,
                            read_only=onlyread,)
                    2.根据该知识库的id,去问答表中找到该知识库对应的问题对id，问题列表，答案，去任务表中获取对应的公司id
                    3.对问题和答案进行训练：answer = "%s@%s" % (answer, id)
                        self._Chatbot.train([question,answer])
                    4.该知识库对应的问答对全部训练成功后，修改任务表中该知识库的状态1--2，KG表中状态1--2 训练后的数据存到了mongodb中
                      若训练失败，将任务表中该知识库的状态1--0，KG表中状态1--0
                    5.将ZK中当前Box释放,Target为Null，关闭数据库连接
            3.所有线程都结束后，将每个Box的ZK服务停止。20s后，再去连接ZK，开启线程，开启新一轮的监控，训练

    B类Box问答处理：
        调用chatterbot 的 get_response的接口，返回答案
        1.创建B类Box和chatterbot机器人
            根据传来的id创建B类Box,id为1就创建B/VM1/B1,为该Box创建chatterbot机器人，机器人的mongo地址和训练时创建的机器人相同
             1.如果该id对应的Box不存在，就去实例化Box(初次请求)
                  if not ThingsResource.workerBbox[boxid]:
                            self.initialbox(boxid, adata['kbid'], adata['version'])

                  def initcbot(self, kbname, onlyread=True):
                        self._Chatbot = ChatBot(self._Name,
                        storage_adapter=CHATTERBOT['storage_adapter'],

                        filters=['chatterbot.filters.RepetitiveResponseFilter'],
                        database_uri=KGDATABASES['database_uri'],
                        database='ai_%s' % kbname,
                        read_only=onlyread,)
                        self._KGname = kbname
             2.如果该id对应的Box已存在，对比Bo的KG属性是否和传来知识库id和版本号是否相同
                 elif operator.ne(ThingsResource.workerBbox[boxid]._KGname, "%s_%s" % (adata['kbid'], adata['version'])):pass
                 初次创建时的KG的版本可能是2，机器人训练完的数据存到数据库'ai_id_2'，本次请求时KG最新的版本可能有更新，版本可能是3
                 此时需要更改Box的KG属性和chatter的database属性，BoxA训练完后数据存到最新mongo中数据库'ai_id_3'中，BoxB取数据应到这个里面去取
                 更改chatterbot属性：
                 self._Chatbot.storage.change_database_etc("ai_%s_%s" % (adata['kbid'], adata['version']))
                 self._KGname = "%s_%s" % (adata['kbid'], adata['version'])
                 self._Chatbot.statement_list = self._Chatbot.storage.get_response_statements()

        2.调用chatterbot 的 get_response接口，去该机器人的mongo库中对应的database中获取到结果
             each = ThingsResource.workerBbox[boxid].get_response(postquestion)

        3.对返回的结果根据相似度做处理
            if each.confidence > 0:
                 data = {
                            'questionid': each.text.split("@")[-1],
                            'answer': each.text.split("@")[0],
                            'score': each.confidence
                            }
                 doc = {'code': 0, 'data': data}
            else:
                 doc = {'code': 1, 'data': {'score': 0}}

