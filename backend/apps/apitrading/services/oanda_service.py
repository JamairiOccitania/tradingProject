import requests
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OandaService:
    def __init__(self, credentials):
        self.api_key = credentials.get_decrypted_api_key()
        self.account_id = credentials.account_id
        self.base_url = "https://api-fxpractice.oanda.com"  # Demo environment
        # Pour production: "https://api-fxtrade.oanda.com"
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Faire une requête à l'API Oanda"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête Oanda: {e}")
            raise Exception(f"Erreur de connexion à Oanda: {str(e)}")
    
    def test_connection(self):
        """Tester la connexion et récupérer les informations du compte"""
        try:
            # Test de l'API key avec l'endpoint account
            account_info = self._make_request('GET', f'/v3/accounts/{self.account_id}')
            account = account_info.get('account', {})
            
            return {
                'success': True,
                'message': 'Connexion Oanda réussie',
                'account_info': {
                    'currency': account.get('currency'),
                    'balance': float(account.get('balance', 0)),
                    'nav': float(account.get('NAV', 0)),
                    'margin_used': float(account.get('marginUsed', 0)),
                    'margin_available': float(account.get('marginAvailable', 0)),
                    'open_positions': account.get('openPositionCount', 0),
                    'open_trades': account.get('openTradeCount', 0)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Échec de la connexion Oanda: {str(e)}'
            }
    
    def get_account_info(self):
        """Récupérer les informations détaillées du compte"""
        return self._make_request('GET', f'/v3/accounts/{self.account_id}')
    
    def get_account_summary(self):
        """Récupérer le résumé du compte"""
        return self._make_request('GET', f'/v3/accounts/{self.account_id}/summary')
    
    def get_instruments(self):
        """Récupérer la liste des instruments disponibles"""
        return self._make_request('GET', f'/v3/accounts/{self.account_id}/instruments')
    
    def get_pricing(self, instruments):
        """Récupérer les prix actuels pour une liste d'instruments"""
        if isinstance(instruments, str):
            instruments = [instruments]
        
        params = {'instruments': ','.join(instruments)}
        return self._make_request('GET', f'/v3/accounts/{self.account_id}/pricing', params=params)
    
    def get_candles(self, instrument, granularity='H1', count=100, from_time=None, to_time=None):
        """Récupérer les données de chandelles"""
        params = {
            'granularity': granularity,
            'count': count
        }
        
        if from_time:
            params['from'] = from_time
        if to_time:
            params['to'] = to_time
        
        try:
            result = self._make_request('GET', f'/v3/instruments/{instrument}/candles', params=params)
            
            # Convertir en format plus lisible
            formatted_candles = []
            for candle in result.get('candles', []):
                if candle.get('complete'):
                    mid = candle.get('mid', {})
                    formatted_candles.append({
                        'timestamp': candle['time'],
                        'open': float(mid.get('o', 0)),
                        'high': float(mid.get('h', 0)),
                        'low': float(mid.get('l', 0)),
                        'close': float(mid.get('c', 0)),
                        'volume': candle.get('volume', 0)
                    })
            
            return formatted_candles
        except Exception as e:
            logger.error(f"Erreur récupération candles {instrument}: {e}")
            return []
    
    def place_order(self, instrument, units, order_type='MARKET', price=None, stop_loss=None, take_profit=None):
        """Placer un ordre"""
        try:
            order_data = {
                'order': {
                    'type': order_type,
                    'instrument': instrument,
                    'units': str(units)  # Positif pour BUY, négatif pour SELL
                }
            }
            
            if order_type == 'LIMIT' and price:
                order_data['order']['price'] = str(price)
            
            if stop_loss:
                order_data['order']['stopLossOnFill'] = {
                    'price': str(stop_loss)
                }
            
            if take_profit:
                order_data['order']['takeProfitOnFill'] = {
                    'price': str(take_profit)
                }
            
            result = self._make_request('POST', f'/v3/accounts/{self.account_id}/orders', data=order_data)
            
            return {
                'success': True,
                'order_id': result.get('orderCreateTransaction', {}).get('id'),
                'data': result
            }
        
        except Exception as e:
            logger.error(f"Erreur placement ordre {instrument}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_orders(self, state='PENDING'):
        """Récupérer les ordres"""
        params = {'state': state}
        try:
            return self._make_request('GET', f'/v3/accounts/{self.account_id}/orders', params=params)
        except Exception as e:
            logger.error(f"Erreur récupération ordres: {e}")
            return {'orders': []}
    
    def cancel_order(self, order_id):
        """Annuler un ordre"""
        try:
            result = self._make_request('PUT', f'/v3/accounts/{self.account_id}/orders/{order_id}/cancel')
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
    
    def get_positions(self):
        """Récupérer les positions ouvertes"""
        try:
            return self._make_request('GET', f'/v3/accounts/{self.account_id}/positions')
        except Exception as e:
            logger.error(f"Erreur récupération positions: {e}")
            return {'positions': []}
    
    def get_trades(self, state='OPEN'):
        """Récupérer les trades"""
        params = {'state': state}
        try:
            return self._make_request('GET', f'/v3/accounts/{self.account_id}/trades', params=params)
        except Exception as e:
            logger.error(f"Erreur récupération trades: {e}")
            return {'trades': []}
    
    def close_trade(self, trade_id, units=None):
        """Fermer un trade"""
        try:
            data = {}
            if units:
                data['units'] = str(units)
            
            result = self._make_request('PUT', f'/v3/accounts/{self.account_id}/trades/{trade_id}/close', data=data)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            logger.error(f"Erreur fermeture trade {trade_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def test_oanda_connection(credentials):
    """Fonction helper pour tester la connexion Oanda"""
    service = OandaService(credentials)
    return service.test_connection()
