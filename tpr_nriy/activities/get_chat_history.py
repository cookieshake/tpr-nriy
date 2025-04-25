from typing import List, Dict, Any
import asyncio
from temporalio import activity
from tpr_nriy.common.pocketbase import PocketBaseClient

@activity.defn
async def get_chat_history(chat_id: str, limit: int = 15) -> list[dict[str, Any]]:
    """
    Retrieves recent messages for a given chat.
    
    Args:
        chat_id: Unique identifier for the chat session
        limit: Number of messages to retrieve (default: 15)
    
    Returns:
        List[Dict[str, Any]]: List of messages with user information
    """
    client = PocketBaseClient()
    
    # Get messages
    messages = await client.get_records(
        "messages",
        {
            "filter": f"chat_id = '{chat_id}'",
            "sort": "-created",
            "limit": limit,
            "expand": "user_id"
        }
    )
    
    # Fetch user information
    unique_user_ids = list(set(message["user_id"] for message in messages))
    users = await asyncio.gather(*(client.get_record("users", user_id) for user_id in unique_user_ids))
    user_map = {user["id"]: user for user in users}
    
    # Add user information to messages
    for message in messages:
        message["user"] = user_map[message["user_id"]]
    
    return messages
