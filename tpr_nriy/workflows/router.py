from datetime import timedelta
import json
from pydantic import BaseModel
from temporalio import workflow
from temporalio.common import RetryPolicy
from typing import List, Dict, Optional, Any

from tpr_nriy.activities.check_response_needed import check_response_needed
from tpr_nriy.activities.get_chat_history import get_chat_history
from tpr_nriy.activities.add_chat_history import add_chat_history

class NriyRouterInput(BaseModel):
    message_id: str
    chat_id: str
    chat_name: str
    user_id: str
    user_name: str
    message: str

class NriyRouterOutput(BaseModel):
    doReply: bool
    message: str

@workflow.defn
class RouterWorkflow:
    def _parse_input(self, input: str) -> NriyRouterInput:
        """
        Parse input data to NriyRouterInput.
        
        Args:
            input: Input data from chat
            
        Returns:
            NriyRouterInput: Parsed input data
        """
        input = json.loads(input)
        return NriyRouterInput(
            message_id=input["logId"],
            chat_id=input["channelId"],
            chat_name=input["room"],
            user_id=input["author"]["name"],
            user_name=input["author"]["name"],
            message=input["content"]
        )

    @workflow.run
    async def run(self, input: Dict[str, Any]) -> Dict:
        # Parse input
        parsed_input = self._parse_input(input)

        # Add response to PocketBase
        await workflow.execute_activity(
            add_chat_history,
            {
                "message_id": parsed_input.message_id,
                "chat_id": parsed_input.chat_id,
                "chat_name": parsed_input.chat_name,
                "user_id": parsed_input.user_id,
                "user_name": parsed_input.user_name,
                "message": parsed_input.message
            },
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )

        # Get existing chat history
        history = await workflow.execute_activity(
            get_chat_history,
            {
                "chat_id": parsed_input.chat_id,
                "limit": 15
            },
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )

        # Check if response is needed
        needs_response = await workflow.execute_activity(
            check_response_needed,
            {
                "message": parsed_input.message,
                "chat_history": history,
                "last_response_time": None
            },
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )

        if needs_response:
            # Generate response using nriy_v1 workflow
            response = await workflow.execute_child_workflow(
                "nriy_v1",
                {
                    "message": parsed_input.message,
                    "chat_history": history,
                    "user_id": parsed_input.user_id
                },
                id=f"nriy_v1-{parsed_input.message_id}",
                task_queue="nriy"
            )

            # Add response to PocketBase
            await workflow.execute_activity(
                add_chat_history,
                {
                    "message_id": f"msg-{workflow.now().timestamp()}",
                    "chat_id": parsed_input.chat_id,
                    "chat_name": parsed_input.chat_name,
                    "user_id": "assistant",
                    "user_name": "Assistant",
                    "message": response["response"]
                },
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3
                )
            )

            return NriyRouterOutput(
                doReply=True,
                message=response["response"]
            ).model_dump()
        
        return NriyRouterOutput(
            doReply=False,
            message=None
        ).model_dump()
