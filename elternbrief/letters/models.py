from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import json


class Group(models.Model):
    """Just an arbitrary group of students."""
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class ClassGroup(models.Model):
    """Just a school class."""
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Letter(models.Model):
    """A letter sent to parents."""
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


class ResponseTextField(models.Model):
    """A simple text field for the response to a letter."""
    description = models.CharField("Beschreibung", max_length=200)
    optional = models.BooleanField("Optional", default=True)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)


class ResponseBoolField(models.Model):
    """A simple boolean field for the response to a letter."""
    description = models.CharField("Beschreibung", max_length=200)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)


class ResponseSelectionField(models.Model):
    """A simple selection field for the response to a letter."""
    description = models.CharField("Beschreibung", max_length=200)
    options = models.TextField("Auswahlmöglichkeiten (kommagetrennt)")
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)


class Student(models.Model):
    """A student."""
    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    class_group = models.ForeignKey(ClassGroup, verbose_name="Klasse", on_delete=models.PROTECT)
    groups = models.ManyToManyField(Group, verbose_name="Gruppen", blank=True)

    def __str__(self):
        """String representation is full name followed by class group."""
        return self.first_name + " " + self.last_name + ", " + str(self.class_group)

    @property
    def letters(self):
        """Return a list of all letters that concern this student.
        Search for letters concerning all the groups as well as the class group the student is a member of.
        Do not return a letter if its publication date is in the future."""
        time = timezone.now()
        letter_list = \
            list(Letter.objects.filter(classes_concerned__name=self.class_group, date_published__lte=time)) + \
            list(Letter.objects.filter(groups_concerned__in=self.groups.all(), date_published__lte=time))
        return letter_list


class Profile(models.Model):
    """Model that extends the attributes of the user model."""

    # Each user entity is assigned a Profile:
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # All the students a user is allowed to view letters for:
    children = models.ManyToManyField(Student, verbose_name="Kinder", blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a new Profile each time a new user is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the corresponding Profile whenever a User objects is saved to the database."""
    instance.profile.save()


class Response(models.Model):
    """The response to a letter."""
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    response_date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.student) + ", " + str(self.letter)
