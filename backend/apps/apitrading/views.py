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

from .models import (
    Bot, APIKey, TradeLog, Backtest, TrailingStop, PositionSizing,
    HedgingStrategy, GridBot, ArbitrageStrategy, BrokerCredentials, GridOrder, ArbitrageTrade
)
from .serializers import (
    UserSerializer, BotSerializer, APIKeySerializer, 
    BacktestSerializer, PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer, UserProfileSerializer, 
    ChangePasswordSerializer, TrailingStopSerializer,
    PositionSizingSerializer, HedgingStrategySerializer,
    GridBotSerializer, ArbitrageStrategySerializer, BrokerCredentialsSerializer
)
from apps.trading.tasks import run_bot_task, stop_bot_task, run_backtest_task, test_task, add_numbers
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
    return Response({'message': 'Compte supprimé avec succès'}, status=status.HTTP_204_NO_CONTENT)

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

class TrailingStopViewSet(viewsets.ModelViewSet):
    queryset = TrailingStop.objects.all()
    serializer_class = TrailingStopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrailingStop.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """Met à jour le prix actuel et ajuste le stop si nécessaire"""
        trailing_stop = self.get_object()
        new_price = request.data.get('current_price')
        
        if not new_price:
            return Response({'error': 'current_price required'}, status=400)
        
        trailing_stop.current_price = new_price
        
        # Logique de mise à jour du trailing stop
        if trailing_stop.position_type == 'long':
            if new_price > (trailing_stop.highest_price or trailing_stop.entry_price):
                trailing_stop.highest_price = new_price
                new_stop = new_price * (1 - trailing_stop.trailing_distance)
                if new_stop > trailing_stop.stop_price:
                    trailing_stop.stop_price = new_stop
        else:  # short position
            if new_price < (trailing_stop.lowest_price or trailing_stop.entry_price):
                trailing_stop.lowest_price = new_price
                new_stop = new_price * (1 + trailing_stop.trailing_distance)
                if new_stop < trailing_stop.stop_price:
                    trailing_stop.stop_price = new_stop
        
        trailing_stop.save()
        return Response(TrailingStopSerializer(trailing_stop).data)

class PositionSizingViewSet(viewsets.ModelViewSet):
    queryset = PositionSizing.objects.all()
    serializer_class = PositionSizingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PositionSizing.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def calculate_size(self, request, pk=None):
        """Calcule la taille de position pour des paramètres donnés"""
        position_sizing = self.get_object()
        account_balance = request.data.get('account_balance', 10000)
        asset_price = request.data.get('asset_price', 2000)
        volatility = request.data.get('volatility', 0.02)
        
        calculated_size = position_sizing.calculate_position_size(
            account_balance, asset_price, volatility
        )
        
        return Response({
            'calculated_size': calculated_size,
            'account_balance': account_balance,
            'asset_price': asset_price,
            'risk_amount': account_balance * position_sizing.risk_percentage
        })

class HedgingStrategyViewSet(viewsets.ModelViewSet):
    queryset = HedgingStrategy.objects.all()
    serializer_class = HedgingStrategySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HedgingStrategy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Active une stratégie de hedging"""
        strategy = self.get_object()
        strategy.status = 'active'
        strategy.save()
        return Response({'status': 'success', 'message': 'Stratégie de hedging activée'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Ferme une stratégie de hedging"""
        strategy = self.get_object()
        strategy.status = 'closed'
        strategy.save()
        return Response({'status': 'success', 'message': 'Stratégie de hedging fermée'})

class GridBotViewSet(viewsets.ModelViewSet):
    queryset = GridBot.objects.all()
    serializer_class = GridBotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GridBot.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        grid_bot = serializer.save(user=self.request.user)
        # Créer les ordres de la grille
        self._create_grid_orders(grid_bot)

    def _create_grid_orders(self, grid_bot):
        """Crée les ordres initiaux de la grille"""
        from .models import GridOrder
        
        grid_prices = grid_bot.get_grid_prices()
        for i, price in enumerate(grid_prices):
            # Alterne entre ordres d'achat et de vente
            order_type = 'buy' if i % 2 == 0 else 'sell'
            GridOrder.objects.create(
                grid_bot=grid_bot,
                level=i,
                order_type=order_type,
                price=price,
                size=grid_bot.order_size
            )

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Démarre un grid bot"""
        grid_bot = self.get_object()
        if grid_bot.status == 'running':
            return Response({'error': 'Grid bot is already running'}, status=400)
        
        grid_bot.status = 'running'
        grid_bot.save()
        return Response({'status': 'success', 'message': f'Grid bot {grid_bot.name} started'})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Arrête un grid bot"""
        grid_bot = self.get_object()
        grid_bot.status = 'stopped'
        grid_bot.save()
        return Response({'status': 'success', 'message': f'Grid bot {grid_bot.name} stopped'})

