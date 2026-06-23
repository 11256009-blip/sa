from django.apps import AppConfig


class BookstoreConfig(AppConfig):
    name = 'Bookstore'
    
    def ready(self):
        import Bookstore.signals  # noqa

