"""Webhook verification against a delivery signed by the QuBe Sync server.

tests/fixtures/webhook_vectors.json was signed by Qube.WebhookSender.signature_header/3
on the server, with made-up secrets.
"""
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from qubesync import QubeSync, StaleWebhookError, InvalidWebhookSignatureError

VECTORS = json.loads((Path(__file__).parent / "fixtures" / "webhook_vectors.json").read_text(encoding="utf-8"))
T = VECTORS["timestamp"]
BODY = VECTORS["body"]
SECRET_ONE, SECRET_TWO = VECTORS["secrets"]
HEADER_ONE = VECTORS["header_one_secret"]
HEADER_TWO = VECTORS["header_two_secrets"]
V1 = HEADER_ONE.split("v1=")[1]


@pytest.fixture(autouse=True)
def secret_and_clock():
    os.environ["QUBE_WEBHOOK_SECRET"] = SECRET_ONE
    with patch("qubesync.client.time.time", return_value=float(T)):
        yield
    os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"


def at(now):
    return patch("qubesync.client.time.time", return_value=float(now))


def verify(body=BODY, header=HEADER_ONE, **kwargs):
    return QubeSync.verify_and_build_webhook(body, header, **kwargs)


def test_verifies_a_delivery_signed_by_the_server():
    result = verify()
    assert result == json.loads(BODY)
    assert result["response_json"]["note"] == "naïve café — ünïcode"


def test_verifies_raw_bytes():
    assert verify(BODY.encode("utf-8")) == json.loads(BODY)


def test_verifies_while_a_secret_rotates_with_either_secret():
    assert verify(BODY, HEADER_TWO) == json.loads(BODY)
    os.environ["QUBE_WEBHOOK_SECRET"] = SECRET_TWO
    assert verify(BODY, HEADER_TWO) == json.loads(BODY)
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY, HEADER_ONE)


def test_refuses_the_wrong_secret():
    os.environ["QUBE_WEBHOOK_SECRET"] = "whsec_some_other_secret"
    with pytest.raises(InvalidWebhookSignatureError, match="Webhook signature mismatch"):
        verify()


def test_refuses_a_tampered_body():
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY.replace("processed", "cancelled"))


def test_refuses_a_re_serialized_body():
    with pytest.raises(InvalidWebhookSignatureError):
        verify(json.dumps(json.loads(BODY)))


def test_refuses_the_hmac_of_the_body_alone():
    body_only = hmac.new(SECRET_ONE.encode(), BODY.encode(), hashlib.sha256).hexdigest()
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY, f"t={T},v1={body_only}")


def test_refuses_another_scheme():
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY, f"t={T},v0={V1}")


@pytest.mark.parametrize("header", [
    None, "", "garbage", f"v1={V1}", f"t={T}", f"t={T},v1=", f"t=abc,v1={V1}", f"t=,v1={V1}", f"t=²,v1={V1}",
])
def test_refuses_a_malformed_or_missing_header(header):
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY, header)


def test_refuses_a_non_ascii_signature_without_crashing():
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY, f"t={T},v1=ünïcode")


def test_reads_t_and_v1_by_key_in_any_order():
    assert verify(BODY, f"v1={V1},t={T}") == json.loads(BODY)


def test_compares_in_constant_time():
    with patch("qubesync.client.hmac.compare_digest", wraps=hmac.compare_digest) as compare:
        verify()
    assert compare.called


def test_prints_nothing(capsys):
    verify()
    with pytest.raises(InvalidWebhookSignatureError):
        verify(BODY, f"t={T},v1=bad")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_accepts_up_to_300_seconds_old():
    with at(T + 300):
        assert verify() == json.loads(BODY)


def test_refuses_301_seconds_old():
    with at(T + 301), pytest.raises(StaleWebhookError, match="301 seconds old"):
        verify()


def test_accepts_up_to_300_seconds_in_the_future():
    with at(T - 300):
        assert verify() == json.loads(BODY)


def test_refuses_301_seconds_in_the_future():
    with at(T - 301), pytest.raises(StaleWebhookError, match="301 seconds in the future"):
        verify()


def test_max_age_sets_the_window_both_ways():
    with at(T + 120), pytest.raises(StaleWebhookError):
        verify(max_age=60)
    with at(T - 120), pytest.raises(StaleWebhookError):
        verify(max_age=60)
    with at(T - 120):
        assert verify(max_age=120) == json.loads(BODY)


def test_checks_the_window_before_the_signature():
    with at(T + 301), pytest.raises(StaleWebhookError):
        verify(BODY, f"t={T},v1=bad")
