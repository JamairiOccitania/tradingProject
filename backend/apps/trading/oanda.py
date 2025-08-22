import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as accounts

class OandaAPI:
    def __init__(self, api_key, mode='paper'):
        self.client = oandapyV20.API(access_token=api_key)
        if mode == 'paper':
            # Pour le paper trading, OANDA utilise un compte spécifique.
            # Vous devrez peut-être trouver votre ID de compte de pratique.
            self.account_id = self._get_practice_account_id()
        else:
            # Pour le live trading, vous devrez fournir votre ID de compte principal.
            self.account_id = self._get_live_account_id()

    def _get_practice_account_id(self):
        # Logique pour trouver l'ID du compte de pratique
        # Ceci est un exemple, vous devrez peut-être l'adapter.
        r = accounts.AccountList()
        self.client.request(r)
        for acc in r.response['accounts']:
            if 'practice' in acc['id']:
                return acc['id']
        # Fallback - à remplacer par votre ID de compte de démo si la recherche échoue
        return "YOUR_PAPER_TRADING_ACCOUNT_ID"

    def _get_live_account_id(self):
        # Logique pour trouver l'ID du compte live
        r = accounts.AccountList()
        self.client.request(r)
        for acc in r.response['accounts']:
            if 'live' in acc['id']:
                return acc['id']
        # Fallback - à remplacer par votre ID de compte live si la recherche échoue
        return "YOUR_LIVE_TRADING_ACCOUNT_ID"

    def get_historical_data(self, instrument, count=100, granularity='M1'):
        # Récupère les données historiques
        r = instruments.InstrumentsCandles(instrument=instrument, params={"count": count, "granularity": granularity})
        self.client.request(r)
        return r.response

    def get_account_summary(self, account_id):
        # Récupère le résumé du compte
        r = accounts.AccountSummary(account_id)
        self.client.request(r)
        return r.response

    def place_order(self, instrument, units, order_type='MARKET'):
        # Place un ordre (simplifié)
        # En réalité, vous devrez gérer plus de paramètres comme les stops, limits, etc.
        order_data = {
            "order": {
                "type": order_type,
                "instrument": instrument,
                "units": units
            }
        }
        r = orders.OrderCreate(self.account_id, data=order_data)
        self.client.request(r)
        return r.response
