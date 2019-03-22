# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from app.models import LexiconIndexes, LexiconMaps, Questions, Words, Synonyms, KnowGraphs, TrainPubHistory, \
    TrainingMission

admin.site.register(LexiconIndexes)
admin.site.register(LexiconMaps)
admin.site.register(Questions)
admin.site.register(Words)
admin.site.register(Synonyms)
admin.site.register(KnowGraphs)
admin.site.register(TrainPubHistory)
admin.site.register(TrainingMission)


