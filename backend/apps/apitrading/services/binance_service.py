import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class BinanceService:
    def __init__(self, credentials):
        self.api_key = credentials.get_decrypted_api_key()
        self.api_secret = credentials.get_decrypted_api_secret()
        self.testnet = credentials.testnet
        
        if self.testnet:
            self.base_url = "https://testnet.binance.vision/api"
        else:
            self.base_url = "https://api.binance.com/api"
    
    def _generate_signature(self, params):
        """Générer la signature HMAC SHA256 pour l'authentification"""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method, endpoint, params=None, signed=False):
        """Faire une requête à l'API Binance"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=params, timeout=10)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête Binance: {e}")
            raise Exception(f"Erreur de connexion à Binance: {str(e)}")
    
    def test_connection(self):
        """Tester la connexion et récupérer les informations du compte"""
        try:
            # Test de l'API key avec l'endpoint account
            account_info = self._make_request('GET', '/v3/account', signed=True)
            
            return {
                'success': True,
                'message': 'Connexion Binance réussie',
                'account_info': {
                    'can_trade': account_info.get('canTrade', False),
                    'can_withdraw': account_info.get('canWithdraw', False),
                    'can_deposit': account_info.get('canDeposit', False),
                    'balances_count': len([b for b in account_info.get('balances', []) if float(b['free']) > 0])
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Échec de la connexion Binance: {str(e)}'
            }
    
    def get_account_info(self):
        """Récupérer les informations détaillées du compte"""
        return self._make_request('GET', '/v3/account', signed=True)
    
    def get_symbol_info(self, symbol):
        """Récupérer les informations d'un symbole"""
        try:
            exchange_info = self._make_request('GET', '/v3/exchangeInfo')
            for s in exchange_info.get('symbols', []):
                if s['symbol'] == symbol:
                    return s
            return None
        except Exception as e:
            logger.error(f"Erreur récupération info symbole {symbol}: {e}")
            return None
    
    def get_ticker_price(self, symbol):
        """Récupérer le prix actuel d'un symbole"""
        try:
            ticker = self._make_request('GET', '/v3/ticker/price', {'symbol': symbol})
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Erreur récupération prix {symbol}: {e}")
            return None
    
    def get_klines(self, symbol, interval='1h', limit=100):
        """Récupérer les données de chandelles"""
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            klines = self._make_request('GET', '/v3/klines', params)
            
            # Convertir en format plus lisible
            formatted_klines = []
            for kline in klines:
                formatted_klines.append({
                    'timestamp': kline[0],
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            return formatted_klines
        except Exception as e:
            logger.error(f"Erreur récupération klines {symbol}: {e}")
            return []
    
    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """Placer un ordre"""
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),  # BUY ou SELL
                'type': order_type.upper(),  # MARKET, LIMIT, STOP_LOSS, etc.
                'quantity': str(quantity)
            }
            
            if order_type.upper() == 'LIMIT' and price:
                params['price'] = str(price)
                params['timeInForce'] = 'GTC'  # Good Till Cancelled
            
            if stop_price:
                params['stopPrice'] = str(stop_price)
            
            result = self._make_request('POST', '/v3/order', params, signed=True)
            return {
                'success': True,
                'order_id': result['orderId'],
                'data': result
            }
        
        except Exception as e:
            logger.error(f"Erreur placement ordre {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_open_orders(self, symbol=None):
        """Récupérer les ordres ouverts"""
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            orders = self._make_request('GET', '/v3/openOrders', params, signed=True)
            return orders
        except Exception as e:
            logger.error(f"Erreur récupération ordres ouverts: {e}")
            return []
    
    def cancel_order(self, symbol, order_id):
        """Annuler un ordre"""
        try:
            params = {
                'symbol': symbol,
                'orderId': order_id
            }
            result = self._make_request('DELETE', '/v3/order', params, signed=True)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            logger.error(f"Erreur annulation ordre {order_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def test_binance_connection(credentials):
    """Fonction helper pour tester la connexion Binance"""
    service = BinanceService(credentials)
    return service.test_connection()
