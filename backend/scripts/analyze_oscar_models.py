from django.apps import apps
from oscar.core.loading import get_model
from pprint import pprint

def analyze_oscar_models():
    print('Oscar models we should inherit from:')
    oscar_models = [
        model for model in apps.get_models() 
        if 'oscar.apps' in model.__module__ and 'abstract' in model.__module__
    ]
    for model in sorted(oscar_models, key=lambda m: m.__module__):
        print(f'- {model.__name__} ({model.__module__})')

    print('\nOur custom models that should inherit from Oscar:')
    our_models = [
        model for model in apps.get_models()
        if model.__module__.startswith(('marketplace', 'crypto_payments'))
    ]
    for model in sorted(our_models, key=lambda m: m.__module__):
        print(f'- {model.__name__} ({model.__module__})')

if __name__ == '__main__':
    analyze_oscar_models()
