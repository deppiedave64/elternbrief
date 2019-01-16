from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout


def index(request):
    context = {}

    if request.user.is_authenticated:
        return render(request, 'letters/index_logged_in.html', context)
    else:
        return render(request, 'letters/index.html', context)


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
