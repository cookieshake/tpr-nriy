from temporalio.client import Client
import os

async def get_temporal_client():
    if not hasattr(get_temporal_client, "client"):
        get_temporal_client.client = await Client.connect(os.environ["TEMPORAL_HOST"])
    return get_temporal_client.client
