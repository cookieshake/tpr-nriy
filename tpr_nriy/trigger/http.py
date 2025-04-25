import os
from fastapi import FastAPI, HTTPException
from temporalio.client import Client
from typing import Dict, Any
import json
import importlib

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
            id=f"{workflow_name}-{input.get('logId', '')}",
            task_queue="nriy"
        )
        
        # Get result
        result = await handle.result()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
