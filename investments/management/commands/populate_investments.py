from django.core.management.base import BaseCommand
from investments.models import InvestmentProduct

class Command(BaseCommand):
    help = 'Populates the database with initial investment products'

    def handle(self, *args, **kwargs):
        # Clear existing products for a fresh start
        InvestmentProduct.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing products'))

        products = [
            {
                'name': 'NHIF Bima',
                'description': 'Secure your health and your family\'s with NHIF Health Insurance. A portion of your revenue ensures you have access to quality medical care across Tanzania whenever you need it.',
                'is_active': True
            },
            {
                'name': 'DSE Investments',
                'description': 'Grow your wealth by investing in the Dar es Salaam Stock Exchange. We help you build a portfolio of stocks and government bonds, turning your music royalties into long-term assets.',
                'is_active': True
            },
            {
                'name': 'Fixed Account',
                'description': 'Lock away your earnings for a fixed period to earn guaranteed interest. Perfect for saving towards major goals like a house, car, or studio equipment with zero risk.',
                'is_active': True
            }
        ]

        for p_data in products:
            product, created = InvestmentProduct.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'description': p_data['description'],
                    'is_active': p_data['is_active']
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
