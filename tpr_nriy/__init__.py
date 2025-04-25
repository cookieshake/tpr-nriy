from temporalio.client import Client
import os

temporal_client = Client.connect(os.environ["TEMPORAL_HOST"])
