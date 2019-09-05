"""
Model definitions for the letters app of the elternbrief project.
"""

import json

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Group(models.Model):
    """An arbitrary group of students.

    Each group may have any number of students.
    Each student can be a member of any number of groups.
    """

    name = models.CharField("Name", max_length=30, unique=True)

    class Meta:
        verbose_name = "Gruppe"
        verbose_name_plural = "Gruppen"

    def __str__(self):
        """Return a string representation of itself.

        The string representation is determined by the name attribute.
        :return: String representation of itself
        :rtype: str
        """

        return self.name


class ClassGroup(models.Model):
    """A school class.

    Each school class can may have any number of students.
    Each student must be a member of exactly one school class.
    """

    name = models.CharField("Name", max_length=30, unique=True)

    class Meta:
        verbose_name = "Klasse"
        verbose_name_plural = "Klassen"

    def __str__(self):
        """Return string representation of itself.

        The string representation is the value of the name attribute.

        :return: String representation of itself
        :rtype: str
        """

        return self.name


class Student(models.Model):
    """A student."""

    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    class_group = models.ForeignKey(ClassGroup, verbose_name="Klasse",
                                    on_delete=models.PROTECT)
    groups = models.ManyToManyField(Group, verbose_name="Gruppen", blank=True)

    class Meta:
        verbose_name = "Schüler"
        verbose_name_plural = "Schüler"

    def __str__(self):
        """Return string representation of itself.

        The string representation is the full name followed by class group.

        :return: String representation of itself
        :rtype: str
        """

        return self.first_name + " " + self.last_name + ", " + str(
            self.class_group)

    @property
    def letters(self):
        """Return a set of all letters that concern this student.

        Return letters concerning all the groups as well as the
        class group the student is a member of.
        Do not return a letter if its publication date is in the future.

        :return: Set of all letters concerning this student
        :rtype: set
        """

        time = timezone.now()
        query = models.Q(date_published__lte=time) & (
                models.Q(classes_concerned__name=self.class_group)
                | models.Q(groups_concerned__in=self.groups.all())
        )

        return set(Letter.objects.filter(query))

    @property
    def parents(self):
        """Return list of parents of this student.

        :return: List of parents of this student
        :rtype: list
        """

        return list(User.objects.filter(profile__children=self))


class Letter(models.Model):
    """A letter sent to parents.

    A letter object contains information on what should be displayed
    to parents viewing the letter.
    What fields are available when creating a response is determined
    by adding ResponseFields to a letter.
    """

    name = models.CharField("Name", max_length=30)
    date_published = models.DateField("Veröffentlichungsdatum",
                                      default=timezone.now)
    date_due = models.DateField("Fällig bis", blank=True, null=True)
    teacher = models.CharField("Zuständige Lehrkraft", max_length=30,
                               blank=True)
    confirmation = models.BooleanField("Muss bestätigt werden", default=True)
    groups_concerned = models.ManyToManyField(Group,
                                              verbose_name="Betroffene Gruppen",
                                              blank=True)
    classes_concerned = models.ManyToManyField(ClassGroup,
                                               verbose_name="Betroffene Klassen",
                                               blank=True)
    document = models.FileField("Dokument", upload_to='documents/%Y/%m/%d/')
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,
                                   editable=False)
    students_viewed = models.ManyToManyField(Student, editable=False,
                                             related_name="letters_viewed")
    students_acknowledged = models.ManyToManyField(Student, through='Response',
                                                   related_name="letters_acknowledged")

    class Meta:
        verbose_name = "Brief"
        verbose_name_plural = "Briefe"

    def __str__(self):
        """Return String representation of itself.

        The string representation is the value of the name attribute.

        :return: String representation of itself
        :rtype: str
        """

        return self.name

    @property
    def students(self):
        """Return all students that are concerned by this letter.

        Return set of all Student objects that are in a class group or
        a group concerned by this letter.

        :return: Set of all Student objects concerned by this letter
        :rtype: set
        """

        query = models.Q(class_group__in=self.classes_concerned.all()) \
                | models.Q(groups__in=self.groups_concerned.all())

        return set(Student.objects.filter(query))

    @property
    def students_confirmed(self):
        """Return all students whose parents have acknowledged this letter.

        Return set of all Student objects for which there exists a
        Response object that is related to that student and this letter.

        :return: Set of all Student objects that have acknowledged this letter
        :rtype: set
        """

        return set(self.students_acknowledged.all())

    @property
    def students_not_confirmed(self):
        """Return all students whose parents have not acknowledged this letter.

        Return set of all Student objects that are concerned by this
        letter for which there exists no Response object that is related
        to that student and this letter.

        :return: Set of Student objects that have not acknowledged this letter
        :rtype: set
        """

        return self.students - self.students_confirmed


