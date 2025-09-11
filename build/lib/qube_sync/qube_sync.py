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
      session.auth = (api_key(), "")
      return session

  def get(url, headers={}):
      resp = connection().get(f"{base_url()}/{url}", headers={**default_headers(), **headers})
      if resp.status_code >= 200 and resp.status_code < 300:
          return resp.json()
      raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

  def post(url, body=None, headers={}):
      resp = connection().post(f"{base_url()}/{url}", headers={**default_headers(), **headers}, json=body)
      if resp.status_code >= 200 and resp.status_code < 300:
          return resp.json()
      raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

  def delete(url, headers={}):
      resp = connection().delete(f"{base_url()}/{url}", headers={**default_headers(), **headers})
      if resp.status_code >= 200 and resp.status_code < 300:
          return True
      raise QubeSyncError(f"Unexpected response: {resp.status_code}\n{resp.text}")

  def create_connection():
      resp = post("connections")
      conn_id = resp.get("data", {}).get("id")
      if not conn_id:
          raise QubeSyncError(f"Connection ID not found: {resp}")
      return conn_id

  def delete_connection(id):
      return delete(f"connections/{id}")

  def get_connection(id):
      return get(f"connections/{id}").get("data")

  def queue_request(connection_id, request):
      if not (request.get("request_xml") or request.get("request_json")):
          raise ValueError("must have either request_xml or request_json")
      if not request.get("webhook_url"):
          print("Warning: no webhook_url provided")
      return post(f"connections/{connection_id}/queued_requests", {"queued_request": request}).get("data")

  def get_request(id):
      return get(f"queued_requests/{id}").get("data")

  def get_requests(connection_id):
      return get(f"connections/{connection_id}/queued_requests").get("data")

  def delete_request(id):
      return delete(f"queued_requests/{id}")

  def get_qwc(connection_id):
      return post(f"connections/{connection_id}/qwc").get("qwc")

  def generate_password(connection_id):
      resp = post(f"connections/{connection_id}/password")
      password = resp.get("data", {}).get("password")
      if not password:
          raise QubeSyncError(f"Password not found: {resp}")
      return password

  def extract_signature_meta(header):
      parts = header.split(",")
      timestamp = int(parts[0].split("=")[1])
      signatures = [p.split("=")[1] for p in parts[1:]]
      return {"timestamp": timestamp, "signatures": signatures}

  def sign_payload(payload):
      return hmac.new(api_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()

  def verify_and_build_webhook(body, signature, max_age=500):
      meta = extract_signature_meta(signature)
      if meta["timestamp"] < time.time() - max_age:
          raise StaleWebhookError(f"Timestamp more than {max_age} seconds old.")
      if any(sign_payload(body) == sig for sig in meta["signatures"]):
          return json.loads(body)
      raise InvalidWebhookSignatureError("Webhook signature mismatch")
