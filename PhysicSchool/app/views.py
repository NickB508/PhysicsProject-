"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest

# Карточки на главной. Пока ссылки ведут на '#'. Когда появятся страницы
# разделов, замените 'url' на адрес раздела (например, reverse('...')).
COURSES = [
    {'grade': 7,  'title': '7 класс', 'url': '#'},
    {'grade': 8,  'title': '8 класс', 'url': '#'},
    {'grade': 9,  'title': '9 класс', 'url': '#'},
    {'grade': 10, 'title': '10 класс', 'url': '#'},
]


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'courses': COURSES,
            'grades': sorted({c['grade'] for c in COURSES}),
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Контакты',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
