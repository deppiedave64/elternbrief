from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib import messages

from .models import Letter, Student, Response


def index(request):
    """Simple homepage."""

    return render(request, 'letters/index.html')


def letters(request):
    """Index of the letters section."""

    # Only show page if user is logged in:
    if request.user.is_authenticated:
        # Make sure that the User has an associated Profile object:
        if hasattr(request.user, 'profile'):
            # Retrieve list of all students the user is allowed to view letters for:
            children_list = request.user.profile.children.all()
            context = {
                'children_list': children_list,
                # Dictionary of ids of all children, associated with the letters that concern them:
                'letters': {child.id: Letter.by_student(child) for child in children_list}
            }
            return render(request, 'letters/letters_index.html', context)
        else:
            # Show error message if the User has now associated Profile object:
            messages.error(request, "Sie sind mit einem Nutzer eingeloggt, der nicht vollständig registriert ist!")


    # Redirect anonymous users to index and show an error message:
    else:
        messages.error(request,
                       "Sie sind momentan nicht eingeloggt. Bitte loggen Sie sich ein, um ihre Übersicht anzuzeigen.")

    return redirect('letters:index')


def letter_detail(request, student_id, letter_id):
    """Shows detailed information about certain Letter object."""

    # Raise 404 exception if a letter or a student with the given id does not exist.
    letter = get_object_or_404(Letter, pk=letter_id)
    student = get_object_or_404(Student, pk=student_id)

    if letter in Letter.by_student(student):
        # Check whether there is already a response for this student and this letter:
        try:
            response = Response.objects.get(student__pk=student_id, letter__pk=letter_id)
        except Response.DoesNotExist:
            response = None

        context = {'student': student, 'letter': letter, 'response': response}
        return render(request, 'letters/letter_detail.html', context)
    else:
        messages.error(request,
                       "Der angegebene Brief betrifft nicht den angegebenen Schüler. Bitte überprüfen Sie ihre Anfrage. "
                       "Wenn Sie denkenm, dass dies nicht passieren sollte, wenden Sie sich bitte an einen Administrator.")
        return redirect('letters:letters')


def login(request):
    """Login page.
    If the user has previously visited this page and entered credentials in the form,
    they will be directed back here and the entered credentials will be in the POST arguments.
    Then they will be logged in a redirected to the index.
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
            messages.error(request, "Nutzername oder Passwort sind falsch. Bitte versuchen Sie es erneut.")
            return render(request, 'letters/login.html')

    # If the user has not already entered any credentials, just show the login page:
    else:
        return render(request, 'letters/login.html')


def logout(request):
    """Logs out a user and redirects to the index."""
    dj_logout(request)
    return redirect('letters:index')
