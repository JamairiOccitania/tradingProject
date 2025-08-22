from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import os

# Service de chiffrement - génération sécurisée de la clé si elle n'existe pas
def get_or_create_encryption_key():
    """Obtient ou crée une clé de chiffrement"""
    try:
        # Essayer d'utiliser la clé des settings
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if key:
            # S'assurer que la clé est au bon format
            if isinstance(key, str):
                if len(key) == 44 and key.endswith('='):
                    # Clé déjà au format base64
                    return Fernet(key.encode())
                else:
                    # Clé brute, encoder en base64
                    key_bytes = key.encode()[:32].ljust(32, b'0')  # Assurer 32 bytes
                    key_b64 = base64.urlsafe_b64encode(key_bytes)
                    return Fernet(key_b64)
        
        # Générer une nouvelle clé si aucune n'existe
        key = Fernet.generate_key()
        print(f"ATTENTION: Nouvelle clé de chiffrement générée: {key.decode()}")
        print("Ajoutez cette clé à vos variables d'environnement: ENCRYPTION_KEY")
        return Fernet(key)
    
    except Exception as e:
        # Fallback: générer une clé temporaire
        print(f"Erreur de configuration de chiffrement: {e}")
        key = Fernet.generate_key()
        return Fernet(key)

fernet = get_or_create_encryption_key()

class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oanda_api_key = models.CharField(max_length=255, null=True, blank=True)
    oanda_account_id = models.CharField(max_length=100, null=True, blank=True)
    encrypted_key = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.oanda_api_key:
            self.encrypted_key = fernet.encrypt(self.oanda_api_key.encode())
        super().save(*args, **kwargs)

    def get_decrypted_key(self):
        if self.encrypted_key:
            try:
                return fernet.decrypt(self.encrypted_key).decode()
            except Exception as e:
                print(f"Erreur déchiffrement API key: {e}")
                return None
        return None

    def __str__(self):
        return f"Clé API pour {self.user.username}"

class BrokerCredentials(models.Model):
    """Stockage sécurisé des identifiants pour différents brokers"""
    BROKER_CHOICES = (
        ('binance', 'Binance'),
        ('oanda', 'Oanda'),
        ('ig', 'IG'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.CharField(max_length=20, choices=BROKER_CHOICES)
    
    # Champs spécifiques Oanda
    account_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Champs spécifiques Binance
    testnet = models.BooleanField(default=True, help_text="Utiliser le testnet Binance")
    
    # Champs spécifiques IG
    demo = models.BooleanField(default=True, help_text="Utiliser le compte démo IG")
    
    # Chiffrement - seuls ces champs sont stockés en base
    encrypted_api_key = models.BinaryField(null=True, blank=True)
    encrypted_api_secret = models.BinaryField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'broker']
    
    def set_api_key(self, api_key):
        """Chiffrer et stocker la clé API"""
        if api_key:
            self.encrypted_api_key = fernet.encrypt(api_key.encode())
    
    def set_api_secret(self, api_secret):
        """Chiffrer et stocker le secret API"""
        if api_secret:
            self.encrypted_api_secret = fernet.encrypt(api_secret.encode())
    
    def get_decrypted_api_key(self):
        if self.encrypted_api_key:
            try:
                return fernet.decrypt(self.encrypted_api_key).decode()
            except Exception as e:
                print(f"Erreur déchiffrement API key: {e}")
                return None
        return None
    
    def get_decrypted_api_secret(self):
        if self.encrypted_api_secret:
            try:
                return fernet.decrypt(self.encrypted_api_secret).decode()
            except Exception as e:
                print(f"Erreur déchiffrement API secret: {e}")
                return None
        return None
    
    def __str__(self):
        return f"{self.broker.title()} - {self.user.username}"

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
    BROKER_CHOICES = (
        ('binance', 'Binance'),
        ('oanda', 'Oanda'),
        ('ig', 'IG'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    asset = models.CharField(max_length=20) # e.g., 'XAU_USD' pour Oanda, 'BTCUSDT' pour Binance
    broker = models.CharField(max_length=20, choices=BROKER_CHOICES, default='oanda')
    strategy = models.CharField(max_length=50, choices=STRATEGY_CHOICES)
    parameters = models.JSONField() # e.g., {'rsi_period': 14, 'sma_period': 50, 'tp': 0.05, 'sl': 0.02, 'position_size': 100}
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='paper')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='stopped')
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.broker.title()}: {self.asset}) - {self.status}"

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

