import os
import json
import requests
import hmac
import hashlib
import time

class QubeSyncError(Exception): pass
class StaleWebhookError(QubeSyncError): pass
class InvalidWebhookSignatureError(QubeSyncError): pass
class ConfigError(QubeSyncError): pass

class QubeSync:
    def base_url():
        return os.getenv("QUBE_URL", "https://qubesync.com/api/v1")

    def default_headers():
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def api_key():
        try:
            return os.environ["QUBE_API_KEY"]
        except KeyError:
            raise ConfigError("QUBE_API_KEY not set in environment.")

    def api_secret():
        try:
            return os.environ["QUBE_WEBHOOK_SECRET"]
        except KeyError:
            raise ConfigError("QUBE_WEBHOOK_SECRET not set in environment.")

    def connection():
        session = requests.Session()
        session.auth = (QubeSync.api_key(), "")
        return session

    def get(url, headers={}):
        resp = QubeSync.connection().get(f"{QubeSync.base_url()}/{url}", headers={**QubeSync.default_headers(), **headers})
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp.json()
        raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

    def post(url, body=None, headers={}):
        resp = QubeSync.connection().post(f"{QubeSync.base_url()}/{url}", headers={**QubeSync.default_headers(), **headers}, json=body)
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp.json()
        raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

    def delete(url, headers={}):
        resp = QubeSync.connection().delete(f"{QubeSync.base_url()}/{url}", headers={**QubeSync.default_headers(), **headers})
        if resp.status_code >= 200 and resp.status_code < 300:
            return True
        raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

    def create_connection():
        resp = QubeSync.post("connections")
        conn_id = resp.get("data", {}).get("id")
        if not conn_id:
            raise QubeSyncError(f"Connection ID not found: {resp}")
        return conn_id

    def delete_connection(id):
        return QubeSync.delete(f"connections/{id}")

    def get_connection(id):
        return QubeSync.get(f"connections/{id}").get("data")

    def queue_request(connection_id, request):
        if not (request.get("request_xml") or request.get("request_json")):
            raise ValueError("must have either request_xml or request_json")
        if not request.get("webhook_url"):
            print("Warning: no webhook_url provided")
        return QubeSync.post(f"connections/{connection_id}/queued_requests", {"queued_request": request}).get("data")

    def get_request(id):
        return QubeSync.get(f"queued_requests/{id}").get("data")

    def get_requests(connection_id):
        return QubeSync.get(f"connections/{connection_id}/queued_requests").get("data")

    def delete_request(id):
        return QubeSync.delete(f"queued_requests/{id}")

    def get_qwc(connection_id):
        return QubeSync.post(f"connections/{connection_id}/qwc").get("qwc")

    def generate_password(connection_id):
        resp = QubeSync.post(f"connections/{connection_id}/password")
        password = resp.get("data", {}).get("password")
        if not password:
            raise QubeSyncError(f"Password not found: {resp}")
        return password

    def extract_signature_meta(header):
        list_items = [i.split("=", 2) for i in header.split(",")]
        timestamp = float([i[1] for i in list_items if i[0] == "t"][0])
        signatures = [i[1] for i in list_items]
        return timestamp, signatures

    def sign_payload(payload):
        return hmac.new(QubeSync.api_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()

    def verify_and_build_webhook(body, signature, max_age=500):
        timestamp, signatures = QubeSync.extract_signature_meta(signature)
        if timestamp < time.time() - max_age:
            raise StaleWebhookError(f"Timestamp more than {max_age} seconds old.")
        
        signed_payload = QubeSync.sign_payload(body)
        if any(hmac.compare_digest(signed_payload, sig) for sig in signatures):
            return json.loads(body)
        
        raise InvalidWebhookSignatureError("Webhook signature mismatch")
