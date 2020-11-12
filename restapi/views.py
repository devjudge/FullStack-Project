# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import uuid

from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from restapi.models import Board, Board_Thread, Thread_Comment, User_Detail, UserBoardMapping
from restapi.serializers import serializer_register

logger = logging.getLogger(__name__)


def signup(request):
    print(request.path)
    data = JSONParser().parse(request)
    data_serialize = serializer_register(data=data)

    if data_serialize.is_valid():
        data_serialize.save()
        user = User_Detail.objects.get(username=data_serialize.data['username'], email=data_serialize.data['email'],
                                       password=data_serialize.data['password'])

        print("New User created as {}".format(user.email))
        data = {
            "id": data_serialize.data['id'],
            "username": data_serialize.data['username'],
            "email": data_serialize.data['email']
        }
        return JsonResponse(data, status=status.HTTP_201_CREATED)

    return JsonResponse({"status": "failure",
                         "reason": data_serialize.errors}, status=status.HTTP_400_BAD_REQUEST)


def login(request):
    print(request.path)
    data = json.loads(request.body.decode("utf-8"))

    try:
        email = data.get('email', None)
        password = data.get('password', None)

        if email and password:
            try:
                result = get_object_or_404(User_Detail, email=email, password=password)
                User_Detail.objects.filter(email=result.email, password=result.password).update(
                    auth_token=uuid.uuid4().hex)

                obj = User_Detail.objects.get(email=email)

            except Http404 as e:
                error = {"status": "failure", "reason": str(e)}
                return JsonResponse(error, status=status.HTTP_404_NOT_FOUND)

            res = {"auth_token": obj.auth_token}
            return JsonResponse(res, status=status.HTTP_201_CREATED)

        res = {"status": "failure"}
        return JsonResponse(res, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        error = {"status": "failure", "reason": str(e)}
        return JsonResponse(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def logout(request):
    try:
        auth_token = request.META['HTTP_AUTH_TOKEN']
        print(auth_token)
        invalidate_token = User_Detail.objects.get(auth_token=auth_token)
        invalidate_token.auth_token = None
        invalidate_token.save()

        return JsonResponse({'detail': "Logged out"}, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        return JsonResponse({"error": ["Token does not exist!"]}, status=status.HTTP_400_BAD_REQUEST)


class CreateBoard(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        unique_id = data.get('board_id', None)
        created_by = data.get('created_by', None)
        name = data.get('name', None)

        if not created_by or not name:
            return Response({'ERROR': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)

        if Board.objects.filter(name=name).exists():
            return JsonResponse({'ERROR': "Board Already registered! "},
                                status=status.HTTP_409_CONFLICT)

        if not User_Detail.objects.filter(username=created_by).exists():
            return JsonResponse({'ERROR': "Username is not registered! "},
                                status=status.HTTP_404_NOT_FOUND)

        username = User_Detail.objects.get(username=created_by)
        board = Board(unique_id=unique_id, created_by=username, name=name)
        board.save()

        res = {'username': created_by}
        return JsonResponse(res, status=status.HTTP_201_CREATED)


class CreateThread(APIView):
    def post(self, request):
        data = JSONParser().parse(request)

        title = data.get('title', None)
        description = data.get('description', None)
        board_id = data.get('board_id', None)
        creator = data.get('creator', None)
        tag = data.get('tag', None)

        if not title or not description:
            return Response({'ERROR': 'Please provide both title and description'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not Board.objects.filter(unique_id=board_id).exists():
            return JsonResponse({'ERROR': "Board does not exists! "},
                                status=status.HTTP_404_NOT_FOUND)

        if not User.objects.filter(username=creator).exists():
            return JsonResponse({'ERROR': "Username is not registered! "},
                                status=status.HTTP_404_NOT_FOUND)

        board = Board.objects.get(unique_id=board_id)
        print(board)
        username = User.objects.get(username=creator)
        board = Board_Thread(title=title, description=description, board=board, creator=username, tag=tag)
        board.save()

        res = {'thread title': title}
        return JsonResponse(res, status=status.HTTP_201_CREATED)


class Comment(APIView):

    def post(self, request):
        data = JSONParser().parse(request)
        text = data.get('text', None)
        thread_title = data.get('thread_title', None)
        author = data.get('author', None)

        if not text or not thread_title:
            return Response({'ERROR': 'Please provide both text and thread_id'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not Board_Thread.objects.filter(title=thread_title).exists():
            return JsonResponse({'ERROR': "Thread does not exists! "},
                                status=status.HTTP_404_NOT_FOUND)

        if not User.objects.filter(username=author).exists():
            return JsonResponse({'ERROR': "Username is not registered! "},
                                status=status.HTTP_404_NOT_FOUND)

        title = Board_Thread.objects.get(title=thread_title)
        print(title)
        username = User.objects.get(username=author)

        com = Thread_Comment(text=text, thread_id=title, author=username)
        com.save()

        res = {'comment': text}
        return JsonResponse(res, status=status.HTTP_201_CREATED)
