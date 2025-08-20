from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import RegisterView, BotViewSet, APIKeyViewSet, AccountSummaryView, BacktestViewSet

router = DefaultRouter()
router.register(r'bots', BotViewSet, basename='bot')
router.register(r'keys', APIKeyViewSet, basename='apikey')
router.register(r'backtests', BacktestViewSet, basename='backtest')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('account/summary/', AccountSummaryView.as_view(), name='account_summary'),
]
