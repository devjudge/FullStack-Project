# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

USER_TYPE = (
    ('moderator', 'moderator User'),
    ('member', 'only member User'),
    ('banned', 'banned User'),
)

STATUS = (
    ('open', 'open thread'),
    ('closed', 'closed thread'),
)


# Create your models here.
class User_Detail(models.Model):
    username = models.CharField(max_length=50, unique=True, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=50)
    auth_token = models.CharField(max_length=100, default=None, null=True)


class Board(models.Model):
    id = models.AutoField(primary_key=True)
    unique_id = models.CharField(max_length=100, null=False, unique=True)
    created_by = models.ForeignKey(User_Detail, on_delete=models.CASCADE, related_name="board_creator")
    name = models.CharField(max_length=100, null=False, unique=
    True)


class UserBoardMapping(models.Model):

    user = models.ManyToManyField(User_Detail)
    board = models.ManyToManyField(Board)
    user_type = models.CharField(max_length=10, choices=USER_TYPE, default='moderator')


class Board_Thread(models.Model):
    id = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="board_name")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    tag = models.CharField(max_length=20, null=False)
    creator = models.ForeignKey(User_Detail, on_delete=models.CASCADE, related_name="thread_creator")
    status = models.CharField(max_length=10, choices=STATUS, default='open')


class Thread_Comment(models.Model):
    id = models.AutoField(primary_key=True)
    thread_id = models.ForeignKey(Board_Thread, on_delete=models.CASCADE, related_name="thread_comment")
    text = models.CharField(max_length=200, null=False)
    author = models.ForeignKey(User_Detail, on_delete=models.CASCADE, related_name="author_name")
