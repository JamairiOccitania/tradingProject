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
        # Retourne le premier compte qui n'est pas un compte de pratique
        for acc in r.response['accounts']:
            if 'practice' not in acc['id']:
                return acc['id']
        # Fallback - à remplacer par votre ID de compte réel
        return "YOUR_LIVE_ACCOUNT_ID"

    def get_historical_data(self, instrument, count=500, granularity='H1'):
        params = {
            'count': count,
            'granularity': granularity
        }
        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        try:
            self.client.request(r)
            return r.response
        except oandapyV20.exceptions.V20Error as e:
            print(f"Error fetching historical data: {e}")
            return None

    def get_account_summary(self):
        r = accounts.AccountSummary(accountID=self.account_id)
        try:
            self.client.request(r)
            return r.response
        except oandapyV20.exceptions.V20Error as e:
            print(f"Error fetching account summary: {e}")
            return None
