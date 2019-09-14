"""View definitions for the letters app of the elternbrief project."""

import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as dj_login, \
    logout as dj_logout
from django_tables2 import RequestConfig, Column

from .models import Letter, Student, Response
from .tables import LetterResultTable


def index(request):
    """Render the start page.

    :param request: Current request
    :return: Start page
    """

    return render(request, 'letters/index.html')


def letters(request):
    """Render overview of available letters.

    If user is  staff member, show all letters that user created.
    If user i no staff member, show all letters concerning the children
    of that user.
    If user is not logged in, show error message and redirect to index.

    :param request: Current request
    :return: Letters overview page
    """

    # Show special page if user is staff member:
    if request.user.is_staff:
        letters_list = Letter.objects.filter(created_by=request.user)
        context = {
            'letters': letters_list
        }

        return render(request, 'letters/letters_index_staff.html', context)

    # Only show page if user is logged in:
    elif request.user.is_authenticated:
        # Make sure that the User has an associated Profile object:
        if hasattr(request.user, 'profile'):
            # Retrieve list of all students the user is allowed to view letters for:
            children_list = request.user.profile.children.all()
            context = {
                'children_list': children_list,
                # Dictionary of ids of all children and the letters that concern them:
                'letters': {child.id: child.letters for child in children_list}
            }

            return render(request, 'letters/letters_index.html', context)

        else:
            # Show error message if the User has now associated Profile object:
            messages.error(request,
                           "Sie sind mit einem Nutzer eingeloggt, \
                           der nicht vollständig registriert ist!")

    # Redirect anonymous users to index and show an error message:
    else:
        messages.error(request,
                       "Sie sind momentan nicht eingeloggt. Bitte \
                       loggen Sie sich ein, um ihre Übersicht anzuzeigen.")

    return redirect('letters:index')


def letter_detail(request, student_id: int, letter_id: int,
                  confirmation=False):
    """Render detailed information about a certain letter.

    Render all information about a letter to a user.
    If necessary, allow the user to confirm the letter.

    :param request: Current request
    :param student_id: ID of student this letter is being viewed for
    :type student_id: int
    :param letter_id: ID of letter to be displayed
    :type letter_id: int
    :param confirmation: Whether or not to process confirmation form
    :type confirmation: bool
    :return: Detail page of letter
    """

    # Make sure that user is logged in:
    if request.user.is_authenticated:
        # Raise 404 exception if letter or student with the given ids do not exist.
        letter = get_object_or_404(Letter, pk=letter_id)
        student = get_object_or_404(Student, pk=student_id)

        # Make sure that user is parent of that student:
        if not student in request.user.profile.children.all():
            messages.error(request,
                           "Für diesen Schüler dürfen Sie keine Briefe betrachten!")
            return redirect('letters:letters')

        # Make sure that this letter concerns that student:
        if not letter in student.letters:
            messages.error(request,
                           "Dieser Brief betrifft nicht diesen Schüler.")
            return redirect('letters:letters')
    else:
        messages.error(request,
                       "Bitte loggen Sie sich ein, um den Brief zu betrachten!")
        return redirect('letters:index')

    # Process letter confirmation:
    if confirmation:
        # Don't allow confirmation if there is already a response:
        if Response.objects.filter(student__id=student_id,
                                   letter__id=letter_id):
            messages.error(request,
                           "Für diesen Brief und diesen Schüler \
                           liegt bereits eine Bestätigung vor.")

            return redirect('letters:letter_detail', student_id=student_id,
                            letter_id=letter_id)

        # Don't allow confirmation if letter doesn't require it:
        if not Letter.objects.get(id=letter_id).confirmation:
            messages.error(request,
                           "Dieser Brief muss nicht bestätigt werden!")

            return redirect('letters:letter_detail', student_id=student_id,
                            letter_id=letter_id)

        fields = {f"boolfield-{field.id}": False for field in
                  list(letter.responseboolfield_set.all())}
        fields.update({key: request.POST[key] for key in request.POST.keys() if
                       "field-" in key})
        response_content = json.dumps(fields)

        Response.objects.create(letter=Letter.objects.get(id=letter_id),
                                student=Student.objects.get(id=student_id),
                                content=response_content).save()

        messages.success(request, "Brief wurde erfolgreich bestätigt!")

        return redirect('letters:letter_detail', student_id=student_id,
                        letter_id=letter_id)

    # Make sure that the letter is marked as read:
    if student not in letter.students_viewed.all():
        letter.students_viewed.add(student)

    # Check whether a response for this student and this letter exists:
    try:
        response = Response.objects.get(student__pk=student_id,
                                        letter__pk=letter_id)
    except Response.DoesNotExist:
        response = None

    context = {'student': student, 'letter': letter, 'response': response}

    # If letter needs confirmation, add all response fields to context:
    if not response and letter.confirmation:
        context.update(
            {"text_fields": list(letter.responsetextfield_set.all()),
             "bool_fields": list(letter.responseboolfield_set.all()),
             "selection_fields": list(
                 letter.responseselectionfield_set.all())})

    return render(request, 'letters/letter_detail.html', context)


@staff_member_required
def letter_result(request, letter_id):
    """Render information about the responses to a letter.

    Display table containing information on which students have confirmed
    a letter and the contents of the corresponding responses.
    May only be viewed by staff members.

    :param request: Current request
    :param letter_id: ID of letter to be displayed
    :type letter_id: int
    :return: Results page of that letter
    """

    letter = get_object_or_404(Letter, pk=letter_id)

    data = [r.as_dict() for r in
            Response.objects.filter(letter__pk=letter_id)] + [
               {
                   'last_name': s.last_name,
                   'first_name': s.first_name,
                   'class_grp': s.class_group,
                   'confirmed': "Nein"
               }
               for s in letter.students_not_confirmed
           ]

    extra_columns = [(field.name, Column(verbose_name=field.description)) for
                     field in
                     letter.responseboolfield_set.all()] + \
                    [(field.name, Column(verbose_name=field.description)) for
                     field in
                     letter.responseselectionfield_set.all()]
    table = LetterResultTable(data, extra_columns=extra_columns)

    RequestConfig(request).configure(table)

    return render(request, 'letters/letter_result.html', {'table': table})


def login(request):
    """Login page.

    :param request: Current request
    :return: Login page or start page if login was successful
    """

    # Check whether user has already entered credentials:
    if 'username' in request.POST.keys() and 'password' in request.POST.keys():
        # Retrieve credentials from POST arguments:
        username = request.POST['username']
        password = request.POST['password']
        # Check whether the credentials are correct:
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If credentials are corrected login user and redirect to index:
            dj_login(request, user)

            return redirect('letters:index')

        else:
            # If credentials are wrong, redirect to this page and show an error message:
            messages.error(request,
                           "Nutzername oder Passwort sind falsch. Bitte versuchen Sie es erneut.")
            return render(request, 'letters/login.html')

    # If the user has not already entered any credentials, just show the login page:
    else:
        return render(request, 'letters/login.html')


def logout(request):
    """Log out a user and redirect to the index.

    :param request: Current request
    :return: Start page
    """

    dj_logout(request)
    return redirect('letters:index')
