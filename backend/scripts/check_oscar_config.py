from django.apps import apps
from oscar.core.loading import get_model
from pprint import pprint

def check_oscar_config():
    print('Oscar apps:')
    oscar_apps = [app for app in apps.get_app_configs() if 'oscar' in app.name]
    for app in oscar_apps:
        print(f'- {app.name}')
        
    print('\nOscar models:')
    oscar_models = [model for model in apps.get_models() if 'oscar' in model.__module__]
    for model in oscar_models:
        print(f'- {model.__name__} ({model.__module__})')

if __name__ == '__main__':
    check_oscar_config()
