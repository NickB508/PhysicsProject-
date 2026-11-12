# PhysicSchool

Django 4.2 веб-приложение (шаблон Visual Studio «Django Web Project»).
Все команды ниже выполняются из папки `PhysicSchool/`, в которой лежит `manage.py`.

## Настройка окружения для нового разработчика

### 1. Python

Нужен Python 3.9 или новее (на сервере стоит 3.12). Проверить, что установлено:

```powershell
py -0p
```

Учтите, что `python` в PATH на Windows часто оказывается заглушкой Microsoft Store, а `py` без
параметров запускает самую новую версию. Поэтому указывайте версию явно, например `py -3.9`.

### 2. Зависимости

Удобнее всего поставить их в виртуальное окружение (папка `.venv` в git не попадает):

```powershell
py -3.9 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Дальше вместо `python` используйте `.venv\Scripts\python`. Можно ставить пакеты и в глобальный
Python (`py -3.9 -m pip install -r requirements.txt`), но тогда версии пакетов будут общими
для всех ваших проектов.

После каждого `git pull`, в котором менялся `requirements.txt`, повторите `pip install -r requirements.txt`.
Если не установить `whitenoise`, `manage.py check` пройдёт без ошибок, но `runserver` упадёт с
`No module named 'whitenoise'`.

### 3. Локальные настройки (необязательно)

```powershell
copy .env.example .env
```

В `.env` раскомментируйте то, что нужно поменять (режим отладки, хосты, путь к базе). Без этого
файла работают значения по умолчанию для разработки. Файл `.env` в git не попадает.
Если та же переменная задана в окружении, она важнее значения из `.env`.

### 4. База данных и запуск

```powershell
python manage.py migrate
python manage.py createsuperuser   # для входа на /login/ и /admin/
python manage.py runserver
```

Сайт откроется на http://127.0.0.1:8000/.

### 5. Visual Studio

Откройте `PhysicSchool.slnx`. В окне **Python Environments** выберите или добавьте свой интерпретатор
(для `.venv`: Add Environment → Existing environment → папка `.venv`). Выбор интерпретатора хранится
у каждого разработчика свой, в проект он не записывается.

При добавлении или удалении файлов проверьте, что они есть в `PhysicSchool.pyproj`.

### 6. Claude Code (если используете)

Общие инструкции лежат в `CLAUDE.md` в корне репозитория. Путь к своему интерпретатору запишите в
`CLAUDE.local.md` рядом с ним (в git не попадает), например:

```markdown
# Local machine setup (not in git)
- Use Python 3.9: `py -3.9` (C:\Users\<имя>\...\python.exe). Django is installed in `.venv`.
```

## Деплой на сервер

Схема: nginx → gunicorn → Django, база SQLite, статика через WhiteNoise. Сервер уже настроен.
Подробности (первоначальная настройка, переменные окружения, HTTPS, частые проблемы) описаны в
[`deploy/DEPLOY.md`](deploy/DEPLOY.md).

### Обновление сайта

1. Проверьте изменения локально (`runserver`). Если меняли модели, создайте миграции
   (`python manage.py makemigrations app`) и закоммитьте их.
2. Если добавили пакет, впишите его в `requirements.txt`.
3. Закоммитьте и запушьте в `master`.
4. Выполните на сервере:

   ```bash
   ssh root@83.220.169.41
   sudo -u deploy /srv/physicschool/PhysicSchool/deploy/deploy.sh
   ```

   Скрипт делает `git pull` → `pip install` → `migrate` → `collectstatic` → перезапуск сервиса.
5. Откройте http://83.220.169.41/. Если что-то не работает, смотрите логи:
   `journalctl -u physicschool -n 50 --no-pager`.

### Важно

- Настройки сервера (секретный ключ, `DEBUG=0`, хосты, путь к базе) хранятся в `/etc/physicschool.env`
  на сервере, а не в git. Новую настройку добавьте в `settings.py` через `os.environ.get(...)`,
  опишите в `.env.example` и `deploy/DEPLOY.md` и пропишите её значение в `/etc/physicschool.env`.
- Изменения в `deploy/physicschool.service` и `deploy/nginx.conf` скрипт сам не применяет.
  Как их установить, описано в разделе DEPLOY.md «Если менялись `deploy/physicschool.service` или `deploy/nginx.conf`».
- База на сервере своя (`/var/lib/physicschool/db.sqlite3`), локальная `db.sqlite3` туда не попадает.
- Не трогайте Docker-контейнеры на сервере (порты 442/tcp и 48090/udp).
