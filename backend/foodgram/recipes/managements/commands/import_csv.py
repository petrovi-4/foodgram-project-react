import csv
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

DATA_DIR = f'{settings.BASE_DIR}/data/'
FILE_NAME = 'ingredients.csv'


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open(f'{DATA_DIR}{FILE_NAME}') as f:
                table = csv.reader(f)
                for column in table:
                    if not Ingredient.objects.filter(
                        name=column[0], measurement_unit=column[1]
                    ).exists():
                        Ingredient.objects.create(
                            name=column[0], measurement_unit=colum[1]
                        )
            print('Import ingredient completed')
        except FileNotFoundError:
            raise FileNotFoundError(
                f'Файл {FILE_NAME} отсутствует по адресу {DATA_DIR}'
            )
