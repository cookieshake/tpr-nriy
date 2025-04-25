import os
from tpr_nriy.workers import get_worker, worker_registry
from tpr_nriy.trigger.http import app
from tpr_nriy import get_temporal_client
import uvicorn
import anyio

async def run_worker(worker_name: str, task_queue_name: str):
    """
    Run a worker.
    
    Args:
        worker_name: Name of the worker to run
        task_queue_name: Name of the task queue
    """
    try:
        temporal_client = await get_temporal_client()
        # Get worker function
        worker_func = get_worker(temporal_client)
        
        # Run worker
        print(f"Starting worker '{worker_name}'... (task_queue: {task_queue_name})")
        await worker_func(task_queue_name)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Available workers: {', '.join(worker_registry.keys())}")

async def run_trigger():
    """
    Run the HTTP trigger.
    """
    host = os.getenv("TRIGGER_HOST", "0.0.0.0")
    port = int(os.getenv("TRIGGER_PORT", "8000"))
    
    print(f"Starting HTTP Trigger... (host: {host}, port: {port})")
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Get mode from environment variable
    mode = os.getenv("MODE", "worker")
    
    if mode == "worker":
        # Get worker configuration
        worker_name = os.getenv("WORKER_NAME", "hello")
        task_queue_name = os.getenv("TASK_QUEUE_NAME", f"{worker_name}")
        
        # Run worker
        await run_worker(worker_name, task_queue_name)
    elif mode == "trigger":
        # Run trigger
        await run_trigger()
    else:
        print(f"Error: Unknown mode '{mode}'")
        print("Available modes: worker, trigger")

if __name__ == "__main__":
    anyio.run(main)
