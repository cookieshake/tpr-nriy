from temporalio import activity

@activity.defn
async def check_response_needed(message: str) -> bool:
    """
    Determines if the bot should respond to the message.
    
    Args:
        message: The message to check
    
    Returns:
        bool: True if the message starts with '/', False otherwise
    """
    return message.startswith("/") 