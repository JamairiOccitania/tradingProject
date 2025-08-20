import os
from celery import Celery

# Définir le module de settings de Django pour le programme 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')

app = Celery('trading_platform')

# Utiliser une chaîne de caractères ici signifie que le worker n'a pas besoin de sérialiser
# l'objet de configuration pour les process enfants.
# - namespace='CELERY' signifie que toutes les clés de configuration de Celery
#   doivent avoir un préfixe `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger les modules de tâches de toutes les applications Django enregistrées.
app.autodiscover_tasks()
