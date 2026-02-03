from django.apps import AppConfig


class HmsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hmsapp'
    verbose_name = 'Health Management System'
    
    def ready(self):
        """Called when the app is ready - can be used for signals"""
        pass
