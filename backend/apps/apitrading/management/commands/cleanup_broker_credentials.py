from django.core.management.base import BaseCommand
from apps.apitrading.models import BrokerCredentials

class Command(BaseCommand):
    help = 'Nettoie les enregistrements BrokerCredentials corrompus'

    def handle(self, *args, **options):
        self.stdout.write('Début du nettoyage des identifiants broker corrompus...')
        
        total_count = BrokerCredentials.objects.count()
        corrupted_count = 0
        
        for cred in BrokerCredentials.objects.all():
            try:
                # Tester le déchiffrement
                cred.get_decrypted_api_key()
                if cred.encrypted_api_secret:
                    cred.get_decrypted_api_secret()
                self.stdout.write(f'✓ Identifiant {cred.id} ({cred.broker}) OK')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'✗ Suppression identifiant corrompu {cred.id} ({cred.broker}): {e}'
                    )
                )
                cred.delete()
                corrupted_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Nettoyage terminé. {corrupted_count}/{total_count} enregistrements corrompus supprimés.'
            )
        )
