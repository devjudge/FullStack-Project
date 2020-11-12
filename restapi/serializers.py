from rest_framework import serializers
from .models import User_Detail


class serializer_register(serializers.ModelSerializer):
    class Meta:
        model = User_Detail
        fields = ('id', 'username',
                        'email', 'password')
