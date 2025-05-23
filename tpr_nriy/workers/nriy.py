from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from tpr_nriy.workflows import get_all_workflows
from tpr_nriy.activities import get_all_activities

async def create_worker(client: Client):
    worker = Worker(
        client,
        task_queue="nriy",
        workflows=list(get_all_workflows().values()),
        activities=list(get_all_activities().values()),
        workflow_runner=SandboxedWorkflowRunner(
            restrictions=SandboxRestrictions.default.with_passthrough_all_modules()
        )
    )
    return worker
