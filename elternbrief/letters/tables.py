import django_tables2 as tables
from .models import Response


class LetterResultTable(tables.Table):
    last_name = tables.Column(verbose_name="Nachname")
    first_name = tables.Column(verbose_name="Vorname")
    class_grp = tables.Column(verbose_name="Klasse")
    confirmed = tables.Column(verbose_name="Bestätigt?")

    class Meta:
        template_name = 'django_tables2/bootstrap4.html'
        attrs = {
            'class': 'w3-table-all'
        }
        row_attrs = {
            'class': lambda record: 'w3-hover-indigo' if record['confirmed'] == "Ja" else 'w3-pale-red w3-hover-red'
        }
