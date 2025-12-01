from django.core.management.base import BaseCommand
from analytics.models import PaymentProvider

class Command(BaseCommand):
    help = 'Populates initial payment providers (Banks and Mobile Money)'

    def handle(self, *args, **kwargs):
        banks = [
            'CRDB Bank', 'NMB Bank', 'NBC Bank', 'Absa Bank Tanzania', 
            'DTB Tanzania', 'Stanbic Bank', 'Exim Bank', 'Azania Bank', 
            'TCB Bank', 'KCB Bank Tanzania'
        ]
        
        mobile_money = [
            'M-PESA', 'Mix By Yas', 'Airtel Money', 'Tigo Pesa', 'HaloPesa'
        ]

        # Add Banks
        for name in banks:
            provider, created = PaymentProvider.objects.get_or_create(
                name=name,
                defaults={'type': 'BANK'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Bank: {name}'))
            else:
                self.stdout.write(f'Bank already exists: {name}')

        # Add Mobile Money
        for name in mobile_money:
            provider, created = PaymentProvider.objects.get_or_create(
                name=name,
                defaults={'type': 'MOBILE'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Mobile Money: {name}'))
            else:
                self.stdout.write(f'Mobile Money already exists: {name}')
