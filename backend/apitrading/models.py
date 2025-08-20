from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet

# Service de chiffrement
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oanda_api_key = models.CharField(max_length=255)
    encrypted_key = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.encrypted_key = fernet.encrypt(self.oanda_api_key.encode())
        super().save(*args, **kwargs)

    def get_decrypted_key(self):
        return fernet.decrypt(self.encrypted_key).decode()

    def __str__(self):
        return f"Clé API pour {self.user.username}"

class Bot(models.Model):
    STRATEGY_CHOICES = (
        ('RSI_SMA', 'RSI + SMA'),
        ('MACD', 'MACD'),
        ('EMA_CROSS', 'EMA Cross'),
    )
    MODE_CHOICES = (
        ('paper', 'Paper Trading'),
        ('live', 'Live Trading'),
    )
    STATUS_CHOICES = (
        ('running', 'Running'),
        ('stopped', 'Stopped'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    asset = models.CharField(max_length=20) # e.g., 'XAU_USD'
    strategy = models.CharField(max_length=50, choices=STRATEGY_CHOICES)
    parameters = models.JSONField() # e.g., {'rsi_period': 14, 'sma_period': 50, 'tp': 0.05, 'sl': 0.02, 'position_size': 100}
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='paper')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='stopped')
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.asset}) - {self.status}"

class TradeLog(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(max_length=50) # e.g., 'BUY', 'SELL', 'HOLD'
    price = models.FloatField()
    profit_loss = models.FloatField(null=True, blank=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Log pour {self.bot.name} @ {self.timestamp}"

class Backtest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.CharField(max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    strategy = models.CharField(max_length=50)
    parameters = models.JSONField()
    status = models.CharField(max_length=20, default='pending')  # pending, running, completed, failed
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    results = models.JSONField(blank=True, null=True)  # Pour stocker les métriques de performance
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backtest for {self.asset} by {self.user.username} ({self.status})"
