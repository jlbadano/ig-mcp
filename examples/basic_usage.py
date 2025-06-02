#!/usr/bin/env python3
"""
Basic usage example for Instagram MCP Server.

This example demonstrates how to:
1. Connect to the Instagram MCP server
2. Use various tools to interact with Instagram API
3. Handle responses and errors
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demonstrate_profile_info(session: ClientSession):
    """Demonstrate getting profile information."""
    print("\n🔍 Getting Instagram profile information...")
    
    try:
        result = await session.call_tool("get_profile_info", {})
        data = json.loads(result[0].text)
        
        if data["success"]:
            profile = data["data"]
            print(f"✅ Profile retrieved successfully!")
            print(f"   Username: @{profile['username']}")
            print(f"   Name: {profile.get('name', 'N/A')}")
            print(f"   Followers: {profile.get('followers_count', 'N/A'):,}")
            print(f"   Following: {profile.get('follows_count', 'N/A'):,}")
            print(f"   Posts: {profile.get('media_count', 'N/A'):,}")
        else:
            print(f"❌ Failed to get profile: {data['error']}")
            
    except Exception as e:
        print(f"❌ Error getting profile: {str(e)}")


async def demonstrate_recent_posts(session: ClientSession):
    """Demonstrate getting recent posts."""
    print("\n📸 Getting recent Instagram posts...")
    
    try:
        result = await session.call_tool("get_media_posts", {"limit": 5})
        data = json.loads(result[0].text)
        
        if data["success"]:
            posts = data["data"]["posts"]
            print(f"✅ Retrieved {len(posts)} recent posts:")
            
            for i, post in enumerate(posts, 1):
                print(f"\n   Post {i}:")
                print(f"   ID: {post['id']}")
                print(f"   Type: {post['media_type']}")
                print(f"   Caption: {post.get('caption', 'No caption')[:50]}...")
                print(f"   Likes: {post.get('like_count', 0):,}")
                print(f"   Comments: {post.get('comments_count', 0):,}")
                print(f"   Posted: {post.get('timestamp', 'Unknown')}")
        else:
            print(f"❌ Failed to get posts: {data['error']}")
            
    except Exception as e:
        print(f"❌ Error getting posts: {str(e)}")


async def demonstrate_media_insights(session: ClientSession):
    """Demonstrate getting media insights."""
    print("\n📊 Getting media insights...")
    
    # First get a recent post to analyze
    try:
        result = await session.call_tool("get_media_posts", {"limit": 1})
        data = json.loads(result[0].text)
        
        if data["success"] and data["data"]["posts"]:
            media_id = data["data"]["posts"][0]["id"]
            print(f"   Analyzing post: {media_id}")
            
            # Get insights for this post
            insights_result = await session.call_tool("get_media_insights", {
                "media_id": media_id,
                "metrics": ["impressions", "reach", "likes", "comments"]
            })
            
            insights_data = json.loads(insights_result[0].text)
            
            if insights_data["success"]:
                insights = insights_data["data"]["insights"]
                print(f"✅ Retrieved insights for post {media_id}:")
                
                for insight in insights:
                    values = insight.get("values", [])
                    if values:
                        value = values[0].get("value", "N/A")
                        print(f"   {insight['title']}: {value:,}")
            else:
                print(f"❌ Failed to get insights: {insights_data['error']}")
        else:
            print("❌ No posts available for insights analysis")
            
    except Exception as e:
        print(f"❌ Error getting insights: {str(e)}")


async def demonstrate_account_insights(session: ClientSession):
    """Demonstrate getting account-level insights."""
    print("\n📈 Getting account insights...")
    
    try:
        result = await session.call_tool("get_account_insights", {
            "metrics": ["impressions", "reach", "profile_visits"],
            "period": "day"
        })
        data = json.loads(result[0].text)
        
        if data["success"]:
            insights = data["data"]["insights"]
            print(f"✅ Retrieved account insights:")
            
            for insight in insights:
                values = insight.get("values", [])
                if values:
                    value = values[0].get("value", "N/A")
                    print(f"   {insight['title']}: {value:,}")
        else:
            print(f"❌ Failed to get account insights: {data['error']}")
            
    except Exception as e:
        print(f"❌ Error getting account insights: {str(e)}")


async def demonstrate_resources(session: ClientSession):
    """Demonstrate accessing resources."""
    print("\n📋 Accessing Instagram resources...")
    
    try:
        # List available resources
        resources = await session.list_resources()
        print(f"✅ Available resources: {len(resources)}")
        
        for resource in resources:
            print(f"   • {resource.name}: {resource.description}")
        
        # Read profile resource
        print("\n   Reading profile resource...")
        profile_content = await session.read_resource("instagram://profile")
        profile_data = json.loads(profile_content)
        
        if "error" not in profile_data:
            print(f"   ✅ Profile resource loaded successfully")
            print(f"      Username: @{profile_data.get('username', 'N/A')}")
        else:
            print(f"   ❌ Error reading profile resource: {profile_data['error']}")
            
    except Exception as e:
        print(f"❌ Error accessing resources: {str(e)}")


async def demonstrate_prompts(session: ClientSession):
    """Demonstrate using prompts."""
    print("\n💬 Using Instagram prompts...")
    
    try:
        # List available prompts
        prompts = await session.list_prompts()
        print(f"✅ Available prompts: {len(prompts)}")
        
        for prompt in prompts:
            print(f"   • {prompt.name}: {prompt.description}")
        
        # Use content strategy prompt
        print("\n   Generating content strategy prompt...")
        strategy_prompt = await session.get_prompt("content_strategy", {
            "focus_area": "engagement",
            "time_period": "week"
        })
        
        print(f"   ✅ Content strategy prompt generated")
        print(f"      Length: {len(strategy_prompt)} characters")
        print(f"      Preview: {strategy_prompt[:200]}...")
        
    except Exception as e:
        print(f"❌ Error using prompts: {str(e)}")


async def validate_token(session: ClientSession):
    """Validate the access token."""
    print("\n🔐 Validating Instagram access token...")
    
    try:
        result = await session.call_tool("validate_access_token", {})
        data = json.loads(result[0].text)
        
        if data["success"]:
            is_valid = data["data"]["valid"]
            if is_valid:
                print("✅ Access token is valid!")
            else:
                print("❌ Access token is invalid!")
                return False
        else:
            print(f"❌ Token validation failed: {data['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating token: {str(e)}")
        return False
    
    return True


async def main():
    """Main demonstration function."""
    print("🚀 Instagram MCP Server - Basic Usage Example")
    print("=" * 50)
    
    # Set up server parameters
    server_script = Path(__file__).parent.parent / "src" / "instagram_mcp_server.py"
    
    if not server_script.exists():
        print(f"❌ Server script not found: {server_script}")
        print("   Make sure you're running this from the project root directory")
        return
    
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)]
    )
    
    try:
        # Connect to the MCP server
        print("🔌 Connecting to Instagram MCP server...")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                print("✅ Connected to Instagram MCP server!")
                
                # Validate token first
                if not await validate_token(session):
                    print("\n❌ Cannot proceed without valid access token")
                    print("   Please check your Instagram API credentials in .env file")
                    return
                
                # Run demonstrations
                await demonstrate_profile_info(session)
                await demonstrate_recent_posts(session)
                await demonstrate_media_insights(session)
                await demonstrate_account_insights(session)
                await demonstrate_resources(session)
                await demonstrate_prompts(session)
                
                print("\n🎉 All demonstrations completed successfully!")
                print("\nNext steps:")
                print("• Integrate with your MCP client (Claude Desktop, etc.)")
                print("• Explore advanced features like media publishing")
                print("• Build custom workflows using the available tools")
                
    except FileNotFoundError:
        print("❌ Python not found. Make sure Python is installed and in your PATH.")
    except Exception as e:
        print(f"❌ Error running demonstration: {str(e)}")
        print("\nTroubleshooting:")
        print("• Check that all dependencies are installed: pip install -r requirements.txt")
        print("• Verify your .env file has valid Instagram API credentials")
        print("• Ensure your Instagram Business Account is properly configured")


if __name__ == "__main__":
    asyncio.run(main()) 