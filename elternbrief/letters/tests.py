import django
from django.test import TestCase
from unittest.mock import MagicMock

from .models import Student, Letter, ClassGroup

class LetterModelTests(TestCase):

    def test_by_student_with_right_class(self):
        """ by_student() returns a letter, if the student is in the class the letter concerns."""

        test_class_group = ClassGroup(name="Test class")
        test_class_group.save()
        test_student = Student(first_name="John", last_name="Doe", class_group=test_class_group)
        test_student.save()

        test_document = MagicMock(spec=django.core.files.File, name="Test document")
        test_document.name = 'test.pdf'

        test_letter = Letter(name="Test letter", document=test_document)
        test_letter.save()
        test_letter.classes_concerned.add(test_class_group)
        test_letter.save()

        self.assertIn(test_letter, Letter.by_student(test_student))