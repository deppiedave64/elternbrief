from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout

from .models import Letter


def index(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            children_list = request.user.profile.children.all()
            context = {
                'children_list': children_list,
                'letters': {child.id: Letter.by_child(child) for child in children_list}
            }
            return render(request, 'letters/index_logged_in.html', context)
        else:
            context = {
                'error_message': "Sie sind mit einem Nutzer eingeloggt, der nicht vollständig registriert ist!"
            }
            return render(request, 'letters/index.html', context)

    else:
        return render(request, 'letters/index.html')


def letters(request):
    return render(request, 'letters/letters_index.html')


def letter_detail(request, letter_id):
    letter = get_object_or_404(Letter, pk=letter_id)
    context = {'letter': letter}
    return render(request, 'letters/letter_detail.html', context)


def login(request):
    if 'username' in request.POST.keys() and 'password' in request.POST.keys():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            dj_login(request, user)
            return redirect('letters:index')
        else:
            context = {'badlogin': True}
            return render(request, 'letters/login.html', context=context)

    else:
        return render(request, 'letters/login.html')


def logout(request):
    dj_logout(request)
    return redirect('letters:index')
