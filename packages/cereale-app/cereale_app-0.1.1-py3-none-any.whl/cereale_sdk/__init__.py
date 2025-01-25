from .client import CerealeClient

__version__ = "0.1.1"
__all__ = ["CerealeClient"]

# cereale_sdk/client.py
import requests
from typing import Optional, Dict, List
from datetime import datetime

class CerealeAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error ({status_code}): {detail}")

class CerealeClient:
    def __init__(self, base_url: str = "https://api.cereale.app"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.refresh_token = None