# Деплой PhysicSchool

Схема: **nginx (80) → gunicorn (unix-сокет) → Django**, база SQLite, статика через WhiteNoise.
Сервер: Ubuntu 24.04, Python 3.12, `83.220.169.41`. Домена пока нет, работает по HTTP.

> На сервере также работает нужная программа (Docker-контейнеры на портах 442/tcp и
> 48090/udp). Не останавливать и не менять эти контейнеры и их порты.

## Что где лежит на сервере

| Что | Где |
|---|---|
| Код (git-клон) | `/srv/physicschool` (владелец `deploy`) |
| Виртуальное окружение | `/srv/physicschool/venv` |
| Django-проект (`manage.py`) | `/srv/physicschool/PhysicSchool` |
| Собранная статика | `/srv/physicschool/PhysicSchool/static` |
| База данных SQLite | `/var/lib/physicschool/db.sqlite3` (вне репозитория) |
| Переменные окружения | `/etc/physicschool.env` (root:deploy, права 640) |
| systemd-сервис | `/etc/systemd/system/physicschool.service` |
| Конфиг nginx | `/etc/nginx/sites-available/physicschool` (симлинк в `sites-enabled`) |
| Сокет gunicorn | `/run/physicschool/gunicorn.sock` |

Копии конфигов лежат в репозитории, в папке `deploy/`. Источник правды для сервиса и nginx это
они: после изменений их нужно заново скопировать на сервер (см. ниже).

## Переменные окружения (`/etc/physicschool.env`)

```
DJANGO_SECRET_KEY=<случайная строка, секрет, в git не хранить>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=83.220.169.41
DJANGO_CSRF_TRUSTED_ORIGINS=http://83.220.169.41
DJANGO_DB_PATH=/var/lib/physicschool/db.sqlite3
```

Сгенерировать новый ключ: `python3 -c "import secrets;print(secrets.token_urlsafe(50))"`.
Несколько хостов или origin перечисляются через запятую. После изменения файла:
`systemctl restart physicschool`.

## Обычное обновление сайта

1. Закоммитить и запушить изменения в ветку `master`.
2. На сервере (под root или любым пользователем с sudo):

   ```bash
   ssh root@83.220.169.41
   sudo -u deploy /srv/physicschool/PhysicSchool/deploy/deploy.sh
   ```

Скрипт `deploy.sh` делает: `git pull --ff-only` → `pip install -r requirements.txt` →
`migrate` → `collectstatic` → `systemctl restart physicschool`.

Проверка: открыть http://83.220.169.41/ и посмотреть логи при проблемах:
`journalctl -u physicschool -n 50 --no-pager`.

## Первоначальная настройка сервера (уже сделана, для справки и для нового сервера)

Всё выполняется под root.

1. **Пакеты:**
   ```bash
   apt-get update            # ошибку про репозиторий zabbix от хостера можно игнорировать
   apt-get install -y nginx python3-venv python3-pip git
   ```
2. **Пользователь и каталоги:**
   ```bash
   adduser --disabled-password --gecos "" deploy
   mkdir -p /srv/physicschool /var/lib/physicschool
   chown deploy:deploy /srv/physicschool /var/lib/physicschool
   ```
3. **Файл окружения** `/etc/physicschool.env` (см. выше), затем:
   ```bash
   chown root:deploy /etc/physicschool.env && chmod 640 /etc/physicschool.env
   ```
4. **sudo без пароля для перезапуска сервиса** (нужен скрипту деплоя):
   ```bash
   echo "deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart physicschool" > /etc/sudoers.d/physicschool
   chmod 440 /etc/sudoers.d/physicschool
   ```
5. **Доступ сервера к приватному репозиторию (deploy key, только чтение):**
   ```bash
   sudo -u deploy bash -c 'mkdir -p ~/.ssh && chmod 700 ~/.ssh \
     && ssh-keygen -t ed25519 -N "" -C deploy@physicschool -f ~/.ssh/id_ed25519 \
     && ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts \
     && cat ~/.ssh/id_ed25519.pub'
   ```
   Публичный ключ добавить в GitHub: репозиторий → Settings → Deploy keys → Add deploy key
   (**без** Allow write access).
