"""Configures Django once for the kit's tests: the qubesync.django app and its migrations, and
the test app (kitapp), on a SQLite file, or with KIT_PG_URL on PostgreSQL's kit_django."""
import os
import tempfile
from urllib.parse import urlparse

import django
from django.conf import settings


def _database():
    url = os.environ.get("KIT_PG_URL")
    if not url:
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(tempfile.mkdtemp(), "kit.sqlite3")}
    parts = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "kit_django",
        "USER": parts.username,
        "PASSWORD": parts.password,
        "HOST": parts.hostname,
        "PORT": parts.port or 5432,
    }


if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="kit-tests",
        ALLOWED_HOSTS=["testserver", "app.example"],
        ROOT_URLCONF="kitapp.urls",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "qubesync.django",
            "kitapp",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        DATABASES={"default": _database()},
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.template.context_processors.csrf",
                    ]
                },
            }
        ],
        LOGIN_URL="/login",
        STATIC_URL="/static/",
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        QUBESYNC_CONFIG="kitapp.config",
    )
    django.setup()
    from django.core.management import call_command

    # qubesync's own migrations, then kitapp's tables from its models (after auth's, which
    # PostgreSQL's foreign keys need first).
    call_command("migrate", verbosity=0)
    call_command("migrate", run_syncdb=True, verbosity=0)
