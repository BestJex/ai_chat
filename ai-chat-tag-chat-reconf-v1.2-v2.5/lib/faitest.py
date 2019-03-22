# -*-coding: utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

from chatterbot import ChatBot


class MyChatBot(object):
    def __init__(self, sessionid='demo'):
        self.my_bot = ChatBot(sessionid,
                              storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
                              logic_adapters=[{
                                  'import_path': 'chatterbot.logic.BestMatch'
                              }, {
                                  'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                                  'threshold': 0.0,
                                  'default_response': '正在学习中'
                              }],
                              database_uri='mongodb://172.23.1.156:27017/',
                              database='ai-chatterbot',
                              read_only=True, )

    #        print('my_bot')

    def get_response(self, inputstatement):
        return self.my_bot.get_response(inputstatement)

    def get_similar(self):
        return self.my_bot.similar

        # Note that get_similar must be called after get_response called, or return None

# return my_bot.get_response(inputstatement)
