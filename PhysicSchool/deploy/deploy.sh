#!/bin/bash
# Обновление сайта на сервере. Запускать от пользователя deploy:
#   sudo -u deploy /srv/physicschool/PhysicSchool/deploy/deploy.sh
set -euo pipefail

cd /srv/physicschool
git pull --ff-only
./venv/bin/pip install -r PhysicSchool/requirements.txt

cd PhysicSchool
set -a; source /etc/physicschool.env; set +a
../venv/bin/python manage.py migrate --noinput
../venv/bin/python manage.py collectstatic --noinput

sudo systemctl restart physicschool