class TrailingStop(models.Model):
    """Trailing Stop : stop-loss dynamique qui suit le prix favorable"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('triggered', 'Triggered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.CharField(max_length=20)
    position_type = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])
    entry_price = models.FloatField()
    current_price = models.FloatField()
    trailing_distance = models.FloatField(help_text="Distance en pourcentage (ex: 0.02 pour 2%)")
    stop_price = models.FloatField()
    highest_price = models.FloatField(null=True, blank=True)  # Pour les positions long
    lowest_price = models.FloatField(null=True, blank=True)   # Pour les positions short
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Trailing Stop {self.asset} - {self.position_type} @ {self.stop_price}"

class PositionSizing(models.Model):
    """Position sizing dynamique : ajustement de la taille des positions selon le risque"""
    SIZING_METHOD_CHOICES = (
        ('fixed_percent', 'Pourcentage fixe du capital'),
        ('kelly', 'Critère de Kelly'),
        ('volatility_based', 'Basé sur la volatilité'),
        ('risk_parity', 'Risk Parity'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    method = models.CharField(max_length=30, choices=SIZING_METHOD_CHOICES)
    risk_percentage = models.FloatField(help_text="Pourcentage du capital à risquer (ex: 0.02 pour 2%)")
    max_position_size = models.FloatField(help_text="Taille maximale de position en unités")
    min_position_size = models.FloatField(help_text="Taille minimale de position en unités")
    parameters = models.JSONField(default=dict, help_text="Paramètres spécifiques à la méthode")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_position_size(self, account_balance, asset_price, volatility=None):
        """Calcule la taille de position basée sur la méthode choisie"""
        if self.method == 'fixed_percent':
            risk_amount = account_balance * self.risk_percentage
            position_size = risk_amount / asset_price
        elif self.method == 'volatility_based' and volatility:
            # Ajuste la taille selon la volatilité
            base_size = account_balance * self.risk_percentage / asset_price
            position_size = base_size / (volatility + 0.01)  # Évite division par zéro
        else:
            position_size = account_balance * self.risk_percentage / asset_price
            
        # Applique les limites min/max
        return max(self.min_position_size, min(self.max_position_size, position_size))
    
    def __str__(self):
        return f"Position Sizing: {self.name} ({self.method})"

class HedgingStrategy(models.Model):
    """Hedging : autoriser des positions opposées sur différents actifs corrélés"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('paused', 'Paused'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    primary_asset = models.CharField(max_length=20, help_text="Asset principal (ex: XAU_USD)")
    hedge_asset = models.CharField(max_length=20, help_text="Asset de couverture (ex: DXY)")
    correlation_coefficient = models.FloatField(help_text="Coefficient de corrélation attendu")
    hedge_ratio = models.FloatField(help_text="Ratio de couverture (ex: 0.8)")
    primary_position_size = models.FloatField()
    hedge_position_size = models.FloatField()
    primary_position_type = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])
    hedge_position_type = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Hedge: {self.primary_asset} vs {self.hedge_asset}"

class GridBot(models.Model):
    """Grille de trading (Grid bot) : stratégie d'achat/vente par paliers"""
    STATUS_CHOICES = (
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    asset = models.CharField(max_length=20)
    lower_price = models.FloatField(help_text="Prix plancher de la grille")
    upper_price = models.FloatField(help_text="Prix plafond de la grille")
    grid_levels = models.IntegerField(help_text="Nombre de niveaux dans la grille")
    order_size = models.FloatField(help_text="Taille de chaque ordre")
    total_investment = models.FloatField(help_text="Investissement total")
    profit_per_grid = models.FloatField(help_text="Profit attendu par niveau")
    current_level = models.IntegerField(default=0)
    total_profit = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped')
    parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_grid_prices(self):
        """Calcule les prix de chaque niveau de la grille"""
        price_step = (self.upper_price - self.lower_price) / (self.grid_levels - 1)
        return [self.lower_price + i * price_step for i in range(self.grid_levels)]
    
    def __str__(self):
        return f"Grid Bot: {self.name} ({self.asset})"

class GridOrder(models.Model):
    """Ordres individuels d'un Grid Bot"""
    ORDER_TYPE_CHOICES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
    )
    
    grid_bot = models.ForeignKey(GridBot, on_delete=models.CASCADE, related_name='orders')
    level = models.IntegerField()
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    price = models.FloatField()
    size = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    filled_price = models.FloatField(null=True, blank=True)
    filled_at = models.DateTimeField(null=True, blank=True)
    profit = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Grid Order: {self.order_type} {self.size} @ {self.price}"

class ArbitrageStrategy(models.Model):
    """Arbitrage inter-actifs : ex. corrélation or/argent, BTC/ETH"""
    STATUS_CHOICES = (
        ('monitoring', 'Monitoring'),
        ('executing', 'Executing'),
        ('closed', 'Closed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    asset_a = models.CharField(max_length=20, help_text="Premier asset (ex: XAU_USD)")
    asset_b = models.CharField(max_length=20, help_text="Deuxième asset (ex: XAG_USD)")
    expected_ratio = models.FloatField(help_text="Ratio attendu A/B")
    threshold_percentage = models.FloatField(help_text="Seuil de déclenchement en %")
    position_size = models.FloatField()
    current_ratio = models.FloatField(null=True, blank=True)
    entry_ratio = models.FloatField(null=True, blank=True)
    profit_target = models.FloatField(help_text="Objectif de profit en %")
    max_loss = models.FloatField(help_text="Perte maximale acceptée en %")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='monitoring')
    total_profit = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_opportunity(self, price_a, price_b):
        """Calcule l'opportunité d'arbitrage"""
        current_ratio = price_a / price_b
        deviation = abs(current_ratio - self.expected_ratio) / self.expected_ratio
        return deviation >= (self.threshold_percentage / 100), current_ratio, deviation
    
    def __str__(self):
        return f"Arbitrage: {self.asset_a}/{self.asset_b}"

class ArbitrageTrade(models.Model):
    """Trades individuels d'une stratégie d'arbitrage"""
    strategy = models.ForeignKey(ArbitrageStrategy, on_delete=models.CASCADE, related_name='trades')
    entry_price_a = models.FloatField()
    entry_price_b = models.FloatField()
    entry_ratio = models.FloatField()
    exit_price_a = models.FloatField(null=True, blank=True)
    exit_price_b = models.FloatField(null=True, blank=True)
    exit_ratio = models.FloatField(null=True, blank=True)
    position_a_type = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])
    position_b_type = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])
    profit = models.FloatField(default=0.0)
    is_closed = models.BooleanField(default=False)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Arbitrage Trade: {self.strategy.name} @ {self.entry_ratio}"
