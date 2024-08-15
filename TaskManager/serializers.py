from rest_framework import serializers

from .models import *


class TGUserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TGUser
        fields = "__all__"


class TaskStatusReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = '__all__'


class TaskPriorityReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPriority
        fields = '__all__'


class TaskReadSerializer(serializers.ModelSerializer):
    priority = TaskPriorityReadSerializer(read_only=True)
    status = TaskStatusReadSerializer(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"


class TaskWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
