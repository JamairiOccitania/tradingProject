from django.contrib import admin
from .models import APIKey, Bot, TradeLog, Backtest

# Register your models here.
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'asset', 'strategy', 'mode', 'status', 'created_at')
    list_filter = ('strategy', 'mode', 'status', 'created_at')
    search_fields = ('name', 'user__username', 'asset')

@admin.register(TradeLog)
class TradeLogAdmin(admin.ModelAdmin):
    list_display = ('bot', 'timestamp', 'decision', 'price', 'profit_loss')
    list_filter = ('decision', 'timestamp')
    search_fields = ('bot__name',)

@admin.register(Backtest)
class BacktestAdmin(admin.ModelAdmin):
    list_display = ('user', 'asset', 'strategy', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('strategy', 'status', 'created_at')
    search_fields = ('user__username', 'asset')
