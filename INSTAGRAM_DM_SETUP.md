# Instagram Direct Messaging Setup Guide

## Overview

Instagram Direct Messaging (DM) features in this MCP server allow you to:
- **Read conversations**: List DM conversations from your Instagram Business account
- **Read messages**: View messages within specific conversations
- **Send messages**: Reply to DMs (within 24-hour window)

**⚠️ IMPORTANT**: These features require **Advanced Access** from Meta for the `instagram_manage_messages` permission. This is NOT available by default and requires Meta's App Review approval.

## Current Status

The DM features are **fully implemented** in this server, but you'll encounter errors until Meta approves your Advanced Access request:

```
Error: (#2) Service temporarily unavailable
```

This error indicates that the `instagram_manage_messages` permission is not yet approved for Advanced Access.

## Required Permissions

### Standard Access (Default)
These permissions work immediately after OAuth connection:
- ✅ `instagram_basic` - Profile and media access
- ✅ `instagram_content_publish` - Post images/videos
- ✅ `instagram_manage_insights` - Analytics data
- ✅ `instagram_manage_comments` - Comment management
- ✅ `pages_show_list` - List Facebook pages
- ✅ `pages_read_engagement` - Page engagement metrics
- ✅ `pages_manage_metadata` - Page metadata
- ✅ `pages_read_user_content` - User-generated content
- ✅ `business_management` - Business account management

### Advanced Access (Requires App Review)
These permissions require Meta's approval:
- ⏳ `instagram_manage_messages` - **Required for all DM features**

## Prerequisites

Before requesting Advanced Access:

1. **Instagram Business Account** connected to a Facebook Page
2. **Facebook App** with Instagram Graph API product added
3. **All Standard Access permissions** working correctly
4. **Privacy Policy URL** publicly accessible
5. **App Use Case** clearly documented
6. **Screen recording** demonstrating your app's DM functionality

## App Review Process

### Step 1: Development Mode (Current Status)

Your app is currently in **Development Mode**, which means:
- ✅ Standard Access permissions work for all users
- ❌ Advanced Access permissions only work for app developers/testers
- ❌ DM features will fail with "#2 Service temporarily unavailable" error

**What you can do**:
- Test all non-DM features (profile, media, insights, publishing)
- Prepare your App Review submission
- Document your use case for DMs

### Step 2: Request Advanced Access

