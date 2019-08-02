"""Tests for the letters app of the elternbrief project."""

import datetime
from unittest.mock import MagicMock

import django
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Student, Letter, ClassGroup, Group


class LetterModelTests(TestCase):

    def test_by_student_with_right_class(self):
        """by_student() returns a letter, if the student is in the class the letter concerns."""

        test_class = ClassGroup(name="Test class")
        test_class.save()

        test_student = Student(first_name="John", last_name="Doe", class_group=test_class)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        test_letter = Letter(name="Test letter", document=test_document)
        test_letter.save()
        test_letter.classes_concerned.add(test_class)
        test_letter.save()

        self.assertIn(test_letter, Letter.by_student(test_student))

    def test_by_student_with_wrong_class(self):
        """by_student() does not return a certain letter, if the student is not in the class it concerns."""

        test_class = ClassGroup(name="Test class")
        test_class.save()

        other_test_class = ClassGroup(name="Some other test class")
        other_test_class.save()

        test_student = Student(first_name="John", last_name="Doe", class_group=test_class)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        test_letter = Letter(name="Test letter", document=test_document)
        test_letter.save()
        test_letter.classes_concerned.add(other_test_class)
        test_letter.save()

        self.assertNotIn(test_letter, Letter.by_student(test_student))

    def test_by_student_with_one_right_group(self):
        """by_student() returns a letter, if the student is in the group the letter concerns."""

        test_group = Group(name="Test group")
        test_group.save()

        test_class = ClassGroup(name="Test class")
        test_class.save()
        test_student = Student(first_name="John", last_name="Doe", class_group=test_class)
        test_student.save()
        test_student.groups.add(test_group)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        test_letter = Letter(name="Test letter", document=test_document)
        test_letter.save()
        test_letter.groups_concerned.add(test_group)
        test_letter.save()

        self.assertIn(test_letter, Letter.by_student(test_student))

    def test_by_student_with_multiple_right_groups(self):
        """by_student() returns multiple letters, if the student is in groups they concern,"""

        test_group = Group(name="Test group")
        test_group.save()
        other_test_group = Group(name="Another test group")
        other_test_group.save()

        test_class = ClassGroup(name="Test class")
        test_class.save()
        test_student = Student(first_name="John", last_name="Doe", class_group=test_class)
        test_student.save()
        test_student.groups.add(test_group)
        test_student.groups.add(other_test_group)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        test_letter = Letter(name="Test letter", document=test_document)
        test_letter.save()
        other_test_letter = Letter(name="Another test letter", document=test_document)
        other_test_letter.save()
        test_letter.groups_concerned.add(test_group)
        other_test_letter.groups_concerned.add(other_test_group)
        test_letter.save()
        other_test_letter.save()

        self.assertIn(test_letter, Letter.by_student(test_student))
        self.assertIn(other_test_letter, Letter.by_student(test_student))

    def test_by_student_with_wrong_group(self):
        """by_student() does not return a certain letter, if the student is not in the group it concerns."""

        test_group = Group(name="Test group")
        test_group.save()

        test_class = ClassGroup(name="Test class")
        test_class.save()
        test_student = Student(first_name="John", last_name="Doe", class_group=test_class)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        test_letter = Letter(name="Test letter", document=test_document)
        test_letter.save()
        test_letter.groups_concerned.add(test_group)
        test_letter.save()

        self.assertNotIn(test_letter, Letter.by_student(test_student))


class LetterViewTests(TestCase):

    def test_do_not_show_future_letters(self):
        """letter view does not show a certain letter, if its publication date is in the future."""

        test_class = ClassGroup(name="Test class")
        test_class.save()

        test_student = Student(first_name="John", last_name="Doe", class_group=test_class)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        publication_date = timezone.now() + datetime.timedelta(days=1)
        test_letter = Letter(name="Test letter", document=test_document, date_published=publication_date)
        test_letter.save()
        test_letter.classes_concerned.add(test_class)
        test_letter.save()

        test_parent = User.objects.create_user('test_parent', password='test_password')
        test_parent.profile.children.add(test_student)
        test_parent.save()

        c = Client()
        c.post('/login/', {'username': 'test_parent', 'password': 'test_password'}, follow=True)

        response = c.get("/letters/")
        self.assertNotContains(response, "Test letter")
