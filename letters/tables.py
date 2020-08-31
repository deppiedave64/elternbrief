"""
Tables definition for letters app of the elternbrief project.

Contains class definitions for dynamically generating tables using
the django_tables2 app.
"""

import django_tables2 as tables


class LetterResultTable(tables.Table):
    """Displays information on the students that have confirmed a given letter."""

    last_name = tables.Column(verbose_name="Nachname")
    first_name = tables.Column(verbose_name="Vorname")
    class_grp = tables.Column(verbose_name="Klasse")
    confirmed = tables.Column(verbose_name="Bestätigt?")

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {
            'class': 'table table-hover table-striped'
        }
        row_attrs = {
            'class': lambda record: 'w3-hover-indigo'
            if record['confirmed'] == "Ja" else 'w3-pale-red w3-hover-red'
        }
