from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'letters/index.html', context)
