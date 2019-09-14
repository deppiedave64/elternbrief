"""AppConfig classes for the letters app of the elternbrief project."""

from django.apps import AppConfig


class LettersConfig(AppConfig):
    """Simple AppConfig for the letters app.

    Extends Django's default AppConfig class.
    """

    name = 'letters'
    verbose_name = "Elternbriefe"
