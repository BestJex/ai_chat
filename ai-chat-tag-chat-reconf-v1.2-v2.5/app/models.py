# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# 各种库的索引表
from common.models import LogicDeleteModel, TimeMarkModel

KNOW_BASE = 0
FILTER_WORDS = 1
PRO_WORDS = 2
SYNONYMS = 3
LEXICON_TYPE = (
    (KNOW_BASE, '知识库'),
    (FILTER_WORDS, '过滤词'),
    (PRO_WORDS, '专有名词'),
    (SYNONYMS, '同义词')
)

WORD_BANK_TYPE = (
    (FILTER_WORDS, '过滤词'),
    (PRO_WORDS, '专有名词'),
    (SYNONYMS, '同义词')
)

WORD_CHAR = (
    (FILTER_WORDS, '过滤词'),
    (PRO_WORDS, '专有名词')
)

UNTRAINED = 0
IN_TRAIN = 1
TRAIN_OK = 2
TRAIN_STATUS = (
    (UNTRAINED, '未训练'),
    (IN_TRAIN, '训练中'),
    (TRAIN_OK, '训练完成')
)

NOTSTARTED = 0
ASSIGNED = 1
EXECUTE = 3
DONE = 2
MISSION_STATUS = (
    (NOTSTARTED, '未开始'),
    (ASSIGNED, '已指派'),
    (EXECUTE, '正在执行中'),
    (DONE, '已完成')
)

TRAIN = 0
ONLINE = 1
OPER_TYPE = (
    (TRAIN, '训练'),
    (ONLINE, '发布')
)


class LexiconIndexes(LogicDeleteModel, TimeMarkModel):
    # 库表唯一标识
    id = models.CharField(primary_key=True, max_length=50, db_index=True, unique=True, verbose_name='库表唯一标识')
    # 词库类型
    lexicon_type = models.SmallIntegerField(choices=LEXICON_TYPE, verbose_name='词库类型')
    # 是否通用 #0 不通用； 1 通用
    is_general = models.BooleanField(default=0, verbose_name='是否通用')
    # 知识库与词库关联
    kb_map = models.ManyToManyField('LexiconIndexes', through='LexiconMaps')

    class Meta:
        verbose_name = '各种库'
        verbose_name_plural = '各种库'


# 知识库与词库关联表
class LexiconMaps(TimeMarkModel):
    # 词库类型
    wb_type = models.SmallIntegerField(choices=WORD_BANK_TYPE, verbose_name='词库类型')
    # 词库
    word_bank = models.ForeignKey('LexiconIndexes', verbose_name='词库', related_name='word_bank',
                                  on_delete=models.CASCADE)
    # 知识库
    know_base = models.ForeignKey('LexiconIndexes', verbose_name='知识库', related_name='know_base',
                                  on_delete=models.CASCADE)

    class Meta:
        verbose_name = '知识库与词库关联'
        verbose_name_plural = '知识库与词库关联'

        index_together = (('word_bank', 'know_base'),)


# 问题表
class Questions(LogicDeleteModel, TimeMarkModel):
    # 问题唯一标识
    id = models.CharField(primary_key=True, max_length=50, verbose_name='问题唯一标识')
    # 标准问题唯一标识
    # standard = models.ForeignKey('Questions', verbose_name='标准问题唯一标识', on_delete=models.CASCADE, null=True)
    # 问题
    content = models.CharField(max_length=256, verbose_name='问题')
    # 知识库唯一标识
    kb = models.ForeignKey('LexiconIndexes', verbose_name='知识库唯一标识', on_delete=models.CASCADE)
    # 是否相似问题 0：否（即为标准问题） 1：是
    is_subordinate = models.BooleanField(default=0, verbose_name='是否相似问题')
    # 答案唯一标识
    answer = models.CharField(max_length=50, verbose_name='答案唯一标识')

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = '问题'


# 词库表
class Words(LogicDeleteModel, TimeMarkModel):
    # 词唯一标识
    id = models.CharField(primary_key=True, max_length=50, verbose_name='词唯一标识')
    # 词
    content = models.CharField(max_length=50)
    # 词库唯一标识
    wb = models.ForeignKey('LexiconIndexes', verbose_name='词库唯一标识', on_delete=models.CASCADE)
    # 词性
    word_character = models.SmallIntegerField(choices=WORD_CHAR, verbose_name='词性')

    class Meta:
        verbose_name = '过滤词或专有名词'
        verbose_name_plural = '过滤词或专有名词'


# 同义词表
class Synonyms(LogicDeleteModel, TimeMarkModel):
    # 词唯一标识
    id = models.CharField(primary_key=True, max_length=50, verbose_name='词唯一标识')
    # 词
    content = models.CharField(max_length=50, verbose_name='词')
    # 词库唯一标识
    wb = models.ForeignKey('LexiconIndexes', verbose_name='词库唯一标识', on_delete=models.CASCADE)
    # 是否普通同义词 0：否（即为基准词）1：是(为普通同义词)
    is_subordinate = models.BooleanField(default=0, verbose_name='是否普通同义词')
    # 基准词唯一标识
    basic = models.ForeignKey('Synonyms', verbose_name='基准词唯一标识', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '同义词'
        verbose_name_plural = '同义词'


class KnowGraphs(TimeMarkModel):
    # KG唯一标识
    id = models.CharField(primary_key=True, max_length=50, verbose_name='KG唯一标识')
    # 知识库唯一标识
    know_base = models.ForeignKey('LexiconIndexes', verbose_name='知识库唯一标识', related_name='kbs',
                                  on_delete=models.CASCADE)

    # KG版本号
    kg_version = models.IntegerField(verbose_name='KG版本号')

    # 是否训练完成 0:未训练 1:训练中 2：训练完成（训练完成）
    train_state = models.SmallIntegerField(choices=TRAIN_STATUS, default=0, verbose_name='训练状态')

    # 是否使用中 0：否（未使用）1：使用中
    in_use = models.BooleanField(default=0, verbose_name='是否使用中')

    class Meta:
        verbose_name = '知识图索引'
        verbose_name_plural = '知识图索引'


class TrainPubHistory(TimeMarkModel):
    # 知识库唯一标识
    kb = models.ForeignKey('LexiconIndexes', verbose_name='知识库唯一标识', related_name='kb', on_delete=models.CASCADE)
    # KG唯一标识 ，对应关系表中使用状态为１的最新数据
    kg = models.ForeignKey('KnowGraphs', verbose_name='KG唯一标识', related_name='kg', on_delete=models.DO_NOTHING,
                           db_constraint=False)
    # 操作类型 0，训练；1，发布
    action = models.SmallIntegerField(choices=OPER_TYPE, default=0, verbose_name='任务状态')

    class Meta:
        verbose_name = '训练&发布历史记录'
        verbose_name_plural = '训练&发布历史记录'


class TrainingMission(LogicDeleteModel, TimeMarkModel):
    # 知识库唯一标识
    know_base = models.ForeignKey('LexiconIndexes', verbose_name='知识库唯一标识', related_name='kbss',
                                  on_delete=models.CASCADE)

    company_id = models.CharField(max_length=50, verbose_name='公司唯一标识')

    # KG版本号
    kg_version = models.IntegerField(verbose_name='KG版本号')

    # 任务状态 0:未开始 1：训练中 2：已完成 3：已指派
    status = models.SmallIntegerField(choices=MISSION_STATUS, default=0, verbose_name='任务状态')

    class Meta:
        verbose_name = '训练任务记录'
        verbose_name_plural = '训练任务记录'
