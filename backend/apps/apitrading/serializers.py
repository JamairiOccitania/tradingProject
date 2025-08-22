from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Bot, APIKey, TradeLog, Backtest, TrailingStop, PositionSizing, 
    HedgingStrategy, GridBot, GridOrder, ArbitrageStrategy, ArbitrageTrade,
    BrokerCredentials
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password=validated_data['password'])
        return user

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ('id', 'oanda_api_key', 'oanda_account_id', 'created_at')
        read_only_fields = ('id', 'created_at')

class TradeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLog
        fields = '__all__'

class BacktestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backtest
        fields = '__all__'
        read_only_fields = ('user', 'status', 'celery_task_id', 'results', 'created_at')

class BotSerializer(serializers.ModelSerializer):
    logs = TradeLogSerializer(many=True, read_only=True)

    class Meta:
        model = Bot
        fields = ('id', 'name', 'asset', 'broker', 'strategy', 'parameters', 'mode', 'status', 'logs')

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return data

class TrailingStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrailingStop
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class PositionSizingSerializer(serializers.ModelSerializer):
    calculated_size = serializers.SerializerMethodField()
    
    class Meta:
        model = PositionSizing
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
    
    def get_calculated_size(self, obj):
        # Exemple de calcul avec des valeurs par défaut
        return obj.calculate_position_size(10000, 2000, 0.02)

class HedgingStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = HedgingStrategy
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class GridOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GridOrder
        fields = '__all__'
        read_only_fields = ('created_at', 'filled_at')

class GridBotSerializer(serializers.ModelSerializer):
    orders = GridOrderSerializer(many=True, read_only=True)
    grid_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = GridBot
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'total_profit')
    
    def get_grid_prices(self, obj):
        return obj.get_grid_prices()

class ArbitrageTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArbitrageTrade
        fields = '__all__'
        read_only_fields = ('opened_at', 'closed_at')

class ArbitrageStrategySerializer(serializers.ModelSerializer):
    trades = ArbitrageTradeSerializer(many=True, read_only=True)
    opportunity_status = serializers.SerializerMethodField()
    
    class Meta:
        model = ArbitrageStrategy
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'total_profit')
    
    def get_opportunity_status(self, obj):
        # Exemple avec des prix fictifs - à remplacer par de vraies données
        if obj.current_ratio:
            has_opportunity, current_ratio, deviation = obj.calculate_opportunity(2000, 25)
            return {
                'has_opportunity': has_opportunity,
                'current_ratio': current_ratio,
                'deviation_percentage': deviation * 100
            }
        return None

class BrokerCredentialsSerializer(serializers.ModelSerializer):
    # Champs en écriture seulement pour la sécurité
    api_key = serializers.CharField(write_only=True)
    api_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Champs en lecture pour affichage (masqués)
    api_key_masked = serializers.SerializerMethodField()
    api_secret_masked = serializers.SerializerMethodField()
    
    # Champs pour l'édition (valeurs déchiffrées)
    api_key_decrypted = serializers.SerializerMethodField()
    api_secret_decrypted = serializers.SerializerMethodField()
    
    class Meta:
        model = BrokerCredentials
        fields = (
            'id', 'broker', 'api_key', 'api_secret', 'account_id', 'testnet', 'demo',
            'api_key_masked', 'api_secret_masked', 'api_key_decrypted', 'api_secret_decrypted',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'api_key_masked', 'api_secret_masked', 'api_key_decrypted', 'api_secret_decrypted')
    
    def get_api_key_masked(self, obj):
        """Retourne une version masquée de la clé API"""
        key = obj.get_decrypted_api_key()
        if key and len(key) > 8:
            return key[:4] + '*' * (len(key) - 8) + key[-4:]
        elif key:
            return '*' * len(key)
        return None
    
    def get_api_secret_masked(self, obj):
        """Retourne une version masquée du secret API"""
        secret = obj.get_decrypted_api_secret()
        if secret and len(secret) > 8:
            return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
        elif secret:
            return '*' * len(secret)
        return None
    
    def get_api_key_decrypted(self, obj):
        """Retourne la clé API déchiffrée pour l'édition"""
        return obj.get_decrypted_api_key()
    
    def get_api_secret_decrypted(self, obj):
        """Retourne le secret API déchiffré pour l'édition"""
        return obj.get_decrypted_api_secret()
    
    def create(self, validated_data):
        """Créer une nouvelle instance avec chiffrement"""
        print(f"DEBUG SERIALIZER - create() appelée avec: {validated_data}")
        api_key = validated_data.pop('api_key', None)
        api_secret = validated_data.pop('api_secret', None)
        print(f"DEBUG SERIALIZER - api_key: {bool(api_key)}, api_secret: {bool(api_secret)}")
        
        instance = BrokerCredentials.objects.create(**validated_data)
        print(f"DEBUG SERIALIZER - Instance créée, ID: {instance.id}")
        
        if api_key:
            print(f"DEBUG SERIALIZER - Chiffrement api_key...")
            instance.set_api_key(api_key)
        if api_secret:
            print(f"DEBUG SERIALIZER - Chiffrement api_secret...")
            instance.set_api_secret(api_secret)
        
        instance.save()
        print(f"DEBUG SERIALIZER - Instance sauvée, encrypted_api_key: {bool(instance.encrypted_api_key)}")
        return instance
    
    def update(self, instance, validated_data):
        """Mettre à jour une instance avec chiffrement"""
        api_key = validated_data.pop('api_key', None)
        api_secret = validated_data.pop('api_secret', None)
        
        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Chiffrer les nouvelles clés si fournies
        if api_key:
            instance.set_api_key(api_key)
        if api_secret:
            instance.set_api_secret(api_secret)
        
        instance.save()
        return instance
    
    def validate(self, data):
        """Validation spécifique selon le broker"""
        broker = data.get('broker')
        
        if broker == 'oanda':
            if not data.get('account_id'):
                raise serializers.ValidationError("L'ID de compte Oanda est requis")
        
        elif broker == 'binance':
            if not data.get('api_secret'):
                raise serializers.ValidationError("Le secret API Binance est requis")
        
        elif broker == 'ig':
            if not data.get('account_id'):
                raise serializers.ValidationError("Le nom d'utilisateur IG est requis")
            if not data.get('api_secret'):
                raise serializers.ValidationError("Le mot de passe IG est requis")
        
        return data
