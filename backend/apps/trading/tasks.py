from celery import shared_task
import time
from apps.apitrading.models import Bot, TradeLog, APIKey, Backtest, BrokerCredentials
from .oanda import OandaAPI
from .strategies import rsi_sma_strategy, macd_strategy, ema_cross_strategy, STRATEGIES
from .backtester import Backtester
from apps.apitrading.utils import decrypt_key
from apps.apitrading.services.binance_service import BinanceService
from apps.apitrading.services.oanda_service import OandaService

# Map des stratégies - utilise le dictionnaire du fichier strategies.py
STRATEGY_MAP = STRATEGIES

def get_broker_service(bot):
    """Retourne le service approprié selon le broker du bot"""
    try:
        credentials = BrokerCredentials.objects.get(user=bot.user, broker=bot.broker, is_active=True)
        
        if bot.broker == 'binance':
            return BinanceService(credentials)
        elif bot.broker == 'oanda':
            return OandaService(credentials)
        else:
            raise ValueError(f"Broker non supporté: {bot.broker}")
    
    except BrokerCredentials.DoesNotExist:
        raise Exception(f"Aucun identifiant actif trouvé pour le broker {bot.broker}")

def format_market_data_for_strategy(raw_data, broker):
    """Convertit les données de marché au format attendu par les stratégies"""
    if broker == 'binance':
        # Les données Binance sont déjà au bon format
        return {'candles': raw_data}
    elif broker == 'oanda':
        # Adapter le format Oanda si nécessaire
        formatted_candles = []
        for candle in raw_data:
            formatted_candles.append({
                'time': candle['timestamp'],
                'mid': {
                    'o': str(candle['open']),
                    'h': str(candle['high']),
                    'l': str(candle['low']),
                    'c': str(candle['close'])
                },
                'volume': candle['volume']
            })
        return {'candles': formatted_candles}
    
    return raw_data

@shared_task
def run_bot_task(bot_id):
    try:
        bot = Bot.objects.get(id=bot_id)
        
        if bot.status != 'running':
            return f"Bot {bot.name} is not running. Stopping task."

        # Obtenir le service broker approprié
        broker_service = get_broker_service(bot)

        # Boucle principale du bot
        while bot.status == 'running':
            try:
                # Récupérer les données de marché selon le broker
                if bot.broker == 'binance':
                    raw_data = broker_service.get_klines(bot.asset, interval='1m', limit=100)
                elif bot.broker == 'oanda':
                    raw_data = broker_service.get_candles(bot.asset, granularity='M1', count=100)
                else:
                    raise Exception(f"Broker non supporté: {bot.broker}")
                
                if not raw_data or len(raw_data) < 50:
                    TradeLog.objects.create(
                        bot=bot, 
                        decision='ERROR', 
                        price=0, 
                        details=f'Pas assez de données historiques pour {bot.broker}'
                    )
                    time.sleep(60)
                    continue

                # Formater les données pour la stratégie
                historical_data = format_market_data_for_strategy(raw_data, bot.broker)

                # Obtenir la décision de la stratégie
                strategy_func = STRATEGY_MAP.get(bot.strategy)
                if not strategy_func:
                    bot.status = 'stopped'
                    bot.save()
                    return f"Strategy {bot.strategy} not found for bot {bot.name}."

                result = strategy_func(historical_data, bot.parameters)
                decision = result['decision']
                current_price = result['price']
                details = result['details']

                # Log de la décision
                TradeLog.objects.create(
                    bot=bot, 
                    decision=decision, 
                    price=current_price, 
                    details=f"[{bot.broker.upper()}] {details}"
                )

                # Exécuter l'ordre selon le broker
                if decision == 'BUY' or decision == 'SELL':
                    if bot.mode == 'live':
                        try:
                            if bot.broker == 'binance':
                                side = 'BUY' if decision == 'BUY' else 'SELL'
                                order_result = broker_service.place_order(
                                    symbol=bot.asset,
                                    side=side,
                                    order_type='MARKET',
                                    quantity=bot.parameters.get('position_size', 0.001)
                                )
                            elif bot.broker == 'oanda':
                                units = bot.parameters.get('position_size', 100)
                                if decision == 'SELL':
                                    units = -units
                                order_result = broker_service.place_order(
                                    instrument=bot.asset,
                                    units=units,
                                    order_type='MARKET'
                                )
                            
                            if order_result.get('success'):
                                TradeLog.objects.create(
                                    bot=bot,
                                    decision=f'{decision}_EXECUTED',
                                    price=current_price,
                                    details=f"Ordre exécuté: {order_result.get('order_id')}"
                                )
                            else:
                                TradeLog.objects.create(
                                    bot=bot,
                                    decision=f'{decision}_FAILED',
                                    price=current_price,
                                    details=f"Échec ordre: {order_result.get('error')}"
                                )
                        except Exception as e:
                            TradeLog.objects.create(
                                bot=bot,
                                decision=f'{decision}_ERROR',
                                price=current_price,
                                details=f"Erreur placement ordre: {str(e)}"
                            )

                # Re-vérifier le statut du bot depuis la DB
                bot.refresh_from_db()
                if bot.status != 'running':
                    break

                time.sleep(60)  # Attendre 1 minute avant la prochaine itération

            except Exception as e:
                TradeLog.objects.create(
                    bot=bot,
                    decision='ERROR',
                    price=0,
                    details=f"Erreur dans la boucle: {str(e)}"
                )
                time.sleep(60)  # Attendre avant de réessayer

    except Bot.DoesNotExist:
        return f"Bot with id {bot_id} not found."
    except Exception as e:
        # En cas d'erreur, arrêter le bot pour éviter les boucles infinies
        try:
            bot = Bot.objects.get(id=bot_id)
            bot.status = 'stopped'
            bot.save()
            TradeLog.objects.create(bot=bot, decision='ERROR', price=0, details=str(e))
        except:
            pass
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

        backtest.results = results
        backtest.status = 'completed'
        backtest.save()

    except Exception as e:
        if 'backtest' in locals():
            backtest.status = 'failed'
            backtest.results = {'error': str(e)}
            backtest.save()
        print(f"Backtest failed for ID {backtest_id}: {e}")

@shared_task
def test_task(message="Hello from Celery!"):
    """
    Tâche de test simple pour vérifier que Celery fonctionne
    """
    import time
    print(f"Starting test task: {message}")
    time.sleep(5)  # Simule une tâche qui prend du temps
    print(f"Test task completed: {message}")
    return f"Task completed successfully: {message}"

@shared_task
def add_numbers(x, y):
    """
    Tâche de test simple pour additionner deux nombres
    """
    result = x + y
    print(f"Adding {x} + {y} = {result}")
    return result
