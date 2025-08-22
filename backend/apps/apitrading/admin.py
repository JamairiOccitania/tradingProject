from django.contrib import admin
from .models import APIKey, Bot, TradeLog, Backtest, BrokerCredentials

# Register your models here.
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

@admin.register(BrokerCredentials)
class BrokerCredentialsAdmin(admin.ModelAdmin):
    list_display = ('user', 'broker', 'is_active', 'testnet', 'demo', 'created_at')
    list_filter = ('broker', 'is_active', 'testnet', 'demo', 'created_at')
    search_fields = ('user__username', 'broker', 'account_id')
    readonly_fields = ('encrypted_api_key', 'encrypted_api_secret', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'broker', 'is_active')
        }),
        ('Configuration spécifique', {
            'fields': ('account_id', 'testnet', 'demo'),
            'description': 'account_id: Username Oanda/IG, testnet: Mode test Binance, demo: Mode démo IG'
        }),
        ('Données chiffrées (lecture seule)', {
            'fields': ('encrypted_api_key', 'encrypted_api_secret'),
            'classes': ('collapse',),
            'description': 'Les clés API sont stockées sous forme chiffrée pour la sécurité'
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # Désactiver l'ajout via l'admin pour forcer l'utilisation de l'API
        return False
    
    def get_readonly_fields(self, request, obj=None):
        # Tous les champs en lecture seule sauf is_active
        if obj:  # Édition
            return self.readonly_fields + ('user', 'broker', 'account_id', 'testnet', 'demo')
        return self.readonly_fields

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
