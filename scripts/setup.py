#!/usr/bin/env python3
"""
Setup script for Instagram MCP Server.

This script helps users configure their Instagram MCP server by:
1. Validating Instagram API credentials
2. Setting up environment variables
3. Testing the connection
4. Generating MCP client configuration
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


class InstagramSetup:
    """Instagram MCP Server setup helper."""
    
    def __init__(self):
        self.config = {}
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env"
    
    def welcome(self):
        """Display welcome message."""
        console.print(Panel.fit(
            "[bold blue]Instagram MCP Server Setup[/bold blue]\n\n"
            "This setup wizard will help you configure your Instagram MCP server\n"
            "with the necessary API credentials and settings.",
            title="Welcome",
            border_style="blue"
        ))
    
    def collect_credentials(self):
        """Collect Instagram API credentials from user."""
        console.print("\n[bold yellow]Step 1: Instagram API Credentials[/bold yellow]")
        console.print("You'll need the following from your Facebook Developer account:")
        console.print("• Facebook App ID")
        console.print("• Facebook App Secret")
        console.print("• Long-lived Instagram Access Token")
        console.print("• Instagram Business Account ID (optional)")
        
        self.config["FACEBOOK_APP_ID"] = Prompt.ask(
            "\nEnter your Facebook App ID",
            password=False
        )
        
        self.config["FACEBOOK_APP_SECRET"] = Prompt.ask(
            "Enter your Facebook App Secret",
            password=True
        )
        
        self.config["INSTAGRAM_ACCESS_TOKEN"] = Prompt.ask(
            "Enter your Instagram Access Token",
            password=True
        )
        
        account_id = Prompt.ask(
            "Enter your Instagram Business Account ID (optional, press Enter to skip)",
            default=""
        )
        if account_id:
            self.config["INSTAGRAM_BUSINESS_ACCOUNT_ID"] = account_id
    
    def collect_settings(self):
        """Collect additional settings."""
        console.print("\n[bold yellow]Step 2: Server Settings[/bold yellow]")
        
        # API Version
        api_version = Prompt.ask(
            "Instagram API version",
            default="v19.0"
        )
        self.config["INSTAGRAM_API_VERSION"] = api_version
        
        # Rate limiting
        rate_limit = Prompt.ask(
            "Rate limit (requests per hour)",
            default="200"
        )
        self.config["RATE_LIMIT_REQUESTS_PER_HOUR"] = rate_limit
        
        # Logging
        log_level = Prompt.ask(
            "Log level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO"
        )
        self.config["LOG_LEVEL"] = log_level
        
        # Cache
        enable_cache = Confirm.ask("Enable caching?", default=True)
        self.config["CACHE_ENABLED"] = str(enable_cache).lower()
        
        if enable_cache:
            cache_ttl = Prompt.ask(
                "Cache TTL (seconds)",
                default="300"
            )
            self.config["CACHE_TTL_SECONDS"] = cache_ttl
    
    async def validate_credentials(self) -> bool:
        """Validate Instagram API credentials."""
        console.print("\n[bold yellow]Step 3: Validating Credentials[/bold yellow]")
        
        with console.status("[bold green]Testing Instagram API connection..."):
            try:
                # Test basic API access
                url = f"https://graph.facebook.com/v19.0/me"
                params = {
                    "access_token": self.config["INSTAGRAM_ACCESS_TOKEN"],
                    "fields": "id,name"
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        console.print(f"✅ API connection successful!")
                        console.print(f"   Connected as: {data.get('name', 'Unknown')}")
                        console.print(f"   User ID: {data.get('id', 'Unknown')}")
                        
                        # Test Instagram Business Account access if provided
                        if "INSTAGRAM_BUSINESS_ACCOUNT_ID" in self.config:
                            await self._test_instagram_account()
                        
                        return True
                    else:
                        error_data = response.json()
                        console.print(f"❌ API connection failed: {error_data}")
                        return False
                        
            except Exception as e:
                console.print(f"❌ Connection error: {str(e)}")
                return False
    
    async def _test_instagram_account(self):
        """Test Instagram Business Account access."""
        try:
            account_id = self.config["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
            url = f"https://graph.facebook.com/v19.0/{account_id}"
            params = {
                "access_token": self.config["INSTAGRAM_ACCESS_TOKEN"],
                "fields": "id,username,name,followers_count"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    console.print(f"✅ Instagram Business Account access successful!")
                    console.print(f"   Account: @{data.get('username', 'Unknown')}")
                    console.print(f"   Name: {data.get('name', 'Unknown')}")
                    console.print(f"   Followers: {data.get('followers_count', 'Unknown')}")
                else:
                    console.print(f"⚠️  Instagram Business Account access failed")
                    console.print("   You can still use the server, but some features may be limited")
                    
        except Exception as e:
            console.print(f"⚠️  Instagram account test error: {str(e)}")
    
    def save_env_file(self):
        """Save configuration to .env file."""
        console.print("\n[bold yellow]Step 4: Saving Configuration[/bold yellow]")
        
        env_content = []
        env_content.append("# Instagram MCP Server Configuration")
        env_content.append("# Generated by setup script\n")
        
        # Instagram API Configuration
        env_content.append("# Instagram API Configuration")
        for key in ["INSTAGRAM_ACCESS_TOKEN", "FACEBOOK_APP_ID", "FACEBOOK_APP_SECRET", "INSTAGRAM_BUSINESS_ACCOUNT_ID"]:
            if key in self.config:
                env_content.append(f"{key}={self.config[key]}")
        
        env_content.append("")
        
        # API Configuration
        env_content.append("# API Configuration")
        env_content.append(f"INSTAGRAM_API_VERSION={self.config.get('INSTAGRAM_API_VERSION', 'v19.0')}")
        env_content.append("INSTAGRAM_API_BASE_URL=https://graph.facebook.com")
        
        env_content.append("")
        
        # Rate Limiting
        env_content.append("# Rate Limiting Configuration")
        env_content.append(f"RATE_LIMIT_REQUESTS_PER_HOUR={self.config.get('RATE_LIMIT_REQUESTS_PER_HOUR', '200')}")
        env_content.append("RATE_LIMIT_POSTS_PER_DAY=25")
        env_content.append("RATE_LIMIT_ENABLE_BACKOFF=true")
        
        env_content.append("")
        
        # Logging
        env_content.append("# Logging Configuration")
        env_content.append(f"LOG_LEVEL={self.config.get('LOG_LEVEL', 'INFO')}")
        env_content.append("LOG_FORMAT=json")
        env_content.append("LOG_FILE=logs/instagram_mcp.log")
        
        env_content.append("")
        
        # Cache
        env_content.append("# Cache Configuration")
        env_content.append(f"CACHE_ENABLED={self.config.get('CACHE_ENABLED', 'true')}")
        env_content.append(f"CACHE_TTL_SECONDS={self.config.get('CACHE_TTL_SECONDS', '300')}")
        
        env_content.append("")
        
        # MCP Server
        env_content.append("# MCP Server Configuration")
        env_content.append("MCP_SERVER_NAME=instagram-mcp-server")
        env_content.append("MCP_SERVER_VERSION=1.0.0")
        env_content.append("MCP_TRANSPORT=stdio")
        
        # Write to file
        with open(self.env_file, "w") as f:
            f.write("\n".join(env_content))
        
        console.print(f"✅ Configuration saved to {self.env_file}")
    
    def generate_mcp_config(self):
        """Generate MCP client configuration."""
        console.print("\n[bold yellow]Step 5: MCP Client Configuration[/bold yellow]")
        
        server_path = str(self.project_root / "src" / "instagram_mcp_server.py")
        
        mcp_config = {
            "mcpServers": {
                "instagram": {
                    "command": "python",
                    "args": [server_path],
                    "env": {
                        "INSTAGRAM_ACCESS_TOKEN": self.config["INSTAGRAM_ACCESS_TOKEN"],
                        "FACEBOOK_APP_ID": self.config["FACEBOOK_APP_ID"],
                        "FACEBOOK_APP_SECRET": self.config["FACEBOOK_APP_SECRET"],
                        "LOG_LEVEL": self.config.get("LOG_LEVEL", "INFO")
                    }
                }
            }
        }
        
        if "INSTAGRAM_BUSINESS_ACCOUNT_ID" in self.config:
            mcp_config["mcpServers"]["instagram"]["env"]["INSTAGRAM_BUSINESS_ACCOUNT_ID"] = self.config["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
        
        config_file = self.project_root / "config" / "mcp_client_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, "w") as f:
            json.dump(mcp_config, f, indent=2)
        
        console.print(f"✅ MCP client configuration saved to {config_file}")
        
        # Show usage instructions
        console.print("\n[bold green]Setup Complete![/bold green]")
        console.print("\nTo use with Claude Desktop, add this to your Claude config:")
        console.print(f"[dim]{json.dumps(mcp_config, indent=2)}[/dim]")
    
    def show_next_steps(self):
        """Show next steps to the user."""
        console.print("\n[bold blue]Next Steps:[/bold blue]")
        
        table = Table(show_header=False, box=None)
        table.add_column("Step", style="bold yellow")
        table.add_column("Description")
        
        table.add_row("1.", "Install dependencies: pip install -r requirements.txt")
        table.add_row("2.", "Test the server: python src/instagram_mcp_server.py")
        table.add_row("3.", "Configure your MCP client (Claude Desktop, etc.)")
        table.add_row("4.", "Start using Instagram tools in your AI conversations!")
        
        console.print(table)
        
        console.print("\n[bold green]Documentation:[/bold green]")
        console.print("• README.md - Complete setup and usage guide")
        console.print("• config/mcp_client_config.json - MCP client configuration")
        console.print("• .env - Environment variables")
    
    async def run(self):
        """Run the setup process."""
        self.welcome()
        
        try:
            self.collect_credentials()
            self.collect_settings()
            
            # Validate credentials
            is_valid = await self.validate_credentials()
            if not is_valid:
                if not Confirm.ask("Credentials validation failed. Continue anyway?"):
                    console.print("Setup cancelled.")
                    return
            
            self.save_env_file()
            self.generate_mcp_config()
            self.show_next_steps()
            
        except KeyboardInterrupt:
            console.print("\n\nSetup cancelled by user.")
        except Exception as e:
            console.print(f"\n❌ Setup failed: {str(e)}")
            sys.exit(1)


async def main():
    """Main entry point."""
    setup = InstagramSetup()
    await setup.run()


if __name__ == "__main__":
    asyncio.run(main()) 