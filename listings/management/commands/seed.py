

from django.core.management.base import BaseCommand
from datetime import timedelta, date
from listings.models import Listing
from faker import Faker
import random




fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with sample listing data'

    def handle(self, *args, **kwargs):
        for _ in range(10):
            start = date.today()
            end = start + timedelta(days=random.randint(3, 30))
            Listing.objects.create(
                title=fake.sentence(),
                description=fake.text(),
                location=fake.city(),
                price_per_night=round(random.uniform(50.0, 300.0), 2),
                available_from=start,
                available_to=end
            )
        self.stdout.write(self.style.SUCCESS("Successfully seeded listings!"))
