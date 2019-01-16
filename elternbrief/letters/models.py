from django.db import models
from django.utils import timezone
from django.conf import settings


class Group(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class ClassGroup(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Letter(models.Model):
    name = models.CharField(max_length=30)
    date_published = models.DateField("Veröffentlichungsdatum", default=timezone.now)
    date_due = models.DateField("Fällig bis", blank=True, null=True)
    teacher = models.CharField("Zuständige Lehrkraft", max_length=30, blank=True)
    confirmation = models.BooleanField("Muss bestätigt werden", default=True)
    groups_concerned = models.ManyToManyField(Group, blank=True)
    classes_concerned = models.ManyToManyField(ClassGroup, blank=True)
    document = models.FileField(upload_to='documents/%Y/%m/%d/')

    def __str__(self):
        return self.name


class Student(models.Model):
    parents = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="Erziehungsberechtigte", blank=True)
    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    class_group = models.ForeignKey(ClassGroup, verbose_name="Klasse", on_delete=models.PROTECT)
    groups = models.ManyToManyField(Group, verbose_name="Gruppen", blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name + ", " + str(self.class_group)
