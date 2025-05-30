"""
Unit tests for Instagram API client.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import httpx

# Mock the settings before importing the client
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests."""
    settings = MagicMock()
    settings.instagram_api_url = "https://graph.facebook.com/v19.0"
    settings.instagram_access_token = "test_token"
    settings.instagram_business_account_id = "test_account_id"
    settings.rate_limit_requests_per_hour = 200
    settings.cache_enabled = True
    settings.cache_ttl_seconds = 300
    
    with patch('src.instagram_client.get_settings', return_value=settings):
        yield settings

from src.instagram_client import InstagramClient, InstagramAPIError, RateLimitExceeded
from src.models.instagram_models import (
    InstagramProfile,
    InstagramMedia,
    PublishMediaRequest,
    MediaType,
    InsightMetric,
    MediaInsight
)


@pytest.fixture
def instagram_client(mock_settings):
    """Create Instagram client for testing."""
    with patch('src.instagram_client.httpx.AsyncClient'):
        client = InstagramClient()
        client.client = AsyncMock()
        # Override settings to ensure they're properly set
        client.settings.instagram_business_account_id = "test_account_id"
        return client


class TestInstagramClient:
    """Test cases for Instagram client."""
    
    @pytest.mark.asyncio
    async def test_get_profile_info_success(self, instagram_client):
        """Test successful profile info retrieval."""
        # Mock API response
        mock_response = {
            "id": "test_account_id",
            "username": "test_user",
            "name": "Test User",
            "biography": "Test bio",
            "followers_count": 1000,
            "follows_count": 500,
            "media_count": 100
        }
        
        instagram_client._make_request = AsyncMock(return_value=mock_response)
        
        # Call method
        profile = await instagram_client.get_profile_info()
        
        # Assertions
        assert isinstance(profile, InstagramProfile)
        assert profile.id == "test_account_id"
        assert profile.username == "test_user"
        assert profile.followers_count == 1000
        
        # Verify API call
        instagram_client._make_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_profile_info_no_account_id(self, instagram_client):
        """Test profile info retrieval without account ID configured."""
        instagram_client.settings.instagram_business_account_id = None
        
        with pytest.raises(InstagramAPIError, match="Instagram business account ID not configured"):
            await instagram_client.get_profile_info()
    
    @pytest.mark.asyncio
    async def test_get_media_posts_success(self, instagram_client):
        """Test successful media posts retrieval."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "id": "post_1",
                    "media_type": "IMAGE",
                    "caption": "Test post",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "like_count": 50,
                    "comments_count": 10
                },
                {
                    "id": "post_2",
                    "media_type": "VIDEO",
                    "caption": "Test video",
                    "timestamp": "2024-01-02T12:00:00Z",
                    "like_count": 75,
                    "comments_count": 15
                }
            ]
        }
        
        instagram_client._make_request = AsyncMock(return_value=mock_response)
        
        # Call method
        posts = await instagram_client.get_media_posts(limit=10)
        
        # Assertions
        assert len(posts) == 2
        assert all(isinstance(post, InstagramMedia) for post in posts)
        assert posts[0].id == "post_1"
        assert posts[0].media_type == MediaType.IMAGE
        assert posts[1].media_type == MediaType.VIDEO
        
        # Verify timestamp conversion
        assert isinstance(posts[0].timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_get_media_insights_success(self, instagram_client):
        """Test successful media insights retrieval."""
        # Mock API response
        mock_response = {
            "data": [
                {
                    "name": "impressions",
                    "period": "lifetime",
                    "values": [{"value": 1000}],
                    "title": "Impressions",
                    "description": "Total impressions"
                },
                {
                    "name": "reach",
                    "period": "lifetime",
                    "values": [{"value": 800}],
                    "title": "Reach",
                    "description": "Total reach"
                }
            ]
        }
        
        instagram_client._make_request = AsyncMock(return_value=mock_response)
        
        # Call method
        insights = await instagram_client.get_media_insights("test_media_id")
        
        # Assertions
        assert len(insights) == 2
        assert insights[0].name == "impressions"
        assert insights[1].name == "reach"
        
        # Verify API call
        instagram_client._make_request.assert_called_once_with(
            "GET", f"test_media_id/insights", params={"metric": "impressions,reach,likes,comments,shares,saves"}
        )
    
    @pytest.mark.asyncio
    async def test_publish_media_success(self, instagram_client):
        """Test successful media publishing."""
        # Mock API responses
        container_response = {"id": "container_123"}
        publish_response = {"id": "media_456"}
        
        instagram_client._make_request = AsyncMock(side_effect=[container_response, publish_response])
        
        # Create publish request
        request = PublishMediaRequest(
            image_url="https://example.com/image.jpg",
            caption="Test caption"
        )
        
        # Call method
        response = await instagram_client.publish_media(request)
        
        # Assertions
        assert response.id == "media_456"
        assert response.status == "published"
        
        # Verify API calls
        assert instagram_client._make_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_validate_access_token_success(self, instagram_client):
        """Test successful access token validation."""
        instagram_client._make_request = AsyncMock(return_value={"id": "test_id"})
        
        is_valid = await instagram_client.validate_access_token()
        
        assert is_valid is True
        instagram_client._make_request.assert_called_once_with(
            "GET", "me", params={"fields": "id"}, use_cache=False
        )
    
    @pytest.mark.asyncio
    async def test_validate_access_token_failure(self, instagram_client):
        """Test access token validation failure."""
        instagram_client._make_request = AsyncMock(side_effect=InstagramAPIError("Invalid token"))
        
        is_valid = await instagram_client.validate_access_token()
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, instagram_client):
        """Test rate limit handling."""
        # Mock HTTP response with 429 status
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        
        instagram_client.client.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(RateLimitExceeded):
            await instagram_client._make_request("GET", "test_endpoint")
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, instagram_client):
        """Test Instagram API error handling."""
        # Mock HTTP response with API error
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid parameter",
                "code": 100,
                "error_subcode": 1234
            }
        }
        
        instagram_client.client.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(InstagramAPIError) as exc_info:
            await instagram_client._make_request("GET", "test_endpoint")
        
        assert exc_info.value.message == "Invalid parameter"
        assert exc_info.value.error_code == 100
        assert exc_info.value.error_subcode == 1234
    
    def test_cache_key_generation(self, instagram_client):
        """Test cache key generation."""
        endpoint = "test_endpoint"
        params = {"param1": "value1", "param2": "value2"}
        
        key = instagram_client._get_cache_key(endpoint, params)
        
        assert "test_endpoint" in key
        assert "param1=value1" in key
        assert "param2=value2" in key
    
    def test_cache_validity_check(self, instagram_client):
        """Test cache validity checking."""
        from datetime import datetime, timedelta
        
        # Valid cache entry
        valid_entry = {
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        assert instagram_client._is_cache_valid(valid_entry) is True
        
        # Expired cache entry
        expired_entry = {
            "expires_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        }
        assert instagram_client._is_cache_valid(expired_entry) is False
        
        # No expiration time
        no_expiry_entry = {}
        assert instagram_client._is_cache_valid(no_expiry_entry) is False
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, instagram_client):
        """Test response caching."""
        mock_response = {"data": "test_data"}
        
        # Mock the client to return a successful response
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = mock_response
        
        instagram_client.client.get = AsyncMock(return_value=mock_http_response)
        
        # First call should hit the API
        result1 = await instagram_client._make_request("GET", "test_endpoint", params={"param": "value"})
        assert result1 == mock_response
        
        # Second call should use cache
        result2 = await instagram_client._make_request("GET", "test_endpoint", params={"param": "value"})
        assert result2 == mock_response
        
        # Should only call the API once due to caching
        assert instagram_client.client.get.call_count == 1
    
    @pytest.mark.asyncio
    async def test_close_client(self, instagram_client):
        """Test client cleanup."""
        await instagram_client.close()
        instagram_client.client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_settings):
        """Test async context manager usage."""
        with patch('src.instagram_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            async with InstagramClient() as client:
                assert client is not None
            
            mock_client.aclose.assert_called_once()


class TestInstagramAPIError:
    """Test cases for Instagram API error handling."""
    
    def test_error_creation(self):
        """Test error object creation."""
        error = InstagramAPIError("Test error", 100, 1234)
        
        assert error.message == "Test error"
        assert error.error_code == 100
        assert error.error_subcode == 1234
        assert str(error) == "Test error"
    
    def test_error_without_codes(self):
        """Test error creation without error codes."""
        error = InstagramAPIError("Simple error")
        
        assert error.message == "Simple error"
        assert error.error_code is None
        assert error.error_subcode is None


class TestRateLimitExceeded:
    """Test cases for rate limit exception."""
    
    def test_rate_limit_error(self):
        """Test rate limit error creation."""
        error = RateLimitExceeded("Rate limit exceeded")
        
        assert isinstance(error, InstagramAPIError)
        assert error.message == "Rate limit exceeded" 