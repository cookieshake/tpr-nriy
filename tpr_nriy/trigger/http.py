from typing import Dict, Any
import json
import uuid
from datetime import timedelta

from fastapi import FastAPI, HTTPException
from temporalio.common import RetryPolicy
from temporalio.api.enums.v1 import EventType
import anyio

from tpr_nriy import get_temporal_client

app = FastAPI(title="TPR NRIY HTTP Trigger")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/workflows/{workflow_name}")
async def trigger_workflow(workflow_name: str, input: Dict[str, Any]):
    """
    Trigger a workflow by name.
    
    Args:
        workflow_name: Name of the workflow to trigger
        input: Input data for the workflow
    
    Returns:
        Dict: Workflow execution result
    """
    try:
        # Create Temporal client
        client = await get_temporal_client()
        
        # Start workflow
        handle = await client.start_workflow(
            workflow_name,
            json.dumps(input),
            id=str(uuid.uuid4()),
            task_queue="nriy",
            execution_timeout=timedelta(seconds=300),
            retry_policy=RetryPolicy(
                maximum_attempts=1
            )
        )
        
        while True:
            history = await handle.fetch_history()
            
            completed_events = [e for e in history.events if e.event_type == EventType.EVENT_TYPE_WORKFLOW_TASK_COMPLETED]
            failed_events = [e for e in history.events if e.event_type in [EventType.EVENT_TYPE_WORKFLOW_TASK_FAILED, EventType.EVENT_TYPE_WORKFLOW_TASK_TIMED_OUT]]
            
            if completed_events:
                break
            elif failed_events:
                await handle.terminate(reason="Workflow Task Failed")
                raise HTTPException(status_code=500, detail=failed_events[0].workflow_task_failed_event_attributes.failure.cause.message)
            
            await anyio.sleep(0.5)
        
        # Get result
        result = await handle.result()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
