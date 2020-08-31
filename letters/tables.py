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
            'class': lambda record: 'table-success' if record['confirmed'] == "Ja" else "table-danger"
        }


class UserImportParentsTable(tables.Table):
    """Displays all the users that have been created via the user import feature."""

    id = tables.Column(verbose_name="ID")
    last_name = tables.Column(verbose_name="Nachname")
    first_name = tables.Column(verbose_name="Vorname")
    email = tables.Column(verbose_name="E-Mail")

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {
            'class': 'table table-hover table-striped px-5'
        }


class UserImportStudentsTable(tables.Table):
    """Displays all the students that have been created via the user import feature."""
    last_name = tables.Column(verbose_name="Nachname")
    first_name = tables.Column(verbose_name="Vorname")
    class_group = tables.Column(verbose_name="Klasse")
    parent_1 = tables.Column(verbose_name="Elternteil 1")
    parent_2 = tables.Column(verbose_name="Elternteil 2")

    class Meta:
        template_name = 'django_tables2/bootstrap-responsive.html'
        attrs = {
            'class': 'table table-hover table-striped px-5'
        }