1. **Go to Facebook App Dashboard**:
   - Navigate to [developers.facebook.com/apps](https://developers.facebook.com/apps)
   - Select your app
   - Go to **App Review** → **Permissions and Features**

2. **Find `instagram_manage_messages`**:
   - Search for "instagram_manage_messages"
   - Click **Request Advanced Access**

3. **Provide Required Information**:

   **App Verification**:
   - Privacy Policy URL (must be publicly accessible)
   - App Icon and Category
   - Business Verification (if applicable)

   **Use Case Description**:
   ```
   Use Case: AI-Powered Instagram Customer Support Assistant

   Our application uses the Instagram Messaging API to provide AI-powered
   customer support through Instagram DMs. The AI assistant helps businesses:

   1. Read incoming customer inquiries (get_conversations, get_conversation_messages)
   2. Send automated responses within the 24-hour messaging window (send_dm)
   3. Provide context-aware replies using AI language models

   DM features are essential for our core functionality as a customer support
   automation tool. Without message access, our application cannot fulfill its
   primary purpose.
   ```

   **Screen Recording Requirements**:
   - Show OAuth flow connecting Instagram account
   - Demonstrate reading conversations
   - Show reading messages from a conversation
   - Demonstrate sending a reply message
   - Total duration: 2-5 minutes
   - Resolution: 1280x720 or higher
   - Format: MP4, MOV, or WebM

4. **Submit for Review**:
   - Click **Submit** and wait for Meta's review
   - Review typically takes **3-7 business days**

### Step 3: Review Timeline

**Typical Timeline**:
- **Submission**: Immediate
- **Under Review**: 3-7 business days
- **Additional Info Requested**: 1-3 days for response
- **Approval**: Immediate after meeting requirements
- **Rejection**: Can resubmit after addressing issues

**During Review**:
- ✅ Continue using Standard Access features
- ✅ Test with developer/tester accounts
- ❌ DM features unavailable for production users

**After Approval**:
- ✅ DM features work for all users
- ✅ App can go to Live Mode
- ✅ Full production deployment

## Testing Before Approval

### What Works (Standard Access)
```python
# ✅ These work immediately
client.get_profile_info()
client.get_media_posts()
client.get_media_insights(media_id)
client.publish_media(request)
client.get_account_insights()
client.get_account_pages()
```

### What Requires Advanced Access
```python
# ❌ These fail with "#2 Service temporarily unavailable"
client.get_conversations(page_id)
client.get_conversation_messages(conversation_id)
client.send_dm(request)
```

### Testing with App Roles

Add testers to your app to test DM features before approval:

1. **Add Testers**:
   - Go to **Roles** in your Facebook App Dashboard
   - Add users as **Developers**, **Testers**, or **Admins**
   - They must accept the role invitation

2. **Tester Limitations**:
   - ⚠️ Even testers will get "#2" error in Development Mode
   - Advanced Access permissions require approval even for testers
   - Only Standard Access permissions work for testing

## Common Errors

### Error: (#2) Service temporarily unavailable

**Cause**: `instagram_manage_messages` requires Advanced Access from Meta.

**Solution**: Submit App Review request for Advanced Access (see Step 2 above).

**Temporary Workaround**: None - this permission REQUIRES Meta approval.

**Status Check**: Verify in App Dashboard → App Review → Permissions and Features.

### Error: (#10) To use 'Messenger Platform', your use of this endpoint must be reviewed

**Cause**: Similar to #2, indicates Advanced Access not approved.

**Solution**: Complete App Review process.

### Error: (#200) Requires business_management permission

**Cause**: Missing `business_management` scope in OAuth configuration.

**Solution**: This is a Standard Access permission - add to OAuth scopes and reconnect account.

### Error: User must be an authenticated Instagram account

**Cause**: Instagram account not properly linked to Facebook Page.

**Solution**:
1. Ensure Instagram account is a **Business** or **Creator** account
2. Link Instagram account to a Facebook Page you own
3. Reconnect via OAuth

### Error: Message must be sent within 24 hours of user's last message

**Cause**: Instagram's 24-hour messaging window restriction.

**Solution**: This is an Instagram platform limitation. You can only reply to messages within 24 hours of the user's last message.

## Production Deployment Checklist

Before deploying to production with DM features:

- [ ] App Review approved for `instagram_manage_messages`
- [ ] App switched to **Live Mode** (not Development Mode)
- [ ] Privacy Policy URL publicly accessible
- [ ] Error handling implemented for all DM API calls
- [ ] 24-hour window logic implemented in your application
- [ ] Rate limiting respected (200 calls/hour for Instagram API)
- [ ] OAuth token refresh logic implemented (60-day expiration)
- [ ] Logging and monitoring for DM operations
- [ ] User consent and data protection compliance (GDPR, etc.)

## Best Practices

### Message Handling

1. **Respect 24-Hour Window**: Always check message timestamp before attempting to reply
2. **Handle Errors Gracefully**: Show clear messages when DMs aren't available yet
3. **Rate Limiting**: Instagram API has 200 calls/hour limit
4. **User Privacy**: Respect user's message privacy and data protection

### Error Messages

Provide clear feedback to users about Advanced Access status:

```python
try:
    conversations = await client.get_conversations()
except InstagramAPIError as e:
    if "#2" in str(e) or "unavailable" in str(e).lower():
        print(
            "Instagram Direct Messaging is not yet available. "
            "This feature requires Advanced Access approval from Meta. "
            "Please see INSTAGRAM_DM_SETUP.md for details."
        )
    else:
        print(f"Error: {e}")
```

### Development Workflow

1. **Phase 1**: Deploy without DM features (Standard Access only)
2. **Phase 2**: Submit App Review for Advanced Access
3. **Phase 3**: Deploy DM features after approval
4. **Phase 4**: Monitor usage and maintain compliance

## Additional Resources

- [Instagram Messaging API Documentation](https://developers.facebook.com/docs/messenger-platform/instagram)
- [App Review Guidelines](https://developers.facebook.com/docs/app-review)
- [Business Verification](https://developers.facebook.com/docs/development/release/business-verification)
- [Platform Terms](https://developers.facebook.com/terms)
- [Instagram Platform Policy](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/overview)

## Support

If you encounter issues:

1. **Check App Review Status**: App Dashboard → App Review
2. **Review Submission Guidelines**: Ensure all requirements met
3. **Provide Complete Information**: Detailed use case and screen recording
4. **Contact Meta Support**: If review is taking longer than expected

## Timeline Summary

| Stage | Duration | DM Features Status |
|-------|----------|-------------------|
| Development Mode | Ongoing | ❌ Not Available |
| App Review Submission | Immediate | ❌ Not Available |
| Under Review | 3-7 days | ❌ Not Available |
| Approved | Immediate | ✅ Available |
| Live Mode | Ongoing | ✅ Available |

**Current Stage**: Development Mode - Submit App Review to proceed.
