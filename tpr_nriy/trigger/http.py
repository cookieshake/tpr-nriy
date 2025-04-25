from fastapi import FastAPI, HTTPException
from temporalio.client import Client
from typing import Dict, Any
import json
import importlib

app = FastAPI(title="TPR NRIY HTTP Trigger")

async def get_activity_function(activity_name: str):
    """
    Get activity function by name.
    
    Args:
        activity_name: Name of the activity
    
    Returns:
        Callable: Activity function
    """
    try:
        # Import activity module
        module = importlib.import_module(f"tpr_nriy.activities.{activity_name}")
        # Get activity function
        return getattr(module, activity_name)
    except (ImportError, AttributeError) as e:
        raise HTTPException(status_code=404, detail=f"Activity {activity_name} not found: {str(e)}")

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
        client = await Client.connect("localhost:7233")
        
        # Start workflow
        handle = await client.start_workflow(
            workflow_name,
            json.dumps(input),
            id=f"{workflow_name}-{input.get('logId', '')}",
            task_queue="nriy-task-queue"
        )
        
        # Get result
        result = await handle.result()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/activities/{activity_name}")
async def trigger_activity(activity_name: str, input: Dict[str, Any]):
    """
    Trigger an activity by name.
    
    Args:
        activity_name: Name of the activity to trigger
        input: Input data for the activity
    
    Returns:
        Any: Activity execution result
    """
    try:
        # Get activity function
        activity_func = await get_activity_function(activity_name)
        
        # Execute activity
        result = await activity_func(**input)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
