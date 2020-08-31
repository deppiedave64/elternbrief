"""Backend logic for validating and importing new users and students from csv files."""

import csv
import io
import re

from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User

from letters.models import Student, ClassGroup, Profile


class UserImportError(Exception):
    def __init__(self, location, message):
        self.location = location
        self.message = f"In {location}: " + message
        super().__init__(self.message)


class UserAlreadyExistsError(UserImportError):
    def __init__(self, email, location="unbekannt"):
        self.email = email
        self.location = location
        self.message = f"Nutzer mit E-Mail {email} existiert bereits."
        super().__init__(self.location, self.message)


class StudentAlreadyExistsError(UserImportError):
    def __init__(self, student, location="unbekannt"):
        self.student = student
        self.location = location
        self.message = f"Schüler {student} existiert bereits."
        super().__init__(self.location, self.message)


class InvalidIDError(UserImportError):
    def __init__(self, id_number, location="unbekannt"):
        self.id = id_number
        self.location = location
        self.message = f"{id_number} ist keine gültige ID."
        super().__init__(self.location, self.message)


class UnknownIDError(UserImportError):
    def __init__(self, id_number, location="unbekannt"):
        self.id = id_number
        self.location = location
        self.message = f"Nutzer mit ID {id_number} existiert nicht."
        super().__init__(self.location, self.message)


class TooFewFieldsError(UserImportError):
    def __init__(self, row, location="unbekannt"):
        self.row = row
        self.location = location
        self.message = f"CSV-Zeile enthält zu wenig Felder: \n {row}"
        super().__init__(self.location, self.message)


class InvalidEmailError(UserImportError):
    def __init__(self, email, location="unbekannt"):
        self.email = email
        self.location = location
        self.message = f"{email} ist keine gültige Email-Adresse."
        super().__init__(self.location, self.message)


def read_parents(import_file: UploadedFile):
    """Read csv file with parents data and return list of dictionaries.

    csv file should have the format
    <id>,<last_name>,<first_name>,<email>

    Raise an exception if any field in a row does not contain valid data, or the given user already exists.

    :param import_file: UploadedFile object wrapping a csv file (must be UTF-8 encoded)
    :raises UnicodeError: csv file is not UTF-8 encoded
    :raises TooFewFieldsError: line does not contain enough fields
    :raises ValueError: id is not a valid number
    :raises UserAlreadyExistsError: A user with that mail address already exists
    :raises InvalidEmailError: Mail address is not valid
    :return: List of dictionaries containing user data
    """

    parents = []

    # Convert input file to text stream parse it as csv:
    import_file.seek(0)  # Move file pointer to beginning, in case file has already been read from
    try:
        parents_reader = csv.DictReader(io.StringIO(import_file.read().decode('utf-8')), delimiter=',',
                                        fieldnames=('id', 'last_name', 'first_name', 'email'))
    except UnicodeError as e:
        raise UserImportError(import_file.name, str(e))

    # Precompile regular expression for validating mail addresses:
    email_regex = re.compile(r"^\w+(\.\w+)*[@]\w+(\.\w+)+$", flags=re.A)

    for line_count, row in enumerate(parents_reader, start=1):
        # Make sure that all fields contain data:
        if None in row.values():
            raise TooFewFieldsError(row, f"{import_file.name}:{line_count}")

        # Make sure that id is a valid integer:
        try:
            int(row['id'])
        except ValueError:
            raise InvalidIDError(row['id'], f"{import_file.name}:{line_count}")

        # Check whether user with given email already exists:
        if User.objects.filter(email=row['email']):
            raise UserAlreadyExistsError(row['email'], f"{import_file.name}:{line_count}")

        # Make sure that mail address is valid:
        # if not re.fullmatch(r"^\w+(\.\w+)*[@]\w+(\.\w+)+$", row['email']):
        # print(row['email'], type(row['email']), email_regex.match(row['email']), email_regex.pattern)
        # raise InvalidEmailError(row['email'], f"{import_file.name}:{line_count}")

        parents.append(row)

    return parents


