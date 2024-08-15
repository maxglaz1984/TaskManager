from django.contrib import admin
from .models import *


admin.site.register(TGUser)
admin.site.register(Task)
admin.site.register(TaskStatus)
admin.site.register(TaskPriority)