#!/usr/bin/env python3
"""
Main Vercel Serverless Entry Point for Digital Twin
This file handles all incoming requests to the Vercel deployment
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vercel_mcp_server import app

def handler(request, response):
    """
    Vercel serverless function handler
    This is the entry point for all requests to the application
    """
    return app
