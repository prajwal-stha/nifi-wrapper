import json
import yaml
import requests
from src.core.config import NIFI_IP, NIFI_USER, NIFI_PASSWORD, ROOT_CANVAS_ID
from src.services.receive_bearer import get_bearer_token


class ProcessorWorkflow():
    def __init__(self, token):
        yaml_path = "src/utils/helper.yaml"
        with open(yaml_path, "r") as f:
            yaml_contents = yaml.load(f, Loader=yaml.FullLoader)

        self.headers = yaml_contents["headers"]
        self.headers["Authorization"] = token
        self.create_processGroup = yaml_contents["create_processGroup"]
        self.create_processGroup["component"]["parentGroupId"] = ROOT_CANVAS_ID
        self.instance_template = yaml_contents['instance_template']
        self.data = f'username={NIFI_USER}&password={NIFI_PASSWORD}'

    def get_processors_from_dataflow(self, dataflow_id):
        """
            inputs: the id of dataflow
            action: gets all the processors, output ports and input ports from the dataflow
            output: returns the list of processors
        """
        all_processors = []

        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/processors", headers=self.headers,
                                data=self.data, verify=False)
        processors = json.loads(response.text)

        all_processors.extend(processors["processors"])

        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/process-groups", headers=self.headers, data=self.data, verify=False)
        processor_groups = json.loads(response.text)

        for processor in processor_groups["processGroups"]:
            pid = processor["id"]
            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{pid}/processors", headers=self.headers,
                                    data=self.data, verify=False)
            processor_group = json.loads(response.text)

            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{pid}/output-ports", headers=self.headers,
                                    data=self.data, verify=False)
            output_ports = json.loads(response.text)

            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{pid}/input-ports", headers=self.headers,
                                    data=self.data, verify=False)
            input_ports = json.loads(response.text)

            all_processors.extend(processor_group["processors"])
            all_processors.extend(output_ports["outputPorts"])
            all_processors.extend(input_ports["inputPorts"])
        return all_processors