def read_students(import_file: UploadedFile):
    """Read csv file with students data and return list of dictionaries.

    csv file should have the format
    <last_name>,<first_name>,<class>,<id_of_parent_1>,<id_of_parent_2>

    Raise an exception if any field in a row does not contain valid data, or if that student already exists.

    :param import_file: Relative or absolute path to csv file
    :return: List of dictionaries containing students data
    """

    students = []

    # Convert input file to text stream parse it as csv:
    import_file.seek(0)  # Move file pointer to beginning, in case file has already been read from
    try:
        students_reader = csv.DictReader(io.StringIO(import_file.read().decode('utf-8')), delimiter=',',
                                         fieldnames=('last_name', 'first_name', 'class_group', 'parent_1', 'parent_2'))
    except UnicodeError as e:
        raise UserImportError(import_file.name, str(e))

    for line_count, row in enumerate(students_reader, start=1):
        # Remove parent_2 field if there is only one parent for that student:
        if row['parent_2'] is None:
            del row['parent_2']

        # Make sure that all remaining fields contain data:
        if None in row.values():
            raise TooFewFieldsError(row, f"{import_file.name}:{line_count}")

        # Make sure that id of parent_1 is valid and there is a user with that import_id:
        try:
            if not User.objects.filter(profile__import_id=int(row['parent_1'])):
                raise UnknownIDError(row['parent_1'], f"{import_file.name}:{line_count}")
        except ValueError:
            raise InvalidIDError(row['parent_1'], f"{import_file.name}:{line_count}")

        # If there is a parent_2, make sure that their id is valid and there is a user with that import_id:
        if 'parent_2' in row.keys():
            try:
                if not User.objects.filter(profile__import_id=int(row['parent_2'])):
                    raise UnknownIDError(row['parent_2'], f"{import_file.name}:{line_count}")
            except ValueError:
                raise InvalidIDError(row['parent_2'], f"{import_file.name}:{line_count}")

        # Make sure that this student does not already exist:
        if Student.objects.filter(last_name=row['last_name'], first_name=row['first_name'],
                                  class_group__name=row['class_group']):
            raise StudentAlreadyExistsError(f"{row['first_name']} {row['last_name']}, {row['class_group']}",
                                            f"{import_file.name}:{line_count}")

        students.append(row)

    return students


def create_parent(parent: dict):
    """Create user from dictionary.

    Dictionary should have the keys 'id', 'last_name', 'first_name' and
    'email'.
    id is added to the profile object of the new user.

    :param parent: Dictionary containing the new user's data
    """

    new_user = User(username=parent['email'], first_name=parent['first_name'],
                    last_name=parent['last_name'], email=parent['email'])
    new_user.save()
    new_user.profile.import_id = parent['id']
    new_user.save()


def create_student(student: dict):
    """Create student from dictionary.

    Dictionary should have the keys 'last_name', 'first_name', 'class_group',
    'parent_1' and 'parent_2'.
    The new student is registered as a child of the users with the ids of
    'parent_1' and 'parent_2'.
    First parent is mandatory, second parent is optional.

    :param student: Dictionary containing the new student's data
    :return: True if the student was successfully created; otherwise False
    """

    if not ClassGroup.objects.filter(name=student['class_group']):
        ClassGroup.objects.create(name=student['class_group'])

    class_group = ClassGroup.objects.get(name=student['class_group'])

    new_student = Student(first_name=student['first_name'],
                          last_name=student['last_name'],
                          class_group=class_group)
    new_student.save()

    profile = Profile.objects.get(import_id=student['parent_1'])
    profile.children.add(new_student)
    profile.import_id = None

    if 'parent_2' in student.keys():
        profile = Profile.objects.get(import_id=student['parent_2'])
        profile.children.add(new_student)
        profile.import_id = None