class ArbitrageStrategyViewSet(viewsets.ModelViewSet):
    queryset = ArbitrageStrategy.objects.all()
    serializer_class = ArbitrageStrategySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ArbitrageStrategy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def check_opportunity(self, request, pk=None):
        """Vérifie s'il y a une opportunité d'arbitrage"""
        strategy = self.get_object()
        price_a = request.data.get('price_a')
        price_b = request.data.get('price_b')
        
        if not price_a or not price_b:
            return Response({'error': 'price_a and price_b required'}, status=400)
        
        has_opportunity, current_ratio, deviation = strategy.calculate_opportunity(price_a, price_b)
        strategy.current_ratio = current_ratio
        strategy.save()
        
        return Response({
            'has_opportunity': has_opportunity,
            'current_ratio': current_ratio,
            'expected_ratio': strategy.expected_ratio,
            'deviation_percentage': deviation * 100,
            'threshold_percentage': strategy.threshold_percentage
        })

    @action(detail=True, methods=['post'])
    def execute_trade(self, request, pk=None):
        """Exécute un trade d'arbitrage"""
        from .models import ArbitrageTrade
        
        strategy = self.get_object()
        price_a = request.data.get('price_a')
        price_b = request.data.get('price_b')
        
        if not price_a or not price_b:
            return Response({'error': 'price_a and price_b required'}, status=400)
        
        # Détermine le type de positions selon le ratio
        current_ratio = price_a / price_b
        if current_ratio > strategy.expected_ratio:
            # Ratio trop élevé : vendre A, acheter B
            position_a_type = 'short'
            position_b_type = 'long'
        else:
            # Ratio trop bas : acheter A, vendre B
            position_a_type = 'long'
            position_b_type = 'short'
        
        trade = ArbitrageTrade.objects.create(
            strategy=strategy,
            entry_price_a=price_a,
            entry_price_b=price_b,
            entry_ratio=current_ratio,
            position_a_type=position_a_type,
            position_b_type=position_b_type
        )
        
        strategy.status = 'executing'
        strategy.entry_ratio = current_ratio
        strategy.save()
        
        return Response({
            'status': 'success',
            'message': 'Trade d\'arbitrage exécuté',
            'trade_id': trade.id,
            'positions': {
                'asset_a': f"{position_a_type} {strategy.asset_a} @ {price_a}",
                'asset_b': f"{position_b_type} {strategy.asset_b} @ {price_b}"
            }
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advanced_trading_stats(request):
    """Statistiques des fonctionnalités avancées"""
    user = request.user
    
    # Statistiques Trailing Stops
    active_trailing_stops = TrailingStop.objects.filter(user=user, status='active').count()
    triggered_trailing_stops = TrailingStop.objects.filter(user=user, status='triggered').count()
    
    # Statistiques Position Sizing
    position_sizing_configs = PositionSizing.objects.filter(user=user, is_active=True).count()
    
    # Statistiques Hedging
    active_hedging = HedgingStrategy.objects.filter(user=user, status='active').count()
    
    # Statistiques Grid Bots
    running_grid_bots = GridBot.objects.filter(user=user, status='running').count()
    total_grid_profit = GridBot.objects.filter(user=user).aggregate(
        total=Sum('total_profit')
    )['total'] or 0.0
    
    # Statistiques Arbitrage
    monitoring_arbitrage = ArbitrageStrategy.objects.filter(user=user, status='monitoring').count()
    total_arbitrage_profit = ArbitrageStrategy.objects.filter(user=user).aggregate(
        total=Sum('total_profit')
    )['total'] or 0.0
    
    return Response({
        'trailing_stops': {
            'active': active_trailing_stops,
            'triggered': triggered_trailing_stops
        },
        'position_sizing': {
            'active_configs': position_sizing_configs
        },
        'hedging': {
            'active_strategies': active_hedging
        },
        'grid_bots': {
            'running': running_grid_bots,
            'total_profit': float(total_grid_profit)
        },
        'arbitrage': {
            'monitoring': monitoring_arbitrage,
            'total_profit': float(total_arbitrage_profit)
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_celery_task(request):
    """Endpoint pour tester les tâches Celery"""
    from apps.trading.tasks import test_task, add_numbers
    
    task_type = request.data.get('task_type', 'test')
    
    if task_type == 'test':
        message = request.data.get('message', 'Test depuis l\'API!')
        task = test_task.delay(message)
        return Response({
            'task_id': task.id,
            'task_type': 'test_task',
            'message': f'Tâche lancée avec succès: {message}'
        })
    
    elif task_type == 'add':
        x = request.data.get('x', 10)
        y = request.data.get('y', 20)
        task = add_numbers.delay(x, y)
        return Response({
            'task_id': task.id,
            'task_type': 'add_numbers',
            'message': f'Addition lancée: {x} + {y}'
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_celery(request):
    """Endpoint pour tester les tâches Celery - alias pour test_celery_task"""
    from apps.trading.tasks import test_task, add_numbers
    
    task_type = request.data.get('task_type', 'test')
    
    if task_type == 'test':
        message = request.data.get('message', 'Test depuis l\'API!')
        task = test_task.delay(message)
        return Response({
            'task_id': task.id,
            'task_type': 'test_task',
            'message': f'Tâche lancée avec succès: {message}'
        })
    
    elif task_type == 'add':
        x = request.data.get('x', 10)
        y = request.data.get('y', 20)
        task = add_numbers.delay(x, y)
        return Response({
            'task_id': task.id,
            'task_type': 'add_numbers',
            'message': f'Addition lancée: {x} + {y}'
        })
    
    return Response({'error': 'Type de tâche non supporté'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_status(request, task_id):
    """Vérifier le statut d'une tâche Celery"""
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    return Response({
        'task_id': task_id,
        'status': task.status,
        'result': task.result,
        'ready': task.ready(),
        'successful': task.successful() if task.ready() else None
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_task_status(request, task_id):
    """Vérifier le statut d'une tâche"""
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    return Response({
        'task_id': task_id,
        'status': task.status,
        'result': task.result,
        'ready': task.ready(),
        'successful': task.successful() if task.ready() else None
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def broker_credentials_list(request):
    """
    GET: Liste des identifiants broker de l'utilisateur
    POST: Créer de nouveaux identifiants broker
    """
    if request.method == 'GET':
        credentials = BrokerCredentials.objects.filter(user=request.user)
        serializer = BrokerCredentialsSerializer(credentials, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        print(f"DEBUG - Données reçues: {request.data}")
        serializer = BrokerCredentialsSerializer(data=request.data)
        if serializer.is_valid():
            print(f"DEBUG - Données validées: {serializer.validated_data}")
            # Utiliser la méthode create du serializer qui gère le chiffrement
            credentials = serializer.save(user=request.user)
            print(f"DEBUG - Credentials créées, encrypted_api_key: {bool(credentials.encrypted_api_key)}")
            
            # Retourner la réponse avec le serializer mis à jour
            response_serializer = BrokerCredentialsSerializer(credentials)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        print(f"DEBUG - Erreurs de validation: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def broker_credentials_detail(request, pk):
    """
    GET: Récupérer un identifiant broker spécifique
    PUT: Mettre à jour un identifiant broker
    DELETE: Supprimer un identifiant broker
    """
    try:
        credentials = BrokerCredentials.objects.get(pk=pk, user=request.user)
    except BrokerCredentials.DoesNotExist:
        return Response({'error': 'Identifiants non trouvés'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BrokerCredentialsSerializer(credentials)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BrokerCredentialsSerializer(credentials, data=request.data, partial=True)
        if serializer.is_valid():
            # Mettre à jour les champs normaux
            for attr, value in serializer.validated_data.items():
                if attr not in ['api_key', 'api_secret']:
                    setattr(credentials, attr, value)
            
            # Chiffrer les nouvelles clés si fournies
            api_key = serializer.validated_data.get('api_key')
            api_secret = serializer.validated_data.get('api_secret')
            
            if api_key:
                credentials.set_api_key(api_key)
            if api_secret:
                credentials.set_api_secret(api_secret)
            
            credentials.save()
            
            # Retourner la réponse mise à jour
            response_serializer = BrokerCredentialsSerializer(credentials)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not credentials.is_active:
            return Response(
                {'error': 'Ces identifiants sont déjà inactifs'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        credentials.delete()
        return Response({'message': 'Identifiants supprimés avec succès'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_broker_connection(request, pk):
    """
    Tester la connexion avec les identifiants broker
    """
    try:
        credentials = BrokerCredentials.objects.get(pk=pk, user=request.user)
    except BrokerCredentials.DoesNotExist:
        return Response({'error': 'Identifiants non trouvés'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        if credentials.broker == 'binance':
            from .services.binance_service import test_binance_connection
            result = test_binance_connection(credentials)
        elif credentials.broker == 'oanda':
            from .services.oanda_service import test_oanda_connection
            result = test_oanda_connection(credentials)
        elif credentials.broker == 'ig':
            from .services.ig_service import test_ig_connection
            result = test_ig_connection(credentials)
        else:
            return Response({'error': 'Broker non supporté'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': result['success'],
            'message': result['message'],
            'account_info': result.get('account_info', {})
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors du test de connexion: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def arbitrage_strategy_list(request):
    """
    GET: Liste des stratégies d'arbitrage de l'utilisateur
    POST: Créer une nouvelle stratégie d'arbitrage
    """
    if request.method == 'GET':
        strategies = ArbitrageStrategy.objects.filter(user=request.user)
        serializer = ArbitrageStrategySerializer(strategies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ArbitrageStrategySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def arbitrage_strategy_detail(request, pk):
    """
    GET: Détails d'une stratégie d'arbitrage
    PUT: Modifier une stratégie d'arbitrage
    DELETE: Supprimer une stratégie d'arbitrage
    """
    try:
        strategy = ArbitrageStrategy.objects.get(pk=pk, user=request.user)
    except ArbitrageStrategy.DoesNotExist:
        return Response({'error': 'Stratégie non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ArbitrageStrategySerializer(strategy)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ArbitrageStrategySerializer(strategy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        strategy.delete()
        return Response({'message': 'Stratégie supprimée avec succès'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_broker_creation(request):
    """Endpoint de test pour créer un broker avec debug complet"""
    print(f"DEBUG TEST - Données reçues: {request.data}")
    
    # Test direct de création
    from .models import BrokerCredentials
    
    try:
        # Créer manuellement pour tester
        credentials = BrokerCredentials(
            user=request.user,
            broker=request.data.get('broker', 'binance'),
            testnet=request.data.get('testnet', True),
            demo=request.data.get('demo', True)
        )
        
        api_key = request.data.get('api_key')
        api_secret = request.data.get('api_secret')
        
        print(f"DEBUG TEST - Avant chiffrement, api_key: {bool(api_key)}, api_secret: {bool(api_secret)}")
        
        if api_key:
            credentials.set_api_key(api_key)
            print(f"DEBUG TEST - Après set_api_key, encrypted_api_key: {bool(credentials.encrypted_api_key)}")
        
        if api_secret:
            credentials.set_api_secret(api_secret)
            print(f"DEBUG TEST - Après set_api_secret, encrypted_api_secret: {bool(credentials.encrypted_api_secret)}")
        
        credentials.save()
        print(f"DEBUG TEST - Sauvegardé, ID: {credentials.id}")
        
        # Test de déchiffrement
        decrypted_key = credentials.get_decrypted_api_key()
        decrypted_secret = credentials.get_decrypted_api_secret()
        
        print(f"DEBUG TEST - Déchiffrement: key={bool(decrypted_key)}, secret={bool(decrypted_secret)}")
        
        return Response({
            'success': True,
            'id': credentials.id,
            'encrypted_api_key_exists': bool(credentials.encrypted_api_key),
            'encrypted_api_secret_exists': bool(credentials.encrypted_api_secret),
            'decrypted_key_exists': bool(decrypted_key),
            'decrypted_secret_exists': bool(decrypted_secret),
            'decrypted_key_preview': decrypted_key[:10] + '...' if decrypted_key else None,
            'decrypted_secret_preview': decrypted_secret[:10] + '...' if decrypted_secret else None
        })
        
    except Exception as e:
        print(f"DEBUG TEST - Erreur: {e}")
        return Response({'error': str(e)}, status=500)
