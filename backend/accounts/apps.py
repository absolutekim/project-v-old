from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """
        When the app starts, register the signals.
        """
        import accounts.signals  # Import the signals module and register it