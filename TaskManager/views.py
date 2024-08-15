import datetime

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site


def send_email(tg_user, request):
    subject = 'Подтверждение адреса электронной почты'
    code = ConfirmationCode.objects.create(user=tg_user)

    current_site = get_current_site(request)
    confirmation_link = f"http://{current_site.domain}/confirm-email/{tg_user.tg_id}/{code.code}/"
    message = render_to_string('email_confirmation.html',
                               {'confirmation_link': confirmation_link})
    email = EmailMessage(subject, message, to=[tg_user.email])
    email.content_subtype = 'html'
    email.send()


class SendConfirmationEmailView(APIView):
    @staticmethod
    def post(request):

        serializer = TGUserWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            tg_user = serializer.save()
            send_email(tg_user, request)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckUser(APIView):
    def get(self, request):
        data = dict(request.data)
        tg_id = int(data.get("tg_id", None))
        if tg_id:
            if TGUser.objects.filter(tg_id=tg_id, confirmed=True).exists():
                return Response({"confirmed": True}, status=status.HTTP_200_OK)
            else:
                return Response({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'Error': 'Wrong fields'}, status=status.HTTP_400_BAD_REQUEST)


class CheckConfirmationEmailView(View):
    @staticmethod
    def get(request, tg_id, code):
        tg_user = get_object_or_404(TGUser, tg_id=tg_id)
        code_obj = get_object_or_404(ConfirmationCode, user=tg_user)
        print(datetime.datetime.now(datetime.timezone.utc))
        if datetime.datetime.now(datetime.timezone.utc) - code_obj.creation_datetime < datetime.timedelta(minutes=30)\
                and code == code_obj.code:
            tg_user.confirmed = True
            tg_user.save()
            code_obj.delete()
            return render(request, "email_confirmed.html")
        else:
            return render(request, "invalid_confirmation.html")


class TaskView(APIView):
    @staticmethod
    def get(request):
        tg_id = request.GET.get("tg_id")
        task_id = request.GET.get("task_id")
        if task_id:
            tasks = Task.objects.get(id=task_id)
            serializer = TaskReadSerializer(tasks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            tg_user = TGUser.objects.get(tg_id=tg_id)
        except TGUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tg_user.confirmed:
            tasks = Task.objects.filter(user=tg_user, finished=False)
            serializer = TaskReadSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def post(request):
        tg_id = request.GET.get("tg_id")
        try:
            tg_user = TGUser.objects.get(tg_id=tg_id)
        except TGUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tg_user.confirmed:

            try:
                request.data._mutable = True
            except AttributeError:
                pass
            request.data['user'] = tg_user.id

            serializer = TaskWriteSerializer(data=request.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def patch(request):
        tg_id = request.GET.get("tg_id")
        task_id = request.GET.get("task_id")

        if task_id is None or tg_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            tg_user = TGUser.objects.get(tg_id=tg_id)
        except TGUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tg_user.confirmed:

            try:
                request.data._mutable = True
            except AttributeError:
                pass
            request.data['user'] = tg_user.id

            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = TaskWriteSerializer(task, data=request.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request):
        tg_id = request.GET.get("tg_id")
        task_id = request.GET.get("task_id")

        if task_id is None or tg_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            tg_user = TGUser.objects.get(tg_id=tg_id)
        except TGUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tg_user.confirmed:

            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            task.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Task2View(APIView):
    @staticmethod
    def get(request):
        tg_id = request.GET.get("tg_id")
        try:
            tg_user = TGUser.objects.get(tg_id=tg_id)
        except TGUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tg_user.confirmed:
            tasks = Task.objects.filter(user=tg_user, finished=True)
            serializer = TaskReadSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Task3View(APIView):
    @staticmethod
    def get(request):
        tg_id = request.GET.get("tg_id")
        try:
            tg_user = TGUser.objects.get(tg_id=tg_id)
        except TGUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if tg_user.confirmed:
            tasks = Task.objects.filter(user=tg_user, finished=False,
                                        deadline_date__lte=datetime.datetime.now(datetime.timezone.utc))
            serializer = TaskReadSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class TaskStatusView(APIView):
    @staticmethod
    def get(request):
        return Response(TaskStatusReadSerializer(TaskStatus.objects.all(), many=True).data, status=status.HTTP_200_OK)


class TaskPriorityView(APIView):
    @staticmethod
    def get(request):
        return Response(TaskPriorityReadSerializer(TaskPriority.objects.all(), many=True).data,
                        status=status.HTTP_200_OK)
