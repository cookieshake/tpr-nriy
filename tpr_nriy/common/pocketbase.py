import os
from typing import Any, Dict, List, Tuple
from datetime import datetime
import httpx
import asyncio

# PocketBase 설정
POCKETBASE_URL = os.getenv("POCKETBASE_URL", "http://localhost:8090")

class PocketBaseClient:
    def __init__(self, base_url: str = POCKETBASE_URL):
        self.base_url = base_url.rstrip("/")
    
    async def create_record(
        self,
        collection: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a new record in the specified collection.
        
        Args:
            collection: Collection name
            data: Record data to create
        
        Returns:
            Dict[str, Any]: Created record
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/collections/{collection}/records",
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def upsert_record(
        self,
        collection: str,
        id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Upserts a record in the specified collection.
        
        Args:
            collection: Collection name
            id: Record ID
            data: Record data to upsert
        
        Returns:
            Dict[str, Any]: Upserted record
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api/collections/{collection}/records",
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_records(
        self,
        collection: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Gets records from the specified collection with filtering and sorting.
        
        Args:
            collection: Collection name
            params: Query parameters (filter, sort, limit, expand, etc.)
        
        Returns:
            List[Dict[str, Any]]: List of records
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/collections/{collection}/records",
                params=params
            )
            response.raise_for_status()
            return response.json()["items"]
    
    async def get_record(
        self,
        collection: str,
        id: str
    ) -> Dict[str, Any]:
        """
        Gets a record by ID from the specified collection.
        
        Args:
            collection: Collection name
            id: Record ID
        
        Returns:
            Dict[str, Any]: Retrieved record
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/collections/{collection}/records/{id}"
            )
            response.raise_for_status()
            return response.json()
    
    async def update_record(
        self,
        collection: str,
        id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates a record in the specified collection.
        
        Args:
            collection: Collection name
            id: Record ID
            data: Record data to update
        
        Returns:
            Dict[str, Any]: Updated record
        """
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/collections/{collection}/records/{id}",
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_record(
        self,
        collection: str,
        id: str
    ) -> bool:
        """
        Deletes a record from the specified collection.
        
        Args:
            collection: Collection name
            id: Record ID
        
        Returns:
            bool: True if successful
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/collections/{collection}/records/{id}"
            )
            response.raise_for_status()
            return True