"""What a mapped operation's input and endings read with: each reads past a missing
association, so a record without one maps to a field left out.

    from qubesync.kit import mapping as m

    def input(self):
        return m.without_nils({
            "operation": "invoice.create",
            "params": {
                "ref_number": m.as_string(self.record.id),
                "txn_date": m.as_date(m.get(self.record, "contract", "approved_at")),
            },
        })
"""
from typing import Any, List, Optional

__all__ = ["get", "rows", "dig", "as_string", "as_number", "as_integer", "as_date", "without_nils"]


def get(value, *names):
    # type: (Any, *str) -> Any
    """value.name1.name2..., or None as soon as one is None."""
    for name in names:
        if value is None:
            return None
        value = getattr(value, name, None)
    return value


def rows(value):
    # type: (Any) -> List[Any]
    """A has-many's rows: a Django manager's .all(), a list as it is, None as none."""
    if value is None:
        return []
    if hasattr(value, "all") and callable(value.all):
        return list(value.all())
    return list(value)


def dig(data, *keys):
    # type: (Any, *str) -> Any
    """data[key1][key2]..., or None as soon as one is missing. data may be a webhook's event
    (qubesync.webhooks), which reads its keys with get as a dict does."""
    for key in keys:
        if isinstance(data, dict) or callable(getattr(data, "get", None)):
            data = data.get(key)
        else:
            return None
    return data


def as_string(value):
    # type: (Any) -> Optional[str]
    if isinstance(value, bool):
        return "true" if value else "false"
    return None if value is None else str(value)


def as_number(value):
    # type: (Any) -> Optional[float]
    """value as a number, or None when it isn't one ("", "n/a"): the field is left out."""
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def as_integer(value):
    # type: (Any) -> Optional[int]
    number = as_number(value)
    return None if number is None else int(number)


def as_date(value):
    # type: (Any) -> Optional[str]
    """A date as QuickBooks takes it, YYYY-MM-DD, from a date, a datetime or a string."""
    if value is None:
        return None
    if hasattr(value, "date") and callable(value.date):
        value = value.date()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)[:10]


def without_nils(value):
    # type: (Any) -> Any
    """value without its None values, at every depth: a field the record doesn't have yet is
    left out rather than sent as null."""
    if isinstance(value, dict):
        return {key: without_nils(inner) for key, inner in value.items() if inner is not None}
    if isinstance(value, list):
        return [without_nils(inner) for inner in value if inner is not None]
    return value
