# Instagram API Authentication - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites Checklist
- [ ] Instagram Business Account (not Personal)
- [ ] Facebook Page connected to Instagram
- [ ] Facebook Developer Account

### Step-by-Step Setup

#### 1. Create Facebook App (2 minutes)
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **"Create App"** → **"Business"** → **"Next"**
3. Enter app name: `"My Instagram MCP Server"`
4. Enter your email address
5. Click **"Create App"**

#### 2. Add Instagram Products (1 minute)
1. In app dashboard, click **"Add Product"**
2. Find **"Instagram Graph API"** → Click **"Set Up"**
3. Find **"Instagram Basic Display"** → Click **"Set Up"**

#### 3. Get Your Credentials (1 minute)
1. Go to **Settings** → **Basic**
2. Copy **App ID** and **App Secret**
3. Keep App Secret secure! 🔒

#### 4. Generate Access Token (1 minute)
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Select your app from dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   - `pages_show_list`
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_insights`
5. Copy the generated token

#### 5. Get Instagram Business Account ID (30 seconds)
1. In Graph API Explorer, make GET request to: `/me/accounts`
2. Find your Facebook Page in response
3. Copy the `access_token` for your page
4. Make GET request to: `/{page-id}?fields=instagram_business_account`
5. Copy the Instagram Business Account ID

## 🔧 Environment Setup

Create `.env` file in your project root:

```env
# Required Credentials
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id_here

# Optional Configuration
INSTAGRAM_API_VERSION=v19.0
RATE_LIMIT_REQUESTS_PER_HOUR=200
CACHE_ENABLED=true
LOG_LEVEL=INFO
```

## ✅ Test Your Setup

Run the setup script:
```bash
python scripts/setup.py
```

Or test manually:
```python
import requests
import os

# Test API connection
access_token = "YOUR_ACCESS_TOKEN"
response = requests.get(f'https://graph.facebook.com/v19.0/me?access_token={access_token}')
print(response.json())
```

## 🚨 Common Issues & Solutions

### Issue: "Invalid OAuth access token"
**Solution:**
- Check if token expired (short-lived tokens expire in 1 hour)
- Generate long-lived token (60 days):
```bash
curl "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
```

### Issue: "Instagram account not found"
**Solution:**
- Ensure Instagram account is Business (not Personal)
- Verify Instagram is connected to Facebook Page
- Check Instagram Business Account ID is correct

### Issue: "Insufficient permissions"
**Solution:**
- Re-generate token with all required permissions
- Check app is in correct mode (Development vs Live)
- Verify permissions in Facebook App settings

### Issue: App in Development Mode
**Solution:**
- For testing: Development mode is fine
- For production: Submit app for review to go Live
- Add test users in App Roles for development

## 🔄 Token Management

### Long-Lived Tokens
- Short-lived: 1 hour expiration
- Long-lived: 60 days expiration
- Always use long-lived for production

### Token Refresh
```python
def refresh_token(current_token, app_id, app_secret):
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': current_token
    }
    response = requests.get(url, params=params)
    return response.json().get('access_token')
```

## 📋 Required Permissions Explained

| Permission | Purpose |
|------------|---------|
| `instagram_basic` | Read basic profile info, media |
| `instagram_content_publish` | Upload and publish content |
| `instagram_manage_insights` | Access analytics and insights |
| `pages_show_list` | List connected Facebook pages |
| `pages_read_engagement` | Read page engagement metrics |

## 🔗 Useful Links

- [Facebook Developers](https://developers.facebook.com)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer)
- [Instagram Graph API Docs](https://developers.facebook.com/docs/instagram-api)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken)

## 💡 Pro Tips

1. **Save your credentials securely** - Use environment variables
2. **Test with Graph API Explorer** - Validate permissions before coding
3. **Monitor token expiration** - Set up automatic refresh
4. **Use Development mode** - For testing and development
5. **Read the docs** - Instagram API has specific requirements

## 🆘 Need Help?

1. Check the [troubleshooting section](README.md#troubleshooting) in README
2. Use Facebook's [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken)
3. Review Instagram API [error codes](https://developers.facebook.com/docs/instagram-api/reference/error-codes)
4. Run the setup script: `python scripts/setup.py` 