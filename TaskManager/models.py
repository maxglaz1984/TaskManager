import random

from django.db import models
from django.contrib.auth.models import User, Group


def generate_random_code():
    return str(random.randint(1000, 9999))


class TGUser(models.Model):
    tg_id = models.IntegerField(unique=True, verbose_name="TG ID")
    email = models.CharField(max_length=255, verbose_name="email")
    confirmed = models.BooleanField(verbose_name="Подтверждена учетная запись?", default=False)

    def __str__(self):
        return f"{self.tg_id}"


class ConfirmationCode(models.Model):
    user = models.OneToOneField(TGUser, verbose_name="Пользователь TG", on_delete=models.CASCADE)
    code = models.IntegerField(default=generate_random_code, verbose_name="Код")
    creation_datetime = models.DateTimeField(auto_now_add=True)


class TaskPriority(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название приоритетности")

    def __str__(self):
        return self.name


class TaskStatus(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название статуса")

    def __str__(self):
        return self.name


class Task(models.Model):
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE, verbose_name="Пользователь", null=True)
    name = models.CharField(max_length=255, verbose_name="Заголовок задачи", null=True)
    text = models.TextField(verbose_name="Текст задачи", null=True)
    deadline_date = models.DateTimeField(verbose_name="Дата дедлайна", null=True)
    finished = models.BooleanField(verbose_name="Завершена?", default=False)
    priority = models.ForeignKey(TaskPriority, on_delete=models.SET_NULL, null=True, verbose_name="Приоритет")
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, verbose_name="Статус")

    def __str__(self):
        return self.name


