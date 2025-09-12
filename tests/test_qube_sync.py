import pytest
import os
import time
import json
import hmac
import hashlib
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from qubesync import QubeSync, QubeSyncError, ConfigError, StaleWebhookError, InvalidWebhookSignatureError

# Set up test environment variables
os.environ["QUBE_API_KEY"] = "test_api_key"
os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"

class TestQubeSync:
    
    def setup_method(self):
        """Setup method run before each test"""
        # Ensure environment variables are set
        os.environ["QUBE_API_KEY"] = "test_api_key"
        os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"
    
    def test_base_url_default(self):
        """Test base_url returns default when QUBE_URL not set"""
        if "QUBE_URL" in os.environ:
            del os.environ["QUBE_URL"]
        assert QubeSync.base_url() == "https://qubesync.com/api/v1"
    
    def test_base_url_custom(self):
        """Test base_url returns custom URL when QUBE_URL is set"""
        os.environ["QUBE_URL"] = "https://custom.api.com"
        assert QubeSync.base_url() == "https://custom.api.com"
        # Clean up
        del os.environ["QUBE_URL"]
    
    def test_default_headers(self):
        """Test default headers are correct"""
        headers = QubeSync.default_headers()
        expected = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        assert headers == expected
    
    def test_api_key_success(self):
        """Test api_key returns the correct key when set"""
        assert QubeSync.api_key() == "test_api_key"
    
    def test_api_key_missing(self):
        """Test api_key raises ConfigError when not set"""
        del os.environ["QUBE_API_KEY"]
        with pytest.raises(ConfigError, match="QUBE_API_KEY not set in environment"):
            QubeSync.api_key()
        # Restore for other tests
        os.environ["QUBE_API_KEY"] = "test_api_key"
    
    def test_api_secret_success(self):
        """Test api_secret returns the correct secret when set"""
        assert QubeSync.api_secret() == "supersecret"
    
    def test_api_secret_missing(self):
        """Test api_secret raises ConfigError when not set"""
        del os.environ["QUBE_WEBHOOK_SECRET"]
        with pytest.raises(ConfigError, match="QUBE_WEBHOOK_SECRET not set in environment"):
            QubeSync.api_secret()
        # Restore for other tests
        os.environ["QUBE_WEBHOOK_SECRET"] = "supersecret"
    
    @patch('requests.Session')
    def test_connection(self, mock_session):
        """Test connection creates a session with proper auth"""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        result = QubeSync.connection()
        
        mock_session.assert_called_once()
        assert mock_session_instance.auth == ("test_api_key", "")
        assert result == mock_session_instance
    
    @patch.object(QubeSync, 'connection')
    def test_get_success(self, mock_connection):
        """Test GET request success"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response
        mock_connection.return_value = mock_session
        
        result = QubeSync.get("test/endpoint")
        
        mock_session.get.assert_called_once_with(
            "https://qubesync.com/api/v1/test/endpoint",
            headers=QubeSync.default_headers()
        )
        assert result == {"data": "test"}
    
    @patch.object(QubeSync, 'connection')
    def test_get_error(self, mock_connection):
        """Test GET request error handling"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_session.get.return_value = mock_response
        mock_connection.return_value = mock_session
        
        with pytest.raises(QubeSyncError, match="Unexpected response: 400"):
            QubeSync.get("test/endpoint")
    
    @patch.object(QubeSync, 'connection')
    def test_post_success(self, mock_connection):
        """Test POST request success"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": "created"}
        mock_session.post.return_value = mock_response
        mock_connection.return_value = mock_session
        
        body = {"key": "value"}
        result = QubeSync.post("test/endpoint", body)
        
        mock_session.post.assert_called_once_with(
            "https://qubesync.com/api/v1/test/endpoint",
            headers=QubeSync.default_headers(),
            json=body
        )
        assert result == {"data": "created"}
    
    @patch.object(QubeSync, 'connection')
    def test_delete_success(self, mock_connection):
        """Test DELETE request success"""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_session.delete.return_value = mock_response
        mock_connection.return_value = mock_session
        
        result = QubeSync.delete("test/endpoint")
        
        mock_session.delete.assert_called_once_with(
            "https://qubesync.com/api/v1/test/endpoint",
            headers=QubeSync.default_headers()
        )
        assert result is True
    
    @patch.object(QubeSync, 'post')
    def test_create_connection_success(self, mock_post):
        """Test create_connection success"""
        mock_post.return_value = {"data": {"id": "conn_123", "name": "test_conn"}}
        
        options = {"name": "test_connection"}
        result = QubeSync.create_connection(options)
        
        mock_post.assert_called_once_with("connections", body=options)
        assert result == {"id": "conn_123", "name": "test_conn"}
    
    @patch.object(QubeSync, 'post')
    def test_create_connection_no_id(self, mock_post):
        """Test create_connection error when no ID returned"""
        mock_post.return_value = {"data": {}}
        
        with pytest.raises(QubeSyncError, match="Could not create connection"):
            QubeSync.create_connection({})
    
    @patch.object(QubeSync, 'delete')
    def test_delete_connection(self, mock_delete):
        """Test delete_connection"""
        mock_delete.return_value = True
        
        result = QubeSync.delete_connection("conn_123")
        
        mock_delete.assert_called_once_with("connections/conn_123")
        assert result is True
    
    @patch.object(QubeSync, 'get')
    def test_get_connection(self, mock_get):
        """Test get_connection"""
        mock_get.return_value = {"data": {"id": "conn_123", "name": "test"}}
        
        result = QubeSync.get_connection("conn_123")
        
        mock_get.assert_called_once_with("connections/conn_123")
        assert result == {"id": "conn_123", "name": "test"}
    
    @patch.object(QubeSync, 'post')
    def test_queue_request_with_json(self, mock_post):
        """Test queue_request with request_json"""
        mock_post.return_value = {"data": {"id": "req_123"}}
        
        request = {
            "request_json": {"version": "16.0", "request": {"key": "value"}},
            "webhook_url": "https://example.com/webhook"
        }
        
        result = QubeSync.queue_request("conn_123", request)
        
        mock_post.assert_called_once_with(
            "connections/conn_123/queued_requests",
            {"queued_request": request}
        )
        assert result == {"id": "req_123"}
    
    @patch.object(QubeSync, 'post')
    def test_queue_request_with_xml(self, mock_post):
        """Test queue_request with request_xml"""
        mock_post.return_value = {"data": {"id": "req_123"}}
        
        request = {
            "request_xml": "<xml>test</xml>",
            "webhook_url": "https://example.com/webhook"
        }
        
        result = QubeSync.queue_request("conn_123", request)
        
        mock_post.assert_called_once_with(
            "connections/conn_123/queued_requests",
            {"queued_request": request}
        )
        assert result == {"id": "req_123"}
    
    def test_queue_request_missing_request_data(self):
        """Test queue_request raises error when neither json nor xml provided"""
        request = {"webhook_url": "https://example.com/webhook"}
        
        with pytest.raises(ValueError, match="must have either request_xml or request_json"):
            QubeSync.queue_request("conn_123", request)
    
    @patch.object(QubeSync, 'get')
    def test_get_request(self, mock_get):
        """Test get_request"""
        mock_get.return_value = {"data": {"id": "req_123", "status": "pending"}}
        
        result = QubeSync.get_request("req_123")
        
        mock_get.assert_called_once_with("queued_requests/req_123")
        assert result == {"id": "req_123", "status": "pending"}
    
    @patch.object(QubeSync, 'get')
    def test_get_requests(self, mock_get):
        """Test get_requests"""
        mock_get.return_value = {"data": [{"id": "req_123"}, {"id": "req_456"}]}
        
        result = QubeSync.get_requests("conn_123")
        
        mock_get.assert_called_once_with("connections/conn_123/queued_requests")
        assert result == [{"id": "req_123"}, {"id": "req_456"}]
    
    @patch.object(QubeSync, 'delete')
    def test_delete_request(self, mock_delete):
        """Test delete_request"""
        mock_delete.return_value = True
        
        result = QubeSync.delete_request("req_123")
        
        mock_delete.assert_called_once_with("queued_requests/req_123")
        assert result is True
    
    @patch.object(QubeSync, 'post')
    def test_get_qwc(self, mock_post):
        """Test get_qwc"""
        mock_post.return_value = {"qwc": "qwc_content_here"}
        
        result = QubeSync.get_qwc("conn_123")
        
        mock_post.assert_called_once_with("connections/conn_123/qwc")
        assert result == "qwc_content_here"
    
    @patch.object(QubeSync, 'post')
    def test_generate_password_success(self, mock_post):
        """Test generate_password success"""
        mock_post.return_value = {"data": {"password": "generated_password"}}
        
        result = QubeSync.generate_password("conn_123")
        
        mock_post.assert_called_once_with("connections/conn_123/password")
        assert result == "generated_password"
    
    @patch.object(QubeSync, 'post')
    def test_generate_password_no_password(self, mock_post):
        """Test generate_password error when no password returned"""
        mock_post.return_value = {"data": {}}
        
        with pytest.raises(QubeSyncError, match="Password not found"):
            QubeSync.generate_password("conn_123")
    
    def test_extract_signature_meta_valid(self):
        """Test extract_signature_meta with valid header"""
        header = "t=1234567890,v1=signature1,v1=signature2"
        
        timestamp, signatures = QubeSync.extract_signature_meta(header)
        
        assert timestamp == 1234567890
        assert signatures == ["signature1", "signature2"]
    
    def test_extract_signature_meta_missing_timestamp(self):
        """Test extract_signature_meta with missing timestamp"""
        header = "v1=signature1"
        
        with pytest.raises(InvalidWebhookSignatureError, match="Invalid signature header format"):
            QubeSync.extract_signature_meta(header)
    
    def test_extract_signature_meta_missing_signature(self):
        """Test extract_signature_meta with missing signature"""
        header = "t=1234567890"
        
        with pytest.raises(InvalidWebhookSignatureError, match="Invalid signature header format"):
            QubeSync.extract_signature_meta(header)
    
    def test_extract_signature_meta_with_equals_in_signature(self):
        """Test extract_signature_meta handles equals signs in signature"""
        header = "t=1234567890,v1=sig==with==equals"
        
        timestamp, signatures = QubeSync.extract_signature_meta(header)
        
        assert timestamp == 1234567890
        assert signatures == ["sig==with==equals"]
    
    def test_sign_payload(self):
        """Test sign_payload generates correct signature"""
        payload = "test_payload"
        expected = hmac.new(
            "supersecret".encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        result = QubeSync.sign_payload(payload)
        
        assert result == expected
    
    def test_verify_and_build_webhook_success(self):
        """Test verify_and_build_webhook with valid signature"""
        payload = '{"key": "value"}'
        timestamp = int(time.time())
        signed_payload = QubeSync.sign_payload(f"{timestamp}.{payload}")
        header = f"t={timestamp},v1={signed_payload}"
        
        result = QubeSync.verify_and_build_webhook(payload, header)
        
        assert result == {"key": "value"}
    
    def test_verify_and_build_webhook_stale(self):
        """Test verify_and_build_webhook with stale timestamp"""
        payload = '{"key": "value"}'
        timestamp = int(time.time()) - 600  # 10 minutes ago
        signed_payload = QubeSync.sign_payload(f"{timestamp}.{payload}")
        header = f"t={timestamp},v1={signed_payload}"
        
        with pytest.raises(StaleWebhookError, match="Timestamp more than 500 seconds old"):
            QubeSync.verify_and_build_webhook(payload, header)
    
    def test_verify_and_build_webhook_invalid_signature(self):
        """Test verify_and_build_webhook with invalid signature"""
        payload = '{"key": "value"}'
        timestamp = int(time.time())
        header = f"t={timestamp},v1=invalid_signature"
        
        with pytest.raises(InvalidWebhookSignatureError, match="Webhook signature mismatch"):
            QubeSync.verify_and_build_webhook(payload, header)
    
    def test_verify_and_build_webhook_custom_max_age(self):
        """Test verify_and_build_webhook with custom max_age"""
        payload = '{"key": "value"}'
        timestamp = int(time.time()) - 100  # 100 seconds ago
        signed_payload = QubeSync.sign_payload(f"{timestamp}.{payload}")
        header = f"t={timestamp},v1={signed_payload}"
        
        # Should pass with max_age=200
        result = QubeSync.verify_and_build_webhook(payload, header, max_age=200)
        assert result == {"key": "value"}
        
        # Should fail with max_age=50
        with pytest.raises(StaleWebhookError):
            QubeSync.verify_and_build_webhook(payload, header, max_age=50)

if __name__ == "__main__":
    pytest.main([__file__])