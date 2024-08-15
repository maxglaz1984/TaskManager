from django.urls import path
from .views import *

urlpatterns = [
    path('create-tg-user', SendConfirmationEmailView.as_view()),
    path('confirm-email/<int:tg_id>/<int:code>/', CheckConfirmationEmailView.as_view(), name='confirm_email'),
    path('task', TaskView.as_view()),
    path('status', TaskStatusView.as_view()),
    path('priority', TaskPriorityView.as_view()),
    path('finished', Task2View.as_view()),
    path('fire-tasks', Task3View.as_view()),
    path('check-user', CheckUser.as_view())
]