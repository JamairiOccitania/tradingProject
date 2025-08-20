from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Bot, APIKey, TradeLog, Backtest
from .serializers import UserSerializer, BotSerializer, APIKeySerializer, BacktestSerializer
# from ..trading.tasks import run_bot_task, stop_bot_task # A décommenter plus tard
from trading.tasks import run_bot_task, stop_bot_task, run_backtest_task
from trading.oanda import OandaAPI
from .utils import decrypt_key

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        bot = self.get_object()
        if bot.status == 'running':
            return Response({'status': 'error', 'message': 'Bot is already running.'}, status=400)
        
        # task = run_bot_task.delay(bot.id) # A décommenter plus tard
        # bot.celery_task_id = task.id # A décommenter plus tard
        bot.status = 'running'
        bot.save()
        return Response({'status': 'success', 'message': f'Bot {bot.name} started.'})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        bot = self.get_object()
        if bot.status == 'stopped':
            return Response({'status': 'error', 'message': 'Bot is already stopped.'}, status=400)

        # stop_bot_task.delay(bot.celery_task_id) # A décommenter plus tard
        bot.celery_task_id = None
        bot.status = 'stopped'
        bot.save()
        return Response({'status': 'success', 'message': f'Bot {bot.name} stopped.'})

class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AccountSummaryView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            api_key_obj = APIKey.objects.get(user=request.user)
            decrypted_key = decrypt_key(api_key_obj.oanda_api_key)
            api = OandaAPI(decrypted_key, api_key_obj.mode)
            summary = api.get_account_summary(api_key_obj.oanda_account_id)
            return Response(summary)
        except APIKey.DoesNotExist:
            return Response({"error": "API Key not found for this user."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class BacktestViewSet(viewsets.ModelViewSet):
    serializer_class = BacktestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Backtest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        backtest = serializer.save(user=self.request.user)
        run_backtest_task.delay(backtest.id)
