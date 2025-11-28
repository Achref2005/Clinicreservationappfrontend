"""
MCP (Model Context Protocol) client for enhanced AI agent capabilities
"""
import httpx
from typing import Dict, Optional, List
from app.config import settings
import json

class MCPClient:
    """Client for interacting with MCP server"""
    
    def __init__(self):
        self.base_url = settings.MCP_SERVER_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_context(self, query: str) -> Dict:
        """Get context from MCP server for a query"""
        try:
            response = await self.client.post(
                f"{self.base_url}/context",
                json={"query": query}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"MCP client error: {e}")
        
        return {"context": None}
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute a tool via MCP"""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=parameters
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"MCP tool execution error: {e}")
        
        return {"result": None, "error": "Tool execution failed"}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()





