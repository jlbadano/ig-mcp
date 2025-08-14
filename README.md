[![MSeeP.ai Security Assessment Badge](https://mseep.net/pr/jlbadano-ig-mcp-badge.png)](https://mseep.ai/app/jlbadano-ig-mcp)

# Instagram MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with Instagram's Graph API, enabling AI applications to interact with Instagram Business accounts programmatically.

## Features

### 🔧 Tools (Model-controlled)
- **Get Profile Info**: Retrieve Instagram business profile details
- **Get Media Posts**: Fetch recent posts from an Instagram account
- **Get Media Insights**: Retrieve engagement metrics for specific posts
- **Publish Media**: Upload and publish images/videos to Instagram
- **Get Account Pages**: List Facebook pages connected to the account

### 📊 Resources (Application-controlled)
- **Profile Data**: Access to profile information including follower counts, bio, etc.
- **Media Feed**: Recent posts with engagement metrics
- **Insights Data**: Detailed analytics for posts and account performance

### 💬 Prompts (User-controlled)
- **Analyze Engagement**: Pre-built prompt for analyzing post performance
- **Content Strategy**: Template for generating content recommendations
- **Hashtag Analysis**: Prompt for hashtag performance evaluation

## Prerequisites

1. **Instagram Business Account**: Must be connected to a Facebook Page
2. **Facebook Developer Account**: Required for API access
3. **Access Token**: Long-lived access token with appropriate permissions
4. **Python 3.10+**: For running the MCP server (required by MCP dependencies)

### Required Instagram API Permissions
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_insights`
- `pages_show_list`
- `pages_read_engagement`

## 🔑 How to Get Instagram API Credentials

> 📖 **Quick Start**: See [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) for a 5-minute setup guide!

This section provides a step-by-step guide to obtain the necessary credentials for the Instagram MCP server.

### Step 1: Set Up Instagram Business Account

1. **Convert to Business Account** (if not already):
   - Open Instagram app → Settings → Account → Switch to Professional Account
   - Choose "Business" → Select a category → Complete setup

2. **Connect to Facebook Page**:
   - Go to Instagram Settings → Account → Linked Accounts → Facebook
   - Connect to an existing Facebook Page or create a new one
   - **Important**: The Facebook Page must be owned by you

### Step 2: Create Facebook App

1. **Go to Facebook Developers**:
   - Visit [developers.facebook.com](https://developers.facebook.com)
   - Log in with your Facebook account

2. **Create New App**:
   - Click "Create App" → Choose "Business" → Click "Next"
   - Fill in app details:
     - **App Name**: Choose a descriptive name (e.g., "My Instagram MCP Server")
     - **App Contact Email**: Your email address
   - Click "Create App"

3. **Add Instagram Basic Display Product**:
   - In your app dashboard, click "Add Product"
   - Find "Instagram Basic Display" → Click "Set Up"

4. **Configure Instagram Basic Display**:
   - Go to Instagram Basic Display → Basic Display
   - Click "Create New App" in the Instagram App section
   - Accept the terms and create the app

### Step 3: Get App Credentials

1. **Get App ID and Secret**:
   - In your Facebook app dashboard, go to Settings → Basic
   - Copy your **App ID** and **App Secret**
   - **Important**: Keep the App Secret secure and never share it publicly

### Step 4: Set Up Instagram Business API Access

1. **Add Instagram Graph API Product**:
   - In your app dashboard, click "Add Product"
   - Find "Instagram Graph API" → Click "Set Up"

2. **Configure Permissions**:
   - Go to Instagram Graph API → Permissions
   - Request the following permissions:
     - `instagram_basic`
     - `instagram_content_publish`
     - `instagram_manage_insights`
     - `pages_show_list`
     - `pages_read_engagement`

### Step 5: Generate Access Token

#### Option A: Using Facebook Graph API Explorer (Recommended for Testing)

1. **Go to Graph API Explorer**:
   - Visit [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)

2. **Configure Explorer**:
   - Select your app from the dropdown
   - Click "Generate Access Token"
   - Select required permissions when prompted

3. **Get Page Access Token**:
   - In the explorer, make a GET request to: `/me/accounts`
   - Find your Facebook Page in the response
   - Copy the `access_token` for your page

4. **Get Instagram Business Account ID**:
   - Use the page access token to make a GET request to: `/{page-id}?fields=instagram_business_account`
   - Copy the Instagram Business Account ID from the response

#### Option B: Using Facebook Login Flow (Recommended for Production)

1. **Set Up Facebook Login**:
   - In your app dashboard, add "Facebook Login" product
   - Configure Valid OAuth Redirect URIs

2. **Implement OAuth Flow**:
   ```python
   # Example OAuth URL
   oauth_url = f"https://www.facebook.com/v19.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope=pages_show_list,instagram_basic,instagram_content_publish,instagram_manage_insights"
   ```

3. **Exchange Code for Token**:
   ```python
   # Exchange authorization code for access token
   token_url = f"https://graph.facebook.com/v19.0/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&client_secret={app_secret}&code={auth_code}"
   ```

### Step 6: Get Long-Lived Access Token

Short-lived tokens expire in 1 hour. Convert to long-lived token (60 days):

```bash
curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_lived_token}"
```

### Step 7: Set Up Environment Variables

Create a `.env` file in your project root:

```env
# Facebook App Credentials
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here

# Instagram Access Token (long-lived)
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token_here

# Instagram Business Account ID
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here

# Optional: API Configuration
INSTAGRAM_API_VERSION=v19.0
RATE_LIMIT_REQUESTS_PER_HOUR=200
CACHE_ENABLED=true
LOG_LEVEL=INFO
```

### Step 8: Test Your Setup

Run the validation script to test your credentials:

```bash
python scripts/setup.py
```

Or test manually:

```python
import os
import requests

# Test access token
access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
response = requests.get(f'https://graph.facebook.com/v19.0/me?access_token={access_token}')
print(response.json())
```

### 🚨 Important Security Notes

1. **Never commit credentials to version control**
2. **Use environment variables or secure secret management**
3. **Regularly rotate access tokens**
4. **Monitor token expiration dates**
5. **Use HTTPS only in production**
6. **Implement proper error handling for expired tokens**

### 🔄 Token Refresh Strategy

Long-lived tokens expire after 60 days. Implement automatic refresh:

```python
# Check token validity
def check_token_validity(access_token):
    url = f"https://graph.facebook.com/v19.0/me?access_token={access_token}"
    response = requests.get(url)
    return response.status_code == 200

# Refresh token before expiration
def refresh_long_lived_token(access_token, app_id, app_secret):
    url = f"https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': access_token
    }
    response = requests.get(url, params=params)
    return response.json().get('access_token')
