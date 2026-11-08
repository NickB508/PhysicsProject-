# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PhysicSchool is a Django web app created from the Visual Studio "Django Web Project" template (`PhysicSchool.slnx` + `PhysicSchool/PhysicSchool.pyproj`). It is still close to the template: one app (`app`), no models yet, Bootstrap 3 + jQuery 1.10 served as local static files. The only dependency is `Django>=3.2.14` (settings were generated for Django 2.1).

## Commands

Run everything from the inner `PhysicSchool/` directory, where `manage.py` lives. On this machine, `python` on PATH is the Microsoft Store stub. The real interpreter is Python 3.9 (`py -3.9` or `C:\Users\user\AppData\Local\Programs\Python\Python39\python.exe`), and it has Django 4.2 installed globally (no virtualenv). Substitute it for `python` below:

```bash
pip install -r requirements.txt
python manage.py migrate                 # SQLite DB at PhysicSchool/db.sqlite3
python manage.py createsuperuser         # needed to use /login/ and /admin/
python manage.py runserver
python manage.py makemigrations app      # after editing app/models.py
```

There is no linter or formatter configured.

## Architecture

- `PhysicSchool/PhysicSchool/`: project package (`settings.py`, `urls.py`, `wsgi.py`). **All URL routes are defined in this project-level `urls.py`**; `app` has no `urls.py` of its own. Login/logout use Django's built-in `LoginView`/`LogoutView`, with `app.forms.BootstrapAuthenticationForm` and the `app/login.html` template.
- `PhysicSchool/app/`: the single Django app.
  - Views are function-based. Each one renders `app/<page>.html` with a context that includes `title` and `year`, and `layout.html` uses both, so new views should pass them too.
  - Templates live in `app/templates/app/`. Every page does `{% extends "app/layout.html" %}` and fills `{% block content %}` (and, optionally, `{% block scripts %}`). The navbar and the login/logout partial (`loginpartial.html`) are in the layout.
  - Static assets live in `app/static/app/{content,scripts,fonts}` and are referenced as `{% static 'app/...' %}`.
- `PhysicSchool.pyproj` lists every source and content file explicitly. When you add or remove files, add or remove matching `<Compile>`/`<Content>` entries so the Visual Studio project stays in sync.

## Gotchas

- `settings.py` hardcodes `SECRET_KEY`, sets `DEBUG = True` and `ALLOWED_HOSTS = []`, so it is only suitable for development.
