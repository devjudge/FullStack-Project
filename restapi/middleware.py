from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class RestapiMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if request.path == '/signup/' or request.path == '/login/' or request.path == '/logout/':
            pass

        else:
            auth_token = request.META['HTTP_AUTH_TOKEN']
            try:
                result = User.objects.get(auth_token=auth_token)
                print(result)

            except User.DoesNotExist as e:
                error = {"status": "failure", "reason": str(e)}
                return JsonResponse(error, status=status.HTTP_401_UNAUTHORIZED)
