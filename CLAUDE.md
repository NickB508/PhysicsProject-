# CLAUDE.md 

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PhysicSchool is a Django web app created from the Visual Studio "Django Web Project" template (`PhysicSchool.slnx` + `PhysicSchool/PhysicSchool.pyproj`). It is still close to the template: one app (`app`), no models yet, Bootstrap 3 + jQuery 1.10 served as local static files. Dependencies (`requirements.txt`): `Django>=4.2,<5.0` (4.2 LTS; settings were generated for Django 2.1), plus `whitenoise` (imported by `settings.py` middleware, so it must be installed locally too) and `gunicorn` (server only). Developer onboarding and the short deploy procedure are in `PhysicSchool/README.md`; full server details are in `PhysicSchool/deploy/DEPLOY.md`. Keep README in sync when setup or deploy steps change.

## Per-developer setup

Several developers work on different machines, so nothing machine-specific belongs in checked-in files:

- **Python interpreter:** differs per machine and is described in `CLAUDE.local.md` (gitignored, next to this file). If it is missing, ask the user which interpreter to use (`py -0p` lists installed ones) and write it there. Don't put interpreter paths in this file.
- **Django settings:** `settings.py` reads `DJANGO_*` environment variables (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DB_PATH`). Locally they can be set in `PhysicSchool/.env` (gitignored; copy from `PhysicSchool/.env.example`). Real environment variables take precedence over `.env`; the server uses `/etc/physicschool.env`. Add new per-developer settings the same way: read them via `os.environ.get` in `settings.py` and document them in `.env.example`.

## Commands

Run everything from the inner `PhysicSchool/` directory, where `manage.py` lives. Substitute the interpreter from `CLAUDE.local.md` for `python` below:

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

- Without environment variables `settings.py` falls back to development defaults (a dev `SECRET_KEY`, `DEBUG` on, empty `ALLOWED_HOSTS`). Production values come only from the environment.
- `manage.py check` passes even if `whitenoise` is missing; the failure only appears when `runserver` loads the WSGI app. After pulling changes to `requirements.txt`, rerun `pip install -r requirements.txt`.
