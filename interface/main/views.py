from django.shortcuts import render

def index(request):
    return render(request, 'contest/index.html')

def problem(request):
    return render(request, 'contest/problem.html')
