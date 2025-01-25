import requests
from typing import Optional, Dict, List
from datetime import datetime

class CerealeAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error ({status_code}): {detail}")

class CerealeClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.refresh_token = None

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if self.token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.token:
            kwargs['headers']['Authorization'] = f"Bearer {self.token}"

        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            raise CerealeAPIError(response.status_code, response.json().get('detail', 'Unknown error'))
            
        return response.json() if response.content else {}

    def login(self, phone: str, verification_code: str = "0000") -> Dict:
        """Login with phone number and verification code."""
        data = {
            "username": phone,
            "password": verification_code
        }
        response = self._make_request("POST", "/auth/token", data=data)
        self.token = response.get('access_token')
        return response

    def register(self, phone: str, user_type: str = "buyer") -> Dict:
        """Register a new user."""
        data = {
            "phone": phone,
            "user_type": user_type
        }
        return self._make_request("POST", "/auth/register", json=data)

    def verify(self, phone: str, code: str = "0000") -> Dict:
        """Verify phone number with code."""
        data = {
            "phone": phone,
            "code": code
        }
        response = self._make_request("POST", "/auth/verify", json=data)
        self.token = response.get('access_token')
        self.refresh_token = response.get('refresh_token')
        return response

    def refresh_token(self) -> Dict:
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        data = {"refresh_token": self.refresh_token}
        response = self._make_request("POST", "/auth/refresh", json=data)
        self.token = response.get('access_token')
        self.refresh_token = response.get('refresh_token')
        return response

    def me(self) -> Dict:
        """Get current user information."""
        return self._make_request("GET", "/auth/me")

    def complete_profile(self, profile_data: Dict) -> Dict:
        """Complete user profile."""
        return self._make_request("POST", "/auth/complete-profile", json=profile_data)

    # Listings
    def get_listings(self, skip: int = 0, limit: int = 10, **filters) -> List[Dict]:
        """Get all listings with optional filters."""
        params = {"skip": skip, "limit": limit, **filters}
        return self._make_request("GET", "/listings", params=params)

    def get_my_listings(self) -> List[Dict]:
        """Get current user's listings."""
        return self._make_request("GET", "/listings/my")

    def get_listing(self, listing_id: int) -> Dict:
        """Get specific listing details."""
        return self._make_request("GET", f"/listings/{listing_id}")

    def create_listing(self, listing_data: Dict, image_ids: List[int] = None, document_ids: List[int] = None) -> Dict:
        """Create a new listing."""
        params = {}
        if image_ids:
            params['image_ids'] = image_ids
        if document_ids:
            params['document_ids'] = document_ids
        return self._make_request("POST", "/listings/create", json=listing_data, params=params)

    def update_listing(self, listing_id: int, listing_data: Dict) -> Dict:
        """Update an existing listing."""
        return self._make_request("PUT", f"/listings/{listing_id}", json=listing_data)

    def delete_listing(self, listing_id: int) -> Dict:
        """Delete a listing."""
        return self._make_request("DELETE", f"/listings/{listing_id}")

    # Offers
    def create_offer(self, offer_data: Dict) -> Dict:
        """Create a new offer."""
        return self._make_request("POST", "/offers/create", json=offer_data)

    def get_sent_offers(self, status: Optional[str] = None) -> List[Dict]:
        """Get offers sent by current user."""
        params = {"status": status} if status else {}
        return self._make_request("GET", "/offers/sent", params=params)

    def get_received_offers(self, status: Optional[str] = None) -> List[Dict]:
        """Get offers received by current user."""
        params = {"status": status} if status else {}
        return self._make_request("GET", "/offers/received", params=params)

    # Orders
    def create_order(self, order_data: Dict) -> Dict:
        """Create a new order."""
        return self._make_request("POST", "/orders/create", json=order_data)

    def get_orders_as_buyer(self, status: Optional[str] = None) -> List[Dict]:
        """Get orders where current user is buyer."""
        params = {"status": status} if status else {}
        return self._make_request("GET", "/orders/send", params=params)

    def get_orders_as_seller(self, status: Optional[str] = None) -> List[Dict]:
        """Get orders where current user is seller."""
        params = {"status": status} if status else {}
        return self._make_request("GET", "/orders/received", params=params)

    # Images
    def upload_image(self, image_file) -> Dict:
        """Upload an image."""
        files = {"file": image_file}
        return self._make_request("POST", "/images/upload", files=files)

    # Documents
    def upload_document(self, document_file) -> Dict:
        """Upload a document."""
        files = {"file": document_file}
        return self._make_request("POST", "/documents/upload", files=files)

    # Favorites
    def add_to_favorites(self, listing_id: int) -> Dict:
        """Add a listing to favorites."""
        data = {"listing_id": listing_id}
        return self._make_request("POST", "/favorites/add", json=data)

    def remove_from_favorites(self, listing_id: int) -> Dict:
        """Remove a listing from favorites."""
        data = {"listing_id": listing_id}
        return self._make_request("DELETE", "/favorites/remove", json=data)

    def get_favorites(self) -> List[Dict]:
        """Get favorite listings."""
        return self._make_request("GET", "/favorites")