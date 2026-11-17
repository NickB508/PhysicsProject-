"""
Definition of views.
"""

import os
from datetime import datetime
from django.http import Http404, HttpRequest
from django.shortcuts import render

# Карточки на главной. Каждая ведёт на /labs/<grade>/.
COURSES = [
    {'grade': 7,  'title': '7 класс'},
    {'grade': 8,  'title': '8 класс'},
    {'grade': 9,  'title': '9 класс'},
    {'grade': 10, 'title': '10 класс'},
]

# Документы лабораторных работ по классам.
# Файлы кладите в app/static/app/docs/<класс>/ (имя латиницей, без пробелов),
# например app/static/app/docs/7/lab-01.docx, и добавляйте строку сюда:
#     7: [
#         {'title': 'Лабораторная работа №1. Измерение объёма тела', 'file': '7/lab-01.docx'},
#     ],
# 'title' показывается на странице и становится именем скачанного файла.
LAB_DOCS = {
    7: [
        {'title': '7 жесткость', 'file': '7/7 ЛР жёсткость.doc'},
        {'title': '7 рычаги', 'file': '7/7 ЛР рычаги.doc'},
        ],
    8: [
        {'title': '8 Ом (автовосстановление)', 'file': '8/8 Ом (автовосстановление).docx'},
        {'title': '8 конструирование цепи', 'file': '8/8 ЛР конструирование цепи.docx'},
        {'title': '8 плавление', 'file': '8/8 ЛР плавление.doc'},
        {'title': '8 тепловой баланс', 'file': '8/8 ЛР тепловой баланс.docx'},
        {'title': '8 удельная теплоёмкость', 'file': '8/8 ЛР удельная теплоёмкость.docx'},],
    9: [{'title': '9 маятник', 'file': '9/9 ЛР маятник.docx'}],
    10: [],
}


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


def labs(request, grade):
    """Renders the list of lab documents for one grade (/labs/<grade>/)."""
    assert isinstance(request, HttpRequest)
    if grade not in LAB_DOCS:
        raise Http404('Нет такого класса')
    docs = []
    for doc in LAB_DOCS[grade]:
        # Расширение берётся из самого файла (.doc, .docx, .pdf ...).
        ext = os.path.splitext(doc['file'])[1].lower()
        docs.append({
            'title': doc['title'],
            'static_path': 'app/docs/' + doc['file'],
            'download_name': doc['title'] + ext,
            'ext': ext,
        })
    return render(
        request,
        'app/labs.html',
        {
            'title': f'Лабораторные работы, {grade} класс',
            'grade': grade,
            'docs': docs,
            'year': datetime.now().year,
        }
    )