class ResponseTextField(models.Model):
    """Text field for the response to a letter.

    Each letter may have up to one ResponseTextField.
    It allows for parents to enter a arbitrary message when
    confirming a letter.
    """

    description = models.CharField("Beschreibung", max_length=200)
    optional = models.BooleanField("Optional", default=True)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)

    @property
    def name(self):
        """Return unique name of this object.

        Name follow the format 'textfield-<id>'.

        :return: Unique name of this object
        :rtype: str
        """

        return f"textfield-{self.id}"

    def __str__(self):
        """Return string representation of itself.

        String representation is this object's unique name.

        :return: String representation of this object
        :rtype: str
        """

        return self.name


class ResponseBoolField(models.Model):
    """A simple boolean field for the response to a letter."""
    description = models.CharField("Beschreibung", max_length=200)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    must_be_true = models.BooleanField("Muss ausgewählt werden", default=False)

    class Meta:
        verbose_name = "Kontrollbox"
        verbose_name_plural = "Kontrollboxen"

    @property
    def name(self):
        """Return unique name of this object.

        Name follow the format 'boolfield-<id>'.

        :return: Unique name of this object
        :rtype: str
        """

        return f"boolfield-{self.id}"

    def __str__(self):
        """Return string representation of itself.

        String representation is this object's unique name.

        :return: String representation of this object
        :rtype: str
        """

        return self.name


class ResponseSelectionField(models.Model):
    """A simple selection field for the response to a letter."""
    description = models.CharField("Beschreibung", max_length=200)
    options = models.TextField("Auswahlmöglichkeiten (kommagetrennt)")
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Auswahlfeld"
        verbose_name_plural = "Auswahlfelder"

    @property
    def name(self):
        """Return unique name of this object.

        Name follow the format 'selectionfield-<id>'.

        :return: Unique name of this object
        :rtype: str
        """

        return f"selectionfield-{self.id}"

    @property
    def options_list(self):
        """Return list of all options of this ResponseSelectionField.

        Return a list of string representing the options available
        to a user when filling out this response field.

        :return: List of all options of this ResponseSelectionField
        :rtype: list
        """

        return [i.strip() for i in self.options.split(",")]

    def __str__(self):
        """Return string representation of itself.

        String representation is this object's unique name.

        :return: String representation of this object
        :rtype: str
        """

        return self.name


class Profile(models.Model):
    """Proxy model for the user model.

    Each Profile object is linked to exactly one user.
    The profile model provides additional information about users.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # All the students a user is allowed to view letters for:
    children = models.ManyToManyField(Student, verbose_name="Kinder",
                                      blank=True)
    # ID used for mass importing users from csv:
    import_id = models.IntegerField(blank=True, editable=False, null=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profile"

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """Creates a new Profile object.

        Called automatically each time a User object is saved.
        Only create a new Profile object if the User object has just
        been created.
        """

        if created:
            Profile.objects.create(user=instance)

    @staticmethod
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        """Save a user's Profile object to the database.

        Called automatically each time a User object is saved.
        """

        instance.profile.save()


class Response(models.Model):
    """Response to a letter.

    A response object holds the information a parent submits when
    confirming a letter.
    If there are any, it also holds the values parents filled in
    a letter's response fields.
    """

    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    response_date = models.DateField(default=timezone.now)
    # Values submitted by parents, encoded as JSON:
    content = models.TextField(default='{}')

    def as_dict(self):
        """Return a dictionary containing this responses content.

        Return a dictionary that is ready to be used to fill a row in
        a table in the results view.
        The dictionary always contains the following key value pairs
        with information about its student:
        'last_name', 'first_name', 'class_grp'
        The value of the 'confirmed' should be a human-readable string
        saying 'yes' in the users language.
        Additionally there's a key for every response field of this
        response's letter, with the corresponding value being whatever
        the parents filled in that field.

        :return: Dictionary containing this response's content
        :rtype: dict
        """

        try:
            response_content = json.loads(self.content)
        except json.JSONDecodeError:
            return "Response content broken. Please contact admin."

        data = {
            'last_name': self.student.last_name,
            'first_name': self.student.first_name,
            'class_grp': self.student.class_group,
            'confirmed': "Ja"
        }

        for field in self.letter.responseboolfield_set.all():
            data.update(
                {field.name: "Ja" if response_content[field.name] else "Nein"})
        for field in self.letter.responseselectionfield_set.all():
            data.update({field.name: response_content[field.name]})

        return data
