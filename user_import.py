#!/usr/bin/env python3

import os
import csv
import argparse

os.environ["DJANGO_SETTINGS_MODULE"] = "elternbrief.settings"

import django

django.setup()

from django.contrib.auth.models import User

from letters.models import Student, ClassGroup, Profile


parser = argparse.ArgumentParser(description="Import users into elternbrief from csv files.")
parser.add_argument('parents_file', metavar="PARENTS_FILE", type=str,
                    nargs=1, help="csv file containing parents data")
parser.add_argument('students_file', metavar="STUDENTS_FILE", type=str,
                    nargs=1, help="csv file containing students data")
parser.add_argument('--create-classes', dest='create_class_groups',
                    action='store_const', const=True, default=False,
                    help="create classes that do not exist "
                         "(default: don't create classes, skip students)")
args = parser.parse_args()


def read_parents(import_file: str):
    """Read csv file with parents data and return list of dictionaries.

    Return dictionary does not contain users with email addresses that already
    exist in the database.
    csv file should have the format
    <id>,<last_name>,<first_name>,<email>

    :param import_file: Relative or absolute path to csv file
    :raises ValueError: id is not a valid number
    :return: List of dictionaries containing user data
    """

    parents = []

    with open(import_file, 'r') as csvfile:
        parents_reader = csv.DictReader(csvfile, delimiter=',', fieldnames=(
            'id', 'last_name', 'first_name', 'email'))

        for row in parents_reader:
            try:
                if not User.objects.filter(email=row['email']):
                    parents.append(row)
                else:
                    print(f"{row['email']}: a user with that email already exists.")
            except ValueError:
                print(f"id {row['id']} is not a valid number!")
                continue

    return parents


def read_students(import_file: str):
    """Read csv file with students data and return list of dictionaries.

    csv file should have the format
    <last_name>,<first_name>,<class>,<id_of_parent_1>,<id_of_parent_2>

    :param import_file: Relative or absolute path to csv file
    :return: List of dictionaries containing students data
    """

    students = []

    with open(import_file, 'r') as csvfile:
        students_reader = csv.DictReader(csvfile, delimiter=',', fieldnames=(
            'last_name', 'first_name', 'class_group', 'parent_1', 'parent_2'))

        for row in students_reader:
            students.append(row)

    return students


def create_parent(parent: dict):
    """Create user from dictionary.

    Dictionary should have the keys 'id', 'last_name', 'first_name' and
    'email'.
    id is added to the profile object of the new user.

    :param parent: Dictionary containing the new user's data
    :return: True if the user was successfully created; otherwise False
    """

    new_user = User(username=parent['email'], first_name=parent['first_name'],
                    last_name=parent['last_name'], email=parent['email'])
    new_user.save()
    new_user.profile.import_id = parent['id']
    new_user.save()

    return True


def create_student(student: dict):
    """Create student from dictionary.

    If the class of the new student does not yet exist, it is only added if
    --create-classes flag is set.
    Dictionary should have the keys 'last_name', 'first_name', 'class_group',
    'parent_1' and 'parent_2'.
    The new student is registered as a child of the users with the ids of
    'parent_1' and 'parent_2'.
    First parent is mandatory, second parent is optional (may be 'None').

    :param student: Dictionary containing the new student's data
    :return: True if the student was successfully created; otherwise False
    """

    if not ClassGroup.objects.filter(name=student['class_group']):
        if args.create_class_groups:
            ClassGroup.objects.create(name=student['class_group'])
        else:
            print(f"Class group {student['class_group']} does not exist. "
                  f"Skipping student {student['first_name'] + student['last_name']}")
            return False

    class_group = ClassGroup.objects.get(name=student['class_group'])

    new_student = Student(first_name=student['first_name'],
                           last_name=student['last_name'],
                           class_group=class_group)
    new_student.save()

    profile = Profile.objects.get(import_id=student['parent_1'])
    profile.children.add(new_student)
    profile.import_id = None

    if student['parent_2'] != 'None':
        profile = Profile.objects.get(import_id=student['parent_2'])
        profile.children.add(new_student)
        profile.import_id = None

    return True

if __name__ == '__main__':
    # Make sure that paths to csv files are valid paths:
    if not os.path.exists(args.parents_file[0]):
        print(f"{args.parents_file[0]} is not a valid path!")
    if not os.path.exists(args.students_file[0]):
        print(f"{args.students_file[0]} is not a valid path!")

    print("Loading parents...")
    parents = read_parents(args.parents_file[0])
    print(f"Loaded {len(parents)} parents.")

    print("Loading students...")
    students = read_students(args.students_file[0])
    print(f"Loaded {len(students)} students.")

    # Create users:
    print("Creating users...")
    user_count = 0
    for parent in parents:
        if create_parent(parent):
            print(f"Succesfully created user {parent['email']}!")
            user_count += 1
        else:
            print(f"User {parent['email']} was not created.")
    print(f"{user_count} users created.")

    # Create students:
    print("Creating students...")
    student_count = 0
    for student in students:
        if create_student(student):
            print(f"Succesfully created student {student['first_name'] + student['last_name']}!")
            student_count += 1
        else:
            print(f"Student {student['first_name'] + student['last_name']} was not created.")
    print(f"{student_count} students created.")

    print("All done!")