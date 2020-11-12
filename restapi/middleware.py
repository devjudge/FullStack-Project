from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from restapi.models import User_Detail


class RestapiMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if request.path == '/signup/' or request.path == '/login/' or request.path == '/logout/':
            pass

        else:
            auth_token = request.META['HTTP_AUTH_TOKEN']
            try:
                result = User_Detail.objects.get(auth_token=auth_token)
                print(result)

            except User_Detail.DoesNotExist as e:
                error = {"status": "failure", "reason": str(e)}
                return JsonResponse(error, status=status.HTTP_401_UNAUTHORIZED)
