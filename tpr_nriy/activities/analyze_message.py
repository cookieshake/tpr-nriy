from typing import Dict, Any
from pydantic import BaseModel, Field
from temporalio import activity
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class MessageAnalysis(BaseModel):
    uses_profanity: bool = Field(
        description="Indicates whether the input text contains profanity or offensive language."
    )

@activity.defn
async def analyze_message(message: str) -> Dict[str, Any]:
    """
    Analyzes a message using LLM to extract various characteristics.
    
    Args:
        message: The message to analyze
    
    Returns:
        Dict[str, Any]: Analysis results
    """
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a message analysis system. Analyze the given message and provide structured information."),
        ("human", "{message}")
    ])
    
    # Create chain with structured output
    chain = prompt | llm.with_structured_output(MessageAnalysis)
    
    # Run analysis
    result = await chain.ainvoke({"message": message})
    
    return result.model_dump()
