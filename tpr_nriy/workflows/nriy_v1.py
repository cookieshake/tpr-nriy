from typing import Dict, Any
import asyncio
from pydantic import BaseModel
from temporalio import workflow
from temporalio.workflow import execute_activity

from tpr_nriy.activities.analyze_message import analyze_message
from tpr_nriy.activities.analyze_context import analyze_context
from tpr_nriy.activities.search_naver import search_naver
from tpr_nriy.activities.generate_response import generate_response

class NriyV1Input(BaseModel):
    history: str
    input: str
    channel_id: str

class NriyV1Output(BaseModel):
    do_reply: bool
    reply_message: str | None = None

@workflow.defn
class NriyV1Workflow:
    def __init__(self) -> None:
        self._logger = workflow.logger

    @workflow.run
    async def run(self, history: str, message: str) -> str:
        """
        Main workflow for processing messages and generating responses.
        
        Args:
            history: Chat history
            message: Current message
        
        Returns:
            str: Generated response
        """
        # Analyze message
        message_analysis = await execute_activity(
            analyze_message,
            message,
            start_to_close_timeout=30
        )
        
        if message_analysis["uses_profanity"]:
            self._logger.info("Message contains profanity, stopping workflow")
            return NriyV1Output(do_reply=False)
        
        # Get current context
        now_context = "현재 시간: " + workflow.now().isoformat()
        
        # Analyze context
        context_analysis = await execute_activity(
            analyze_context,
            history,
            message,
            start_to_close_timeout=30
        )
        
        # Prepare contexts
        contexts = {
            "now": {"context": now_context},
            "history": {"context": history}
        }
        
        # Perform searches concurrently
        search_tasks = []
        if context_analysis["news_search"]:
            search_tasks.append(execute_activity(
                search_naver,
                "news",
                context_analysis["query_string"],
                start_to_close_timeout=30
            ))
        
        if context_analysis["blog_search"]:
            search_tasks.append(execute_activity(
                search_naver,
                "blog",
                context_analysis["query_string"],
                start_to_close_timeout=30
            ))
        
        if context_analysis["web_search"]:
            search_tasks.append(execute_activity(
                search_naver,
                "web",
                context_analysis["query_string"],
                start_to_close_timeout=30
            ))
        
        # Wait for all searches to complete
        search_results = await asyncio.gather(*search_tasks)
        
        # Add results to contexts
        result_index = 0
        if context_analysis["news_search"]:
            contexts["news"] = {"context": search_results[result_index]}
            result_index += 1
        
        if context_analysis["blog_search"]:
            contexts["blog"] = {"context": search_results[result_index]}
            result_index += 1
        
        if context_analysis["web_search"]:
            contexts["web"] = {"context": search_results[result_index]}
        
        # Generate response
        response = await execute_activity(
            generate_response,
            history,
            message,
            contexts,
            start_to_close_timeout=30
        )
        
        return response 