"""Operation and ConnectionEvents that save through SQLAlchemy: the bases qubesync.flask and
qubesync.fastapi give your classes. Needs SQLAlchemy (imported at the first save).

save_record commits the session the record belongs to, so find_record returns a record from
your session (session.get(Invoice, record_id), or Flask-SQLAlchemy's db.session.get).

With more than one worker, a record's events can run in any order, a later one first, and two
at once. handle applies a run event only when its revision is newer than the last applied,
and takes a notification once, by its delivery_id; take a row lock on the record as you find
it (select(Invoice).where(Invoice.id == record_id).with_for_update(), or SELECT ... FOR
UPDATE) so two workers never apply one record's events at once. The first commit releases
it. Override save_record for another ORM.
"""
from typing import Any, List

from . import _bases

__all__ = ["Operation", "ConnectionEvents", "commit"]


def commit(record):
    # type: (Any) -> None
    """Commits the session record belongs to."""
    from sqlalchemy.orm import object_session

    session = object_session(record)
    if session is None:
        raise RuntimeError(
            "qubesync: %r isn't in a SQLAlchemy session, so save_record can't commit it: return "
            "a record from your session in find_record, or override save_record" % (record,)
        )
    session.commit()


class Operation(_bases.Operation):
    __doc__ = _bases.Operation.__doc__

    def save_record(self, fields):
        # type: (List[str]) -> None
        """Writes those fields of the record. As written, SQLAlchemy's way: it commits the
        session the record belongs to (every change in it, not only those fields). Override
        it for another ORM."""
        commit(self.record)


class ConnectionEvents(_bases.ConnectionEvents):
    __doc__ = _bases.ConnectionEvents.__doc__

    def save_record(self, fields):
        # type: (List[str]) -> None
        """Writes those fields of the account. As written, SQLAlchemy's way: it commits the
        session the account belongs to. Override it for another ORM."""
        commit(self.account)
