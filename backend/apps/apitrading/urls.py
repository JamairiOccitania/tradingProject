from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, BotViewSet, APIKeyViewSet, AccountSummaryView, BacktestViewSet,
    password_reset_request, password_reset_confirm, user_profile, change_password, delete_account,
    dashboard_stats
)

router = DefaultRouter()
router.register(r'bots', BotViewSet)
router.register(r'keys', APIKeyViewSet)
router.register(r'backtests', BacktestViewSet)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard_stats, name='dashboard_stats'),
    path('account-summary/', AccountSummaryView.as_view(), name='account_summary'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('profile/', user_profile, name='user_profile'),
    path('change-password/', change_password, name='change_password'),
    path('delete-account/', delete_account, name='delete_account'),
    path('', include(router.urls)),
]