6. **Клонирование и установка:**
   ```bash
   sudo -u deploy git clone git@github.com:NickB508/PhysicsProject-.git /srv/physicschool
   cd /srv/physicschool
   sudo -u deploy python3 -m venv venv
   sudo -u deploy ./venv/bin/pip install -r PhysicSchool/requirements.txt
   chmod +x PhysicSchool/deploy/deploy.sh
   ```
7. **Миграции и статика:**
   ```bash
   cd /srv/physicschool/PhysicSchool
   sudo -u deploy bash -c 'set -a; source /etc/physicschool.env; set +a; \
     ../venv/bin/python manage.py migrate --noinput; \
     ../venv/bin/python manage.py collectstatic --noinput'
   ```
8. **systemd и nginx:**
   ```bash
   install -m 644 /srv/physicschool/PhysicSchool/deploy/physicschool.service /etc/systemd/system/
   install -m 644 /srv/physicschool/PhysicSchool/deploy/nginx.conf /etc/nginx/sites-available/physicschool
   ln -sf /etc/nginx/sites-available/physicschool /etc/nginx/sites-enabled/physicschool
   rm -f /etc/nginx/sites-enabled/default
   nginx -t
   systemctl daemon-reload
   systemctl enable --now physicschool
   systemctl reload nginx          # reload обязателен, одного nginx -t недостаточно
   ```
9. **Файрвол** (сначала разрешить, потом включать, чтобы не потерять SSH и VPN):
   ```bash
   ufw allow 22/tcp; ufw allow 80/tcp; ufw allow 443/tcp
   ufw allow 442/tcp; ufw allow 48090/udp     # порты VPN
   ufw enable
   ```
10. **Администратор сайта** (пароль вводится интерактивно):
    ```bash
    sudo -u deploy bash -c 'cd /srv/physicschool/PhysicSchool && set -a && source /etc/physicschool.env && set +a && ../venv/bin/python manage.py createsuperuser'
    ```

## Если менялись `deploy/physicschool.service` или `deploy/nginx.conf`

`deploy.sh` их **не** переустанавливает. После `git pull` на сервере:

```bash
install -m 644 /srv/physicschool/PhysicSchool/deploy/physicschool.service /etc/systemd/system/
install -m 644 /srv/physicschool/PhysicSchool/deploy/nginx.conf /etc/nginx/sites-available/physicschool
systemctl daemon-reload && systemctl restart physicschool
nginx -t && systemctl reload nginx
```

## Частые проблемы

- **Открывается страница «Welcome to nginx»:** nginx не перезагружен после смены конфига
  (`systemctl reload nginx`) или не удалён `sites-enabled/default`.
- **400 Bad Request:** адрес, по которому открывают сайт, не входит в `DJANGO_ALLOWED_HOSTS`.
  При запросах с самого сервера через `127.0.0.1` это нормально.
- **403 при отправке формы (CSRF):** проверить `DJANGO_CSRF_TRUSTED_ORIGINS` (с схемой, `http://...`).
- **502 Bad Gateway:** не запущен gunicorn, смотреть `systemctl status physicschool` и
  `journalctl -u physicschool`.
- **Не грузится CSS:** не выполнен `collectstatic` или нет прав на каталог `static`.
- **`git pull` не проходит:** проверить, что deploy key добавлен в GitHub, команды git выполнять
  от пользователя `deploy`, а не от root («dubious ownership»).

## Когда появится домен (HTTPS)

1. Указать A-запись домена на `83.220.169.41`.
2. В `deploy/nginx.conf` заменить `server_name _;` на `server_name example.ru;`.
3. `apt-get install -y certbot python3-certbot-nginx && certbot --nginx -d example.ru`.
4. В `/etc/physicschool.env`: `DJANGO_ALLOWED_HOSTS=example.ru`,
   `DJANGO_CSRF_TRUSTED_ORIGINS=https://example.ru`, затем `systemctl restart physicschool`.
5. По желанию добавить в `settings.py` `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`,
   `CSRF_COOKIE_SECURE`.

## Открытые вопросы / рекомендации

- Убрать `db.sqlite3` из git (`git rm --cached PhysicSchool/db.sqlite3`): на сервере своя база.
- Отключить вход root по паролю (`PermitRootLogin prohibit-password` в `sshd_config`).
- Закрыть лишние порты, открытые хостером в ufw (FTP, почта и др.), если не используются.
- Старый `SECRET_KEY` остался в истории git, считать его скомпрометированным.
- Резервная копия: `/var/lib/physicschool/db.sqlite3`.
