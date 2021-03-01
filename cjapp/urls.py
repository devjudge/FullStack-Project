"""cjapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from restapi import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path("api/signup/", views.Register.as_view(), name="new_user"),
    path("api/login/", views.Login.as_view(), name="login_user"),

    url(r'^api/board/create/', views.CreateBoard.as_view()),
    url(r'^api/board/join/', views.JoinBoard.as_view()),
    url(r'^api/boards/', views.GetBoard.as_view()),
    url(r'^api/myboard/', views.GetMyBoard.as_view()),
    url(r'^api/board/(?P<unique_id>[-\w]+)/$', views.BoardMembers.as_view()),

    url(r'^thread/', views.CreateThread.as_view()),
    url(r'^close/thread/', views.CloseThread.as_view()),
    url(r'^threads/(?P<unique_id>[-\w]+)/$', views.GetAllThread.as_view()),

    url(r'^comment/', views.Comment.as_view()),
    path('comments/<str:thread_title>/', views.Comment.as_view()),
]
