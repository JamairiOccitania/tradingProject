import requests
import json
import logging
from datetime import datetime, timedelta
import base64

logger = logging.getLogger(__name__)

class IGService:
    def __init__(self, credentials):
        self.api_key = credentials.get_decrypted_api_key()
        self.username = credentials.account_id  # Username IG
        self.password = credentials.get_decrypted_api_secret()  # Password IG
        self.demo = getattr(credentials, 'testnet', True)  # Demo par défaut
        
        if self.demo:
            self.base_url = "https://demo-api.ig.com/gateway/deal"
        else:
            self.base_url = "https://api.ig.com/gateway/deal"
        
        self.session_token = None
        self.cst_token = None
        self.account_id = None
        
    def _get_headers(self, version="1", authenticated=False):
        """Générer les headers pour les requêtes IG"""
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json; charset=UTF-8',
            'VERSION': version,
            'X-IG-API-KEY': self.api_key
        }
        
        if authenticated and self.session_token and self.cst_token:
            headers['X-SECURITY-TOKEN'] = self.session_token
            headers['CST'] = self.cst_token
            
        return headers
    
    def authenticate(self):
        """S'authentifier auprès de l'API IG"""
        try:
            url = f"{self.base_url}/session"
            headers = self._get_headers(version="2")
            
            data = {
                "identifier": self.username,
                "password": self.password
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            # Récupérer les tokens d'authentification
            self.session_token = response.headers.get('X-SECURITY-TOKEN')
            self.cst_token = response.headers.get('CST')
            
            result = response.json()
            self.account_id = result.get('currentAccountId')
            
            return {
                'success': True,
                'message': 'Authentification IG réussie',
                'account_id': self.account_id
            }
            
        except Exception as e:
            logger.error(f"Erreur authentification IG: {e}")
            return {
                'success': False,
                'message': f'Échec de l\'authentification IG: {str(e)}'
            }
    
    def _make_request(self, method, endpoint, data=None, version="1"):
        """Faire une requête authentifiée à l'API IG"""
        # S'assurer d'être authentifié
        if not self.session_token:
            auth_result = self.authenticate()
            if not auth_result['success']:
                raise Exception(f"Échec de l'authentification: {auth_result['message']}")
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(version=version, authenticated=True)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=data, timeout=10)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête IG: {e}")
            raise Exception(f"Erreur de connexion à IG: {str(e)}")
    
    def test_connection(self):
        """Tester la connexion et récupérer les informations du compte"""
        try:
            # Authentification
            auth_result = self.authenticate()
            if not auth_result['success']:
                return auth_result
            
            # Récupérer les informations du compte
            accounts = self._make_request('GET', '/accounts')
            
            current_account = None
            for account in accounts.get('accounts', []):
                if account['accountId'] == self.account_id:
                    current_account = account
                    break
            
            if current_account:
                return {
                    'success': True,
                    'message': 'Connexion IG réussie',
                    'account_info': {
                        'account_id': current_account['accountId'],
                        'account_name': current_account['accountName'],
                        'currency': current_account['currency'],
                        'balance': float(current_account.get('balance', {}).get('balance', 0)),
                        'available': float(current_account.get('balance', {}).get('available', 0)),
                        'deposit': float(current_account.get('balance', {}).get('deposit', 0)),
                        'profit_loss': float(current_account.get('balance', {}).get('profitLoss', 0))
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Compte non trouvé'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Échec de la connexion IG: {str(e)}'
            }
    
    def get_account_info(self):
        """Récupérer les informations détaillées du compte"""
        return self._make_request('GET', '/accounts')
    
    def search_markets(self, search_term):
        """Rechercher des marchés"""
        try:
            endpoint = f"/markets?searchTerm={search_term}"
            return self._make_request('GET', endpoint)
        except Exception as e:
            logger.error(f"Erreur recherche marchés {search_term}: {e}")
            return {'markets': []}
    
    def get_market_details(self, epic):
        """Récupérer les détails d'un marché"""
        try:
            return self._make_request('GET', f'/markets/{epic}', version="3")
        except Exception as e:
            logger.error(f"Erreur récupération détails marché {epic}: {e}")
            return None
    
    def get_prices(self, epics):
        """Récupérer les prix actuels pour une liste d'epics"""
        if isinstance(epics, str):
            epics = [epics]
        
        try:
            epic_list = ','.join(epics)
            return self._make_request('GET', f'/markets?epics={epic_list}')
        except Exception as e:
            logger.error(f"Erreur récupération prix: {e}")
            return {'marketDetails': []}
    
    def get_historical_prices(self, epic, resolution='HOUR', max_points=100, from_date=None, to_date=None):
        """Récupérer les données historiques"""
        try:
            endpoint = f'/prices/{epic}'
            params = []
            
            if resolution:
                params.append(f'resolution={resolution}')
            if max_points:
                params.append(f'max={max_points}')
            if from_date:
                params.append(f'from={from_date}')
            if to_date:
                params.append(f'to={to_date}')
            
            if params:
                endpoint += '?' + '&'.join(params)
            
            result = self._make_request('GET', endpoint, version="3")
            
            # Convertir en format standardisé
            formatted_prices = []
            for price in result.get('prices', []):
                if price.get('closePrice'):
                    formatted_prices.append({
                        'timestamp': price['snapshotTime'],
                        'open': float(price['openPrice']['bid']),
                        'high': float(price['highPrice']['bid']),
                        'low': float(price['lowPrice']['bid']),
                        'close': float(price['closePrice']['bid']),
                        'volume': price.get('lastTradedVolume', 0)
                    })
            
            return formatted_prices
            
        except Exception as e:
            logger.error(f"Erreur récupération données historiques {epic}: {e}")
            return []
    
    def place_order(self, epic, direction, size, order_type='MARKET', level=None, stop_level=None, limit_level=None):
        """Placer un ordre"""
        try:
            order_data = {
                'epic': epic,
                'expiry': '-',  # DFB (Daily Funded Bet)
                'direction': direction.upper(),  # BUY ou SELL
                'size': str(size),
                'orderType': order_type.upper(),
                'timeInForce': 'FILL_OR_KILL',
                'guaranteedStop': False,
                'forceOpen': True
            }
            
            if order_type.upper() == 'LIMIT' and level:
                order_data['level'] = str(level)
            
            if stop_level:
                order_data['stopLevel'] = str(stop_level)
            
            if limit_level:
                order_data['limitLevel'] = str(limit_level)
            
            result = self._make_request('POST', '/positions/otc', data=order_data, version="2")
            
            return {
                'success': True,
                'deal_reference': result.get('dealReference'),
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Erreur placement ordre {epic}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_positions(self):
        """Récupérer les positions ouvertes"""
        try:
            return self._make_request('GET', '/positions', version="2")
        except Exception as e:
            logger.error(f"Erreur récupération positions: {e}")
            return {'positions': []}
    
    def close_position(self, deal_id, direction, size):
        """Fermer une position"""
        try:
            close_data = {
                'dealId': deal_id,
                'direction': direction.upper(),  # Opposé à la position ouverte
                'size': str(size),
                'orderType': 'MARKET',
                'timeInForce': 'FILL_OR_KILL'
            }
            
            result = self._make_request('DELETE', '/positions/otc', data=close_data, version="1")
            
            return {
                'success': True,
                'deal_reference': result.get('dealReference'),
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Erreur fermeture position {deal_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_working_orders(self):
        """Récupérer les ordres en attente"""
        try:
            return self._make_request('GET', '/workingorders', version="2")
        except Exception as e:
            logger.error(f"Erreur récupération ordres: {e}")
            return {'workingOrders': []}
    
    def cancel_order(self, deal_id):
        """Annuler un ordre en attente"""
        try:
            result = self._make_request('DELETE', f'/workingorders/otc/{deal_id}', version="2")
            return {
                'success': True,
                'deal_reference': result.get('dealReference'),
                'data': result
            }
        except Exception as e:
            logger.error(f"Erreur annulation ordre {deal_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_deal_confirmation(self, deal_reference):
        """Vérifier le statut d'un deal"""
        try:
            return self._make_request('GET', f'/confirms/{deal_reference}')
        except Exception as e:
            logger.error(f"Erreur confirmation deal {deal_reference}: {e}")
            return None

def test_ig_connection(credentials):
    """Fonction helper pour tester la connexion IG"""
    service = IGService(credentials)
    return service.test_connection()
