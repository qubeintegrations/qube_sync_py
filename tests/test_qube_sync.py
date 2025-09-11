import pytest
import os
import time
import json
from qubesync import QubeSync, QubeSyncError, ConfigError, StaleWebhookError, InvalidWebhookSignatureError

os.environ["QUBE_API_KEY"] = "test_api_key"
os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"

def test_multiline_list():
   requests = [
    1,
    2,
    3
  ]
# def test_queue_request():
#    request = {
#       "request_json": {
#          "version": "16.0",
#          "request": {"key": "value"}
#       }
#     }
   
#    connection_id = "test_connection_id"

#    # Mock the QubeSync endpoint
#    response = QubeSync.queue_request(connection_id, request)

   

def test_verify_and_build_webhook():
    # Mock the payload and signature
    payload = '{"key": "value"}'
    signature = QubeSync.sign_payload(payload)
    
    # Mock the header with a current timestamp
    timestamp = time.time()
    header = f"t={timestamp},v1={signature}"
    
    # Call the method
    result = QubeSync.verify_and_build_webhook(payload, header)
    
    # Check if the result is as expected
    assert result == json.loads(payload)

if __name__ == "__main__":
  pytest.main()