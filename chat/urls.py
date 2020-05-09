from chat import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('chats/', views.ChatSessionView.as_view()),
    path('chats/<uri>/', views.ChatSessionView.as_view()),
    path('chats/<uri>/messages/', views.ChatSessionMessageView.as_view()),
]