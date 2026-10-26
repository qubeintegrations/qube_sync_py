"""JSONTextField: JSON kept in a text column, for qube_runs' input, error, question and links."""
from django.db import models

from ..kit._models import dump_json, load_json

__all__ = ["JSONTextField"]


class JSONTextField(models.TextField):
    """JSON kept as text, rather than in a JSONField: the same on PostgreSQL, MySQL (and
    MariaDB) and SQLite, from Django 3.2, with no JSON1 extension or MySQL version to depend
    on. Nothing queries inside these columns."""

    def from_db_value(self, value, expression, connection):
        return load_json(value)

    def get_prep_value(self, value):
        return dump_json(value)

    def value_to_string(self, obj):
        return dump_json(self.value_from_object(obj))
