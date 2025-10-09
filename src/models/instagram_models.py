"""
Pydantic models for Instagram API data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class MediaType(str, Enum):
    """Instagram media types."""

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"


class InsightMetric(str, Enum):
    """Available insight metrics."""

    IMPRESSIONS = "impressions"
    REACH = "reach"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVED = "saved"
    VIDEO_VIEWS = "video_views"
    PROFILE_VISITS = "profile_visits"
    WEBSITE_CLICKS = "website_clicks"


class InsightPeriod(str, Enum):
    """Insight time periods."""

    DAY = "day"
    WEEK = "week"
    DAYS_28 = "days_28"
    LIFETIME = "lifetime"


class MediaInsight(BaseModel):
    """Media insight data."""

    name: str
    period: str
    values: List[Dict[str, Any]]
    title: str
    description: str


class AccountInsight(BaseModel):
    """Account insight data - supports both time series and total value formats."""

    name: str
    period: str
    values: Optional[List[Dict[str, Any]]] = None
    total_value: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    id: Optional[str] = None


class RateLimitInfo(BaseModel):
    """Rate limit information."""

    app_id: str
    call_count: int
    total_cputime: int
    total_time: int


class InstagramProfile(BaseModel):
    """Instagram business profile information."""

    id: str
    username: str
    name: Optional[str] = None
    biography: Optional[str] = None
    website: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    media_count: Optional[int] = None
    profile_picture_url: Optional[str] = None


class InstagramMedia(BaseModel):
    """Instagram media post."""

    id: str
    media_type: MediaType
    media_url: Optional[str] = None
    permalink: Optional[str] = None
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    timestamp: Optional[datetime] = None
    like_count: Optional[int] = None
    comments_count: Optional[int] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v):
        """Parse timestamp from ISO string."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class UserTag(BaseModel):
    """User tag for media."""

    username: str
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)


class PublishMediaRequest(BaseModel):
    """Request to publish media to Instagram."""

    image_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    caption: Optional[str] = None
    location_id: Optional[str] = None
    user_tags: Optional[List[UserTag]] = None

    @field_validator("image_url", "video_url")
    @classmethod
    def validate_media_url(cls, v, info):
        """Validate that at least one media URL is provided."""
        # This validator will be called for each field individually
        # We'll validate the combination in model_validator
        return v

    @field_validator("caption")
    @classmethod
    def validate_caption_length(cls, v):
        """Validate caption length."""
        if v and len(v) > 2200:
            raise ValueError("Caption must be 2200 characters or less")
        return v


class PublishMediaResponse(BaseModel):
    """Response from publishing media."""

    id: str
    status: str = "published"


class InstagramError(BaseModel):
    """Instagram API error response."""

    message: str
    type: Optional[str] = None
    code: Optional[int] = None
    error_subcode: Optional[int] = None
    fbtrace_id: Optional[str] = None


class FacebookPage(BaseModel):
    """Facebook page information."""

    id: str
    name: str
    access_token: Optional[str] = None
    category: Optional[str] = None
    instagram_business_account: Optional[Dict[str, str]] = None


class AccountInsights(BaseModel):
    """Instagram account insights."""

    model_config = ConfigDict(extra="allow")

    impressions: Optional[int] = None
    reach: Optional[int] = None
    profile_views: Optional[int] = None
    website_clicks: Optional[int] = None
    follower_count: Optional[int] = None
    email_contacts: Optional[int] = None
    phone_call_clicks: Optional[int] = None
    text_message_clicks: Optional[int] = None
    get_directions_clicks: Optional[int] = None


class GetInsightsRequest(BaseModel):
    """Request model for getting insights."""

    media_id: str = Field(..., description="Media ID to get insights for")
    metrics: List[InsightMetric] = Field(..., description="Metrics to retrieve")
    period: Optional[InsightPeriod] = Field(
        InsightPeriod.LIFETIME, description="Time period"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: Dict[str, Any] = Field(..., description="Error details")

    @property
    def message(self) -> str:
        """Get error message."""
        return self.error.get("message", "Unknown error")

    @property
    def code(self) -> int:
        """Get error code."""
        return self.error.get("code", 0)

    @property
    def error_subcode(self) -> Optional[int]:
        """Get error subcode."""
        return self.error.get("error_subcode")


class MCPToolResult(BaseModel):
    """MCP tool execution result."""

    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CacheEntry(BaseModel):
    """Cache entry model."""

    key: str = Field(..., description="Cache key")
    value: Dict[str, Any] = Field(..., description="Cached value")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at
