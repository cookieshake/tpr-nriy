from typing import Dict, Any
from textwrap import dedent
from pydantic import BaseModel
from temporalio import activity
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class Context(BaseModel):
    context: str

class Contexts(BaseModel):
    now: Context
    history: Context | None = None
    news: Context | None = None
    blog: Context | None = None
    web: Context | None = None

@activity.defn
async def generate_response(
    history: str,
    message: str,
    contexts: Dict[str, Any]
) -> str:
    """
    Generates a response based on the input and contexts.
    
    Args:
        history: Chat history
        message: Current message
        contexts: Various context information (now, history, news, blog, web)
    
    Returns:
        Dict[str, str]: Generated response
    """
    # Initialize LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", dedent("""
            You are participating in a group chat with multiple people.
            You should listen to what others are saying and respond appropriately and intelligently.
            Pay attention to the flow of conversation. Your name is "나란잉여".
            Use extremely polite and formal language, as if a commoner is speaking to a king.
        """)),
        ("user", dedent("""
            Please refer to the following information:
            ```
            # Current Information
            {now_context}

            # Past Conversation
            {history_context}

            # Search Results
            {news_context}
            {blog_context}
            {web_context}
            ```

            The following conversation is currently taking place in the chat:
            ```
            {history}
            ```

            In this situation, when the following message is added, generate the most appropriate response.
            Do not include any other text. Do not start with "나란잉여: ".
            ```
            {message}
            ```
        """))
    ])
    
    # Parse contexts
    contexts = Contexts.model_validate(contexts)
    
    # Format context strings
    news_context = contexts.news.context if contexts.news else ""
    blog_context = contexts.blog.context if contexts.blog else ""
    web_context = contexts.web.context if contexts.web else ""
    history_context = contexts.history.context if contexts.history else ""
    
    # Generate response
    response = await prompt | llm.ainvoke({
        "now_context": contexts.now.context,
        "history_context": history_context,
        "news_context": news_context,
        "blog_context": blog_context,
        "web_context": web_context,
        "history": history,
        "message": message
    })
        
    return response.content