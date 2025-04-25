from typing import Dict, Any, List
from pydantic import BaseModel, Field
from temporalio import activity
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class ContextAnalysis(BaseModel):
    news_search: bool = Field(
        description="whether news search results would be helpful for answering"
    )
    blog_search: bool = Field(
        description="whether blog search results would be helpful for answering"
    )
    web_search: bool = Field(
        description="whether general web search results would be helpful for answering"
    )
    query_string: str = Field(
        description="suggested Korean search keyword or phrase to use if search is needed"
    )

@activity.defn
async def analyze_context(chat_history: str, message: str) -> Dict[str, Any]:
    """
    Analyzes chat history and current message to determine appropriate actions.
    
    Args:
        chat_history: Previous messages in the chat
        message: Current message to analyze
    
    Returns:
        Dict[str, Any]: Analysis results
    """
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a context analyzer. Analyze the chat history and current message to determine:
1. What actions would be helpful for responding
2. What information would be needed
3. What would be the best approach

Consider the context from chat history when making decisions."""),
        ("system", "Chat History:\n{chat_history}"),
        ("human", "Current Message: {message}")
    ])
    
    # Create chain with structured output
    chain = prompt | llm.with_structured_output(ContextAnalysis)
    
    # Run analysis
    result = await chain.ainvoke({
        "chat_history": chat_history,
        "message": message
    })
    
    return result.model_dump() 