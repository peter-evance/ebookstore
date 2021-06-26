from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        '''Ensures the signals are register at each instances of requests - 
        handlers will be called for every new book image uploaded.'''
        from . import signals
