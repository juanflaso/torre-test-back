from django.apps import AppConfig


class FeedConfig(AppConfig):
    name = 'feed'

    def ready(self):
        import nltk

        nltk.download('stopwords')
        nltk.download('punkt')