```

### 📋 Troubleshooting Common Issues

**Error: "Invalid OAuth access token"**
- Check if token has expired
- Verify token has required permissions
- Ensure Instagram account is connected to Facebook Page

**Error: "Instagram account not found"**
- Verify Instagram Business Account ID is correct
- Check if Instagram account is properly linked to Facebook Page
- Ensure account is a Business account, not Personal

**Error: "Insufficient permissions"**
- Review required permissions in Facebook App
- Re-generate access token with correct scopes
- Check if app is in Development vs Live mode

**Rate Limiting Issues**
- Implement exponential backoff
- Cache responses when possible
- Monitor rate limit headers in API responses

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ig-mcp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your Instagram API credentials
```

4. **Configure the MCP server**:
```bash
# Edit config.json with your specific settings
```

## Configuration

### Environment Variables (.env)
```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
```

### MCP Client Configuration
Add this to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "instagram": {
      "command": "python",
      "args": ["/path/to/ig-mcp/src/instagram_mcp_server.py"],
      "env": {
        "INSTAGRAM_ACCESS_TOKEN": "your_access_token"
      }
    }
  }
}
```

## Usage Examples

### Using with Claude Desktop

1. **Get Profile Information**:
```
Can you get my Instagram profile information?
```

2. **Analyze Recent Posts**:
```
Show me my last 5 Instagram posts and their engagement metrics
```

3. **Publish Content**:
```
Upload this image to my Instagram account with the caption "Beautiful sunset! #photography #nature"
```

### Using with Python MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to the Instagram MCP server
server_params = StdioServerParameters(
    command="python",
    args=["src/instagram_mcp_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Get profile information
        result = await session.call_tool("get_profile_info", {})
        print(result)
```

## API Endpoints Covered

### Profile Management
- Get business profile information
- Update profile details (future feature)

### Media Management
- Retrieve recent posts
- Get specific media details
- Upload and publish new content
- Delete media (future feature)

### Analytics & Insights
- Post engagement metrics (likes, comments, shares)
- Account insights (reach, impressions)
- Hashtag performance analysis

### Account Management
- List connected Facebook pages
- Switch between business accounts

## Rate Limiting & Best Practices

The server implements intelligent rate limiting to comply with Instagram's API limits:

- **Profile requests**: 200 calls per hour
- **Media requests**: 200 calls per hour  
- **Publishing**: 25 posts per day
- **Insights**: 200 calls per hour

### Best Practices
1. Cache frequently accessed data
2. Use batch requests when possible
3. Implement exponential backoff for retries
4. Monitor rate limit headers

## Error Handling

The server provides comprehensive error handling for common scenarios:

- **Authentication errors**: Invalid or expired tokens
- **Permission errors**: Missing required permissions
- **Rate limiting**: Automatic retry with backoff
- **Network errors**: Connection timeouts and retries
- **API errors**: Instagram-specific error responses

## Security Considerations

1. **Token Security**: Store access tokens securely
2. **Environment Variables**: Never commit tokens to version control
3. **HTTPS Only**: All API calls use HTTPS
4. **Token Refresh**: Implement automatic token refresh
5. **Audit Logging**: Log all API interactions

## Development

### Project Structure
```
ig-mcp/
├── src/
│   ├── instagram_mcp_server.py    # Main MCP server
│   ├── instagram_client.py        # Instagram API client
│   ├── models/                    # Data models
│   ├── tools/                     # MCP tools implementation
│   ├── resources/                 # MCP resources implementation
│   └── prompts/                   # MCP prompts implementation
├── tests/                         # Unit and integration tests
├── config/                        # Configuration files
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/

# Run specific test file
python -m pytest tests/test_instagram_client.py
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **"Invalid Access Token"**
   - Verify token is not expired
   - Check token permissions
   - Regenerate long-lived token

2. **"Rate Limit Exceeded"**
   - Wait for rate limit reset
   - Implement request queuing
   - Use batch requests

3. **"Permission Denied"**
   - Verify Instagram Business account setup
   - Check Facebook page connection
   - Review API permissions

### Debug Mode
Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/jlbadano/ig-mcp/issues)
- 📖 Documentation: [Wiki](https://github.com/jlbadano/ig-mcp/wiki)

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) by Meta
- [FastMCP](https://github.com/jlowin/fastmcp) for rapid MCP development 