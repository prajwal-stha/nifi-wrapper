import json
import yaml
import requests
from src.core.config import NIFI_IP, ROOT_CANVAS_ID, NIFI_USER, NIFI_PASSWORD
from src.services.receive_bearer import get_bearer_token

class Metrics():
    def __init__(self, token):
        yaml_path = "src/utils/helper.yaml"
        with open(yaml_path, "r") as f:
            yaml_contents = yaml.load(f, Loader=yaml.FullLoader)

        self.headers = yaml_contents["headers"]
        self.headers["Authorization"] = token
        self.data = f'username={NIFI_USER}&password={NIFI_PASSWORD}'

    def get_queued_flow_files(self, dataflow_id):
        """
            input: the id of dataflow
            output: total number of flow files in queue
        """
        response = requests.get(f"{NIFI_IP}/nifi-api/flow/process-groups/{dataflow_id}/status", headers=self.headers,
                                data=self.data, verify=False)
        if response.ok:
            status = json.loads(response.text)

            queued_flow_files = status["processGroupStatus"]["aggregateSnapshot"]["flowFilesQueued"]

            return queued_flow_files
        return 0