import datetime

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from ..models import Group, ClassGroup, Student, Letter

class ModelStudentTests(TestCase):

    def test_letters_with_no_results(self):
        """If there are no letters that concern a given student and have been published, do not return any."""

        # Create two classes and two groups each.
        # Test student is member of one of them respectively.

        class_a = ClassGroup(name="Class A")
        class_b = ClassGroup(name="Class B")
        group_a = Group(name="Group A")
        group_b = Group(name="Group B")
        class_a.save()
        class_b.save()
        group_a.save()
        group_b.save()

        student = Student(first_name="John", last_name="Doe", class_group=class_a)
        student.save()
        student.groups.add(group_a)

        # A letter that does not concern the student at all:
        letter_a = Letter(name="Test letter A")
        letter_a.save()
        letter_a.classes_concerned.add(class_b)
        letter_a.groups_concerned.add(group_b)

        # A letter that concerns the student's class but has not yet been published:
        letter_b = Letter(name="Test letter B", date_published=timezone.now() + datetime.timedelta(days=1))
        letter_b.save()
        letter_b.classes_concerned.add(class_a)
        letter_b.groups_concerned.add(group_b)

        # A letter that concerns both the student's class and their group but has not yet been published:
        letter_c = Letter(name="Test Letter C", date_published=timezone.now() + datetime.timedelta(days=1))
        letter_c.save()
        letter_c.classes_concerned.add(class_a)
        letter_c.groups_concerned.add(group_a)

        self.assertSetEqual(set(student.letters), set())

    def test_letters_with_one_result(self):
        """If there is one letter concerning a given student, return that one.
        Do not return two other letters that do not concern them.
        """

        # Create two classes and two groups each.
        # Test student is member of one of them respectively.

        class_a = ClassGroup(name="Class A")
        class_b = ClassGroup(name="Class B")
        group_a = Group(name="Group A")
        group_b = Group(name="Group B")
        class_a.save()
        class_b.save()
        group_a.save()
        group_b.save()

        student = Student(first_name="John", last_name="Doe", class_group=class_a)
        student.save()
        student.groups.add(group_a)

        # A letter that concerns both the student's class and group:
        letter_a = Letter(name="Test letter A")
        letter_a.save()
        letter_a.classes_concerned.add(class_a)
        letter_a.groups_concerned.add(group_a)

        # A letter that does concern both the student's class and his group but has not been published yet:
        letter_b = Letter(name="Test letter B", date_published=timezone.now() + datetime.timedelta(days=1))
        letter_b.save()
        letter_b.classes_concerned.add(class_a)
        letter_b.groups_concerned.add(group_a)

        # A letter that concerns the student's group but has not yet been published:
        letter_c = Letter(name="Test Letter C", date_published=timezone.now() + datetime.timedelta(days=1))
        letter_c.save()
        letter_c.classes_concerned.add(class_b)
        letter_c.groups_concerned.add(group_a)

        self.assertSetEqual(set(student.letters), {letter_a})

    def test_letters_with_multiple_results(self):
        """If there are two letters concerning a given student, letters returns both.
        Do not return another letter that does not concern the student.
        """

        # Create two classes and two groups each.
        # Test student is member of one of them respectively.

        class_a = ClassGroup(name="Class A")
        class_b = ClassGroup(name="Class B")
        group_a = Group(name="Group A")
        group_b = Group(name="Group B")
        class_a.save()
        class_b.save()
        group_a.save()
        group_b.save()

        student = Student(first_name="John", last_name="Doe", class_group=class_a)
        student.save()
        student.groups.add(group_a)

        # A letter that concerns the student's class and group but has not yet been published:
        letter_a = Letter(name="Test letter A", date_published=timezone.now() + datetime.timedelta(days=1))
        letter_a.save()
        letter_a.classes_concerned.add(class_a)
        letter_a.groups_concerned.add(group_a)

        # A letter that concerns the student's class but not his group:
        letter_b = Letter(name="Test letter B")
        letter_b.save()
        letter_b.classes_concerned.add(class_a)
        letter_b.groups_concerned.add(group_b)

        # A letter that concerns the student's group but not his class:
        letter_c = Letter(name="Test letter C")
        letter_c.save()
        letter_c.classes_concerned.add(class_b)
        letter_c.groups_concerned.add(group_a)

        self.assertSetEqual(set(student.letters), {letter_b, letter_c})

    def test_parents_with_no_parents(self):
        """If no user feels responsible for a given student, do not return any."""

        # Creat dummy class for the student:
        dummy_class = ClassGroup(name="Dummy Class")
        dummy_class.save()

        # Create new student:
        student = Student(first_name="John", last_name="Doe", class_group=dummy_class)
        student.save()

        # Create two users, but none of them is the student's parent:
        user_a = User(username="user_a", first_name="Some", last_name="Person", email="user_a@example.com")
        user_b = User(username="user_b", first_name="Another", last_name="Person", email="user_b@example.com")
        user_a.save()
        user_b.save()

        self.assertListEqual(student.parents, [])

    def test_parents_with_one_parent(self):
        """If one user is registered as a given student's parent, only return that user."""

        # Creat dummy class for the student:
        dummy_class = ClassGroup(name="Dummy Class")
        dummy_class.save()

        # Create new student:
        student = Student(first_name="John Jr.", last_name="Doe", class_group=dummy_class)
        student.save()

        # Create two users, but none of them is the student's parent:
        user_a = User(username="user_a", first_name="John Sr.", last_name="Doe", email="user_a@example.com")
        user_b = User(username="user_b", first_name="Another", last_name="Person", email="user_b@example.com")
        user_a.save()
        user_b.save()

        user_a.profile.children.add(student)

        self.assertListEqual(student.parents, [user_a])

    def test_parents_with_two_parents(self):
        """If two users are registered as a given student's parents, return both."""

        # Creat dummy class for the student:
        dummy_class = ClassGroup(name="Dummy Class")
        dummy_class.save()

        # Create new student:
        student = Student(first_name="John Jr.", last_name="Doe", class_group=dummy_class)
        student.save()

        # Create two users, but none of them is the student's parent:
        user_a = User(username="user_a", first_name="John Sr.", last_name="Doe", email="user_a@example.com")
        user_b = User(username="user_b", first_name="Jane", last_name="Doe", email="user_b@example.com")
        user_a.save()
        user_b.save()

        user_a.profile.children.add(student)
        user_b.profile.children.add(student)

        self.assertSetEqual(set(student.parents), {user_a, user_b})