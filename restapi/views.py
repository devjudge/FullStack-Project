# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import uuid
from datetime import datetime
from django.core import serializers

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

            res = {'board-id': board_id.id}
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
            data = {'boards': list(res)}
            return Response(data, status=status.HTTP_200_OK)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class GetMyBoard(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            board = UserBoardMapping.objects.all().filter(user_id=request.user.id).select_related('board__unique_id',
                                                                                                  'board__name')
            res = board.values('id', 'board__unique_id', 'board__name', 'user_type')
            return JsonResponse({'boards': list(res)}, safe=False, status=status.HTTP_200_OK)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class BoardMembers(APIView):
    def get(self, request, unique_id):
        if request.user.is_authenticated:
            try:
                board_id = get_object_or_404(Board, unique_id=unique_id)
            except Board.DoesNotExist:
                raise Http404
            board = UserBoardMapping.objects.all().filter(board_id=board_id).select_related('board__unique_id',
                                                                                            'board__name')
            res = board.values('id', 'board__unique_id', 'board__name', 'user_type')
            print(type(res))
            return JsonResponse({'boards': list(res)}, safe=False, status=status.HTTP_200_OK)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class CreateThread(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            data = JSONParser().parse(request)

            title = data.get('title', None)
            description = data.get('description', None)
            board_id = data.get('board_id', None)
            tag = data.get('tag', None)
            creator = request.user.id

            if not title or not description:
                return Response({'ERROR': 'Please provide both title and description'},
                                status=status.HTTP_400_BAD_REQUEST)

            if not Board.objects.filter(unique_id=board_id).exists():
                return JsonResponse({'ERROR': "Board does not exists! "},
                                    status=status.HTTP_404_NOT_FOUND)

            if Board_Thread.objects.filter(title=title).exists():
                return JsonResponse({'ERROR': "Thread with same name already exists! "},
                                    status=status.HTTP_400_BAD_REQUEST)

            board_pk = Board.objects.get(unique_id=board_id)
            if UserBoardMapping.objects.filter(board=board_pk, user_type='banned'):
                return JsonResponse({'ERROR': "User is banned for this Board! "},
                                    status=status.HTTP_404_NOT_FOUND)

            board = Board.objects.get(unique_id=board_id)
            print(board)
            user_id = User.objects.get(id=creator)
            board = Board_Thread(title=title, description=description, board=board, tag=tag, creator=user_id)
            board.save()

            res = {'thread title': title}
            return JsonResponse(res, status=status.HTTP_201_CREATED)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class GetAllThread(APIView):

    def get(self, request, unique_id):
        if request.user.is_authenticated:
            board_id = Board.objects.get(unique_id=unique_id)

            thread = Board_Thread.objects.all().filter(board_id=board_id)
            res = thread.values('id', 'board__unique_id', 'title', 'tag', 'status')
            return JsonResponse({'threads': list(res)}, safe=False, status=status.HTTP_200_OK)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class CloseThread(APIView):

    def post(self, request):
        if request.user.is_authenticated:
            data = JSONParser().parse(request)
            title = data.get('title', None)

            if not title:
                return Response({'ERROR': 'Please provide Title'},
                                status=status.HTTP_400_BAD_REQUEST)

            if not Board_Thread.objects.filter(title=title).exists():
                return JsonResponse({'ERROR': "Thread with name does not exists! "},
                                    status=status.HTTP_400_BAD_REQUEST)

            if not UserBoardMapping.objects.get(user=request.user.is_authenticated, user_type='moderator'):
                return JsonResponse({'ERROR': "User is banned for this Board! "},
                                    status=status.HTTP_404_NOT_FOUND)

            thread = Board_Thread.objects.filter(title=title).update(status='close')
            print(thread)
            return JsonResponse({'threads': thread}, status=status.HTTP_200_OK)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )


class Comment(APIView):

    def post(self, request):
        if request.user.is_authenticated:
            data = JSONParser().parse(request)
            text = data.get('text', None)
            thread_title = data.get('thread_title', None)
            commented_by = request.user.id

            if not text or not thread_title:
                return Response({'ERROR': 'Please provide both text and thread_id'},
                                status=status.HTTP_400_BAD_REQUEST)

            if not Board_Thread.objects.filter(title=thread_title).exists():
                return JsonResponse({'ERROR': "Thread does not exists! "},
                                    status=status.HTTP_404_NOT_FOUND)

            title = Board_Thread.objects.get(title=thread_title)
            print(title)
            user_id = User.objects.get(id=commented_by)
            com = Thread_Comment(text=text, thread_id=title, commented_by=user_id)
            com.save()

            res = {'comment': text}
            return JsonResponse(res, status=status.HTTP_201_CREATED)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )

    def get(self, request, thread_title):
        if request.user.is_authenticated:
            thread_id = Board_Thread.objects.get(title=thread_title)
            comment = Thread_Comment.objects.all().filter(thread_id=thread_id).select_related('board_thread__title',)
            res = comment.values('id', 'thread_id', 'text')
            return JsonResponse({'threads': list(res)}, safe=False, status=status.HTTP_200_OK)

        else:
            return Response(
                'User needs to LogIn',
                status=400,
                content_type="application/json"
            )