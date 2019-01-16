from django.shortcuts import render


def index(request):
    context = {}

    if not request.user.is_authenticated:
        return render(request, 'letters/index.html', context)
    else:
        return render(request, 'letters/index_logged_in.html', context)


def login(request):
    return render(request, 'letters/login.html')
