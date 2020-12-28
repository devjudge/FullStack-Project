# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import uuid
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
# Create your views here.
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

from restapi.models import Board, Board_Thread, Thread_Comment, UserBoardMapping

logger = logging.getLogger(__name__)


class Register(APIView):

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        email = request.data.get('email', None)

        user = User(
            username=username,
            password=password,
            email=email,
            last_login=datetime.now()
        )

        user.set_password(password)
        user.save()

        if user:
            payload = {
                'id': user.id,
                'username': user.username,
            }

            return Response(
                payload,
                status=201,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Error in signup"}),
                status=400,
                content_type="application/json"
            )


class Login(APIView):

    def post(self, request):
        if not request.data:
            return Response({'Error': "Please provide username/password"}, status=400)

        username = request.data.get('username', None)
        password = request.data.get('password', None)
        if authenticate(username=username, password=password):
            user = User.objects.get(username=username)
        else:
            return Response({'Error': "Invalid username/password"}, status=status.HTTP_404_NOT_FOUND)
        if user:
            payload = {
                'id': user.id,
                'username': user.username,
            }

            return Response(
                payload,
                status=status.HTTP_200_OK,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )


class CreateBoard(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            print(request.user.id)
            data = JSONParser().parse(request)
            board_id = data.get('board_id', None)
            name = data.get('name', None)
            created_by = request.user.id

            if not name:
                return Response({'ERROR': 'Please provide Name of the Board'},
                                status=status.HTTP_400_BAD_REQUEST)

            if Board.objects.filter(name=name).exists():
                return JsonResponse({'ERROR': "Board Already registered! "},
                                    status=status.HTTP_409_CONFLICT)

            user_id = User.objects.get(id=created_by)
            board = Board(unique_id=board_id, created_by=user_id, name=name)
            board.save()
            member = UserBoardMapping(user=user_id, board=board)
            member.save()

            res = {'board-id': board_id}
            return JsonResponse(res, status=status.HTTP_201_CREATED)

        else:
            return Response(
                'User needs to LogIn',
                status=status.HTTP_401_UNAUTHORIZED,
                content_type="application/json"
            )


class JoinBoard(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            data = JSONParser().parse(request)
            board_name = data.get('board_name', None)

            try:
                board_id = get_object_or_404(Board, name=board_name)
            except Board.DoesNotExist:
                raise Http404

            user_id = request.user.id
            user_id = User.objects.get(id=user_id)
            membership = UserBoardMapping(user=user_id, board=board_id, user_type='member')
            membership.save()

            res = {'board-name': board_id.id}
            return JsonResponse(res, status=status.HTTP_201_CREATED)
        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class GetBoard(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            board = Board.objects.select_related('created_by__username', 'created_by__id')
            res = board.values('unique_id', 'name', 'created_by__username', 'created_by__id')
            return JsonResponse({'boards': list(res)}, safe=False, status=status.HTTP_201_CREATED)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


#
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
