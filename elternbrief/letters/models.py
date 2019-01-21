from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    @staticmethod
    def by_child(child):
        letters = [letter for letter in Letter.objects.filter(classes_concerned__name=child.class_group)] + \
                  [letter for letter in [Letter.objects.filter(groups_concerned__name=child.groups.all()[i])[0] for i in
                                         range(child.groups.count())]]
        return letters


class Student(models.Model):
    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    class_group = models.ForeignKey(ClassGroup, verbose_name="Klasse", on_delete=models.PROTECT)
    groups = models.ManyToManyField(Group, verbose_name="Gruppen", blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name + ", " + str(self.class_group)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    children = models.ManyToManyField(Student, verbose_name="Kinder", blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
