from django.apps import apps
from oscar.core.loading import get_model
from pprint import pprint

def analyze_models():
    print('Oscar models available:')
    for model in apps.get_models():
        if 'oscar' in model.__module__:
            print(f'- {model.__name__} ({model.__module__})')

    print('\nOur models:')
    for model in apps.get_models():
        if model.__module__.startswith('marketplace') or model.__module__.startswith('crypto_payments'):
            print(f'- {model.__name__} ({model.__module__})')

if __name__ == '__main__':
    analyze_models()
