from datetime import datetime

from app.models import Greeting

T1 = datetime(2026, 11, 10, 9, 0)
T2 = datetime(2026, 11, 8, 9, 0)


def test_add_assigns_id_and_roundtrips_fields(repo):
    added = repo.add(Greeting("oksana", T1, "funny", "Привіт!", True))
    loaded = repo.list_all()[0]
    assert added.id == loaded.id
    assert (loaded.recipient, loaded.send_at, loaded.style) == ("oksana", T1, "funny")
    assert (loaded.text, loaded.repeat, loaded.status) == ("Привіт!", True, "pending")


def test_list_all_is_sorted_by_time(repo):
    repo.add(Greeting("first", T1))
    repo.add(Greeting("second", T2))
    assert [g.recipient for g in repo.list_all()] == ["second", "first"]


def test_due_returns_only_pending_and_past(repo):
    repo.add(Greeting("past", T2))
    repo.add(Greeting("future", T1))
    done = repo.add(Greeting("done", T2))
    done.status = "sent"
    repo.update(done)
    assert [g.recipient for g in repo.due(datetime(2026, 11, 9, 0, 0))] == ["past"]


def test_update_persists_changes(repo):
    added = repo.add(Greeting("oksana", T1))
    added.status, added.error, added.send_at = "failed", "oops", T2
    repo.update(added)
    loaded = repo.list_all()[0]
    assert (loaded.status, loaded.error, loaded.send_at) == ("failed", "oops", T2)


def test_delete(repo):
    added = repo.add(Greeting("oksana", T1))
    assert repo.delete(added.id) is True
    assert repo.delete(added.id) is False
