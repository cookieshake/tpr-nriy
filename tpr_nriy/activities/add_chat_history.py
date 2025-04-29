from typing import Any, Dict
from datetime import datetime
import asyncio
from temporalio import activity
from tpr_nriy.common.pocketbase import PocketBaseClient

@activity.defn
async def add_chat_history(
    message_id: str,
    chat_id: str,
    chat_name: str,
    user_name: str,
    message: str
) -> str:
    """
    Adds a chat message to PocketBase.
    
    Args:
        chat_id: Unique identifier for the chat session
        message_id: Unique identifier for the message
        user_id: Unique identifier for the user
        message: Chat message content
    
    Returns:
        str: Message ID of the added message
    """
    # Prepare record data
    message_record = {
        "id": message_id,
        "chat_id": chat_id,
        "chat_name": chat_name,
        "user_name": user_name,
        "message": message
    }
    
    # Create PocketBase client and add records concurrently
    client = PocketBaseClient()
    await client.upsert_record("messages", message_id, message_record),
    
    return message_id 