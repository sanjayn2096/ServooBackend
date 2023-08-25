# BigtableClient.py
from google.cloud import bigtable


class BigtableClient:
    def __init__(self, project_id, instance_id):
        self.client = bigtable.Client(project=project_id, admin=True)
        self.instance = self.client.instance(instance_id)
