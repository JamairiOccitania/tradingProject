from django.contrib import admin
from .models import APIKey, Bot, TradeLog

admin.site.register(APIKey)
admin.site.register(Bot)
admin.site.register(TradeLog)
