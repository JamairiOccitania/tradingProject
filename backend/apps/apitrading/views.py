from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Bot, APIKey, TradeLog, Backtest
from .serializers import (
    UserSerializer, BotSerializer, APIKeySerializer, 
    BacktestSerializer, PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer, UserProfileSerializer, 
    ChangePasswordSerializer
)
from apps.trading.tasks import run_bot_task, stop_bot_task, run_backtest_task
from apps.trading.oanda import OandaAPI
from .utils import decrypt_key

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()
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
    queryset = APIKey.objects.all()
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
    queryset = Backtest.objects.all()
    serializer_class = BacktestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Backtest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        backtest = serializer.save(user=self.request.user)
        run_backtest_task.delay(backtest.id)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Demande de réinitialisation de mot de passe"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # URL de réinitialisation (à adapter selon votre frontend)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Envoi de l'email
            send_mail(
                subject='Réinitialisation de votre mot de passe',
                message=f'Cliquez sur ce lien pour réinitialiser votre mot de passe: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({'message': 'Email de réinitialisation envoyé'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Pour des raisons de sécurité, on ne révèle pas si l'email existe
            return Response({'message': 'Email de réinitialisation envoyé'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirmation de réinitialisation de mot de passe"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Le frontend doit envoyer uid et token séparément
            uid = request.data.get('uid')
            token = request.data.get('token')
            
            if not uid or not token:
                return Response({'error': 'UID et token requis'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Mot de passe réinitialisé avec succès'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Token invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, ValueError, UnicodeDecodeError):
            return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Gestion du profil utilisateur"""
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Changement de mot de passe"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Ancien mot de passe incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Mot de passe modifié avec succès'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Suppression du compte utilisateur"""
    user = request.user
    user.delete()
    return Response({'message': 'Compte supprimé avec succès'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Statistiques du tableau de bord"""
    user = request.user
    
    # Statistiques des bots
    total_bots = Bot.objects.filter(user=user).count()
    running_bots = Bot.objects.filter(user=user, status='running').count()
    
    # Balance totale (simulée pour le moment - à connecter avec OANDA API)
    try:
        api_key_obj = APIKey.objects.get(user=user)
        # Ici tu peux intégrer l'API OANDA pour récupérer la vraie balance
        total_balance = 10000.0  # Valeur par défaut
    except APIKey.DoesNotExist:
        total_balance = 0.0
    
    # P&L du jour (basé sur les logs de trading)
    today = timezone.now().date()
    today_logs = TradeLog.objects.filter(
        bot__user=user,
        timestamp__date=today,
        profit_loss__isnull=False
    )
    today_pnl = today_logs.aggregate(total=Sum('profit_loss'))['total'] or 0.0
    
    # Statistiques des backtests
    total_backtests = Backtest.objects.filter(user=user).count()
    completed_backtests = Backtest.objects.filter(user=user, status='completed').count()
    
    # Performance moyenne (basée sur les backtests complétés)
    avg_performance = 85.0  # Valeur par défaut, à calculer selon tes métriques
    
    # Activité récente
    recent_trades = TradeLog.objects.filter(
        bot__user=user
    ).order_by('-timestamp')[:5].values(
        'bot__name', 'decision', 'price', 'profit_loss', 'timestamp'
    )
    
    return Response({
        'totalBots': total_bots,
        'runningBots': running_bots,
        'totalBalance': total_balance,
        'todayPnL': float(today_pnl),
        'totalBacktests': total_backtests,
        'completedBacktests': completed_backtests,
        'avgPerformance': avg_performance,
        'recentTrades': list(recent_trades)
    })
