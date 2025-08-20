from celery import shared_task
import time
from apitrading.models import Bot, TradeLog, APIKey, Backtest
from .oanda import OandaAPI
from .strategies import rsi_sma_strategy
from .backtester import Backtester
from apitrading.utils import decrypt_key

# Map des stratégies
STRATEGY_MAP = {
    'RSI_SMA': rsi_sma_strategy,
}

@shared_task
def run_bot_task(bot_id):
    try:
        bot = Bot.objects.get(id=bot_id)
        api_key_obj = APIKey.objects.get(user=bot.user)
        api = OandaAPI(api_key_obj.get_decrypted_key(), bot.mode)

        if bot.status != 'running':
            return f"Bot {bot.name} is not running. Stopping task."

        # Boucle principale du bot
        while bot.status == 'running':
            # Récupérer les données de marché
            # Note: OANDA peut nécessiter des ajustements sur les params (count, granularity)
            historical_data = api.get_historical_data(bot.asset, count=100, granularity='M1')
            
            if not historical_data or 'candles' not in historical_data or len(historical_data['candles']) < 50:
                TradeLog.objects.create(bot=bot, decision='ERROR', price=0, details='Not enough historical data.')
                time.sleep(60) # Attendre avant de réessayer
                continue

            # Obtenir la décision de la stratégie
            strategy_func = STRATEGY_MAP.get(bot.strategy)
            if not strategy_func:
                bot.status = 'stopped'
                bot.save()
                return f"Strategy {bot.strategy} not found for bot {bot.name}."

            result = strategy_func(historical_data, bot.parameters)
            decision = result['decision']
            current_price = result['current_price']
            details = f"RSI: {result['rsi']:.2f}, SMA: {result['sma']:.2f}"

            # Log de la décision
            TradeLog.objects.create(bot=bot, decision=decision, price=current_price, details=details)

            # Exécuter l'ordre (simplifié)
            if decision == 'BUY' or decision == 'SELL':
                # Ici, vous ajouteriez la logique pour créer un ordre via OANDA API
                # api.create_order(...) 
                pass

            # Re-vérifier le statut du bot depuis la DB
            bot.refresh_from_db()
            if bot.status != 'running':
                break

            time.sleep(60) # Attendre 1 minute avant la prochaine itération

    except Bot.DoesNotExist:
        return f"Bot with id {bot_id} not found."
    except Exception as e:
        # En cas d'erreur, arrêter le bot pour éviter les boucles infinies
        bot = Bot.objects.get(id=bot_id)
        bot.status = 'stopped'
        bot.save()
        TradeLog.objects.create(bot=bot, decision='ERROR', price=0, details=str(e))
        return f"Error running bot {bot_id}: {e}"

@shared_task
def stop_bot_task(task_id):
    # Cette fonction est un placeholder. L'arrêt se fait en changeant le statut dans la DB.
    # Celery ne fournit pas un moyen simple et fiable d'arrêter une tâche de l'extérieur.
    # La boucle dans `run_bot_task` vérifiera le statut et s'arrêtera d'elle-même.
    print(f"Attempting to stop task related to Celery ID {task_id}. Bot status should be updated in DB.")
    return

@shared_task
def run_backtest_task(backtest_id):
    try:
        backtest = Backtest.objects.get(id=backtest_id)
        backtest.status = 'running'
        backtest.save()

        user = backtest.user
        api_key_instance = APIKey.objects.get(user=user)
        decrypted_key = decrypt_key(api_key_instance.oanda_api_key.encode())

        backtester = Backtester(
            api_key=decrypted_key,
            account_id=api_key_instance.oanda_account_id,
            asset=backtest.asset,
            start_date=backtest.start_date,
            end_date=backtest.end_date,
            strategy_name=backtest.strategy,
            params=backtest.parameters
        )

        results = backtester.run()

        backtest.result = results
        backtest.status = 'completed'
        backtest.save()

    except Exception as e:
        if 'backtest' in locals():
            backtest.status = 'failed'
            backtest.result = {'error': str(e)}
            backtest.save()
        print(f"Backtest failed for ID {backtest_id}: {e}")
