from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, BotViewSet, APIKeyViewSet, AccountSummaryView, BacktestViewSet,
    password_reset_request, password_reset_confirm, user_profile, change_password, delete_account,
    dashboard_stats, TrailingStopViewSet, PositionSizingViewSet, HedgingStrategyViewSet,
    GridBotViewSet, ArbitrageStrategyViewSet, advanced_trading_stats, test_celery_task, check_task_status,
    arbitrage_strategy_list, arbitrage_strategy_detail, broker_credentials_list, broker_credentials_detail,
    test_broker_connection, test_celery, task_status, test_broker_creation
)

router = DefaultRouter()
router.register(r'bots', BotViewSet)
router.register(r'keys', APIKeyViewSet)
router.register(r'backtests', BacktestViewSet)
router.register(r'trailing-stops', TrailingStopViewSet)
router.register(r'position-sizing', PositionSizingViewSet)
router.register(r'hedging', HedgingStrategyViewSet)
router.register(r'grid-bots', GridBotViewSet)
router.register(r'arbitrage', ArbitrageStrategyViewSet)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard_stats, name='dashboard_stats'),
    path('advanced-stats/', advanced_trading_stats, name='advanced_trading_stats'),
    path('test-celery/', test_celery_task, name='test_celery_task'),
    path('task-status/<str:task_id>/', check_task_status, name='check_task_status'),
    path('account-summary/', AccountSummaryView.as_view(), name='account_summary'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('profile/', user_profile, name='user_profile'),
    path('change-password/', change_password, name='change_password'),
    path('delete-account/', delete_account, name='delete_account'),
    path('arbitrage-strategies/', arbitrage_strategy_list, name='arbitrage-strategy-list'),
    path('arbitrage-strategies/<int:pk>/', arbitrage_strategy_detail, name='arbitrage-strategy-detail'),
    path('broker-credentials/', broker_credentials_list, name='broker-credentials-list'),
    path('broker-credentials/<int:pk>/', broker_credentials_detail, name='broker-credentials-detail'),
    path('broker-credentials/<int:pk>/test/', test_broker_connection, name='test-broker-connection'),
    path('test-celery/', test_celery, name='test-celery'),
    path('task-status/<str:task_id>/', task_status, name='task-status'),
    path('test-broker-creation/', test_broker_creation, name='test-broker-creation'),
    path('', include(router.urls)),
]
