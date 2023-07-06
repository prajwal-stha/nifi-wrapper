import json
import yaml
import requests
from src.core.config import NIFI_IP, NIFI_USER, NIFI_PASSWORD, ROOT_CANVAS_ID
from src.services.receive_bearer import get_root_canvas_id
from src.services.user_workflow import ConfigureUser
from src.services.processor_workflow import ProcessorWorkflow


class ManagementFlow():
    def __init__(self, token):
        yaml_path = "src/utils/helper.yaml"
        with open(yaml_path, "r") as f:
            yaml_contents = yaml.load(f, Loader=yaml.FullLoader)

        self.root_canvas_id = get_root_canvas_id(token)

        self.headers = yaml_contents["headers"]
        self.headers["Authorization"] = token
        self.data = f'username={NIFI_USER}&password={NIFI_PASSWORD}'
        self.configure_user = ConfigureUser(token)
        self.processor_workflow = ProcessorWorkflow(token)

    def delete_flowfiles(self):
        all_connections = []

        # get root id
        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/root", headers=self.headers, data=self.data,
                                verify=False)
        root_process = json.loads(response.text)
        root_id = root_process["id"]

        # get root process groups
        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{root_id}/process-groups", headers=self.headers,
                                data=self.data, verify=False)
        root_process_groups = json.loads(response.text)

        # iterate through the process groups of the root
        for root_process in root_process_groups["processGroups"]:
            process_group_id = root_process["id"]

            # get all the dataflow inside process group
            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{process_group_id}/process-groups",
                                    headers=self.headers, data=self.data, verify=False)
            dataflows = json.loads(response.text)

            for dataflow in dataflows["processGroups"]:
                dataflow_id = dataflow["id"]
                # get connections of the dataflow
                response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/connections",
                                        headers=self.headers, data=self.data, verify=False)
                connections_1 = json.loads(response.text)
                all_connections.extend(connections_1["connections"])

                # get the process groups inside dataflow
                response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/process-groups",
                                        headers=self.headers, data=self.data, verify=False)
                process_groups = json.loads(response.text)

                # get all the connections inside the process groups
                for process_group in process_groups["processGroups"]:
                    pg_id = process_group["id"]
                    response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{pg_id}/connections",
                                            headers=self.headers, data=self.data, verify=False)
                    connections = json.loads(response.text)
                    all_connections.extend(connections["connections"])

        for i in range(len(all_connections)):
            connection_id = all_connections[i]["id"]
            drop_req = requests.post(f"{NIFI_IP}/nifi-api/flowfile-queues/{connection_id}/drop-requests",
                                     headers=self.headers, verify=False)

        return drop_req.status_code

    def delete_all_dataflows(self, process_group_id):
        # get all process groups inside the dataflow
        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{process_group_id}/process-groups",
                                headers=self.headers, data=self.data, verify=False)
        processor_groups = json.loads(response.text)

        for dataflow in processor_groups["processGroups"]:
            dataflow_id = dataflow["id"]
            all_processors = self.processor_workflow.get_processors_from_dataflow(dataflow_id)
            self.configure_user.stop_all_processors(all_processors)
            self.configure_user.disable_controller_services(dataflow_id)
            self.configure_user.delete_flowfiles(dataflow_id)

            response = self.configure_user.delete_dataflow(dataflow_id)
        return response