from rest_framework import serializers
from rest_framework.fields import empty

from app.models import LexiconIndexes, Questions, KnowGraphs, TrainingMission


class LexiconIndexesSerializers(serializers.ModelSerializer):
    class Meta:
        model = LexiconIndexes
        fields = '__all__'


class QuestionsSerializers(serializers.ModelSerializer):
    # standard = serializers.PrimaryKeyRelatedField(read_only=True)
    # kb = serializers.SlugRelatedField(
    #     slug_field='id',
    #     queryset=LexiconIndexes.objects.all()
    # )

    class Meta:
        model = Questions
        fields = '__all__'
        # read_only_fields = ('kb',)

    def init(self, instance=None, data=empty, *kwargs):
        super(QuestionsSerializers, self).init(instance=instance, data=data, *kwargs)

    def create(self, validated_data):
        # standard_id = validated_data.pop('standard_id')
        # kb_id = validated_data.pop('kb_id')

        instance = super(QuestionsSerializers, self).create(validated_data)
        # instance.standard_id = standard_id
        # instance.kb_id = kb_id
        # instance.save()
        return instance


class KnowGraphsSerializers(serializers.ModelSerializer):
    class Meta:
        model = KnowGraphs
        fields = '__all__'


class TrainingMissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = TrainingMission
        fields = '__all__'
