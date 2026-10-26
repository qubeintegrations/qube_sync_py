"""Configures Django once for the kit's tests: the qubesync.django app and its migrations, and
the test app (kitapp), on a SQLite file."""
import os
import tempfile

import django
from django.conf import settings

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
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(tempfile.mkdtemp(), "kit.sqlite3"),
            }
        },
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
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        QUBESYNC_CONFIG="kitapp.config",
    )
    django.setup()
    from django.core.management import call_command

    # qubesync's own migrations, and kitapp's tables from its models.
    call_command("migrate", run_syncdb=True, verbosity=0)
