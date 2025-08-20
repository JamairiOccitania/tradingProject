from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Bot, APIKey, TradeLog, Backtest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password=validated_data['password'])
        return user

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ('oanda_api_key',)

class TradeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLog
        fields = '__all__'

class BacktestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backtest
        fields = '__all__'
        read_only_fields = ('user', 'status', 'celery_task_id', 'results', 'created_at')

class BotSerializer(serializers.ModelSerializer):
    logs = TradeLogSerializer(many=True, read_only=True)

    class Meta:
        model = Bot
        fields = ('id', 'name', 'asset', 'strategy', 'parameters', 'mode', 'status', 'logs')
