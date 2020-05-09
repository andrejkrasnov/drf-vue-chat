from django.contrib import admin
from .models import ChatSessionMessage, ChatSession, ChatSessionMember
# Register your models here.
admin.site.register(ChatSessionMessage)
admin.site.register(ChatSession)
admin.site.register(ChatSessionMember)