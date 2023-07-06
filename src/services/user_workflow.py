import yaml
import json
import requests
from src.core.config import NIFI_IP, NIFI_USER, NIFI_PASSWORD, ROOT_CANVAS_ID
from src.services.receive_bearer import get_root_canvas_id


class ConfigureUser():
    def __init__(self, token):
        yaml_path = "src/utils/helper.yaml"
        with open(yaml_path, "r") as f:
            yaml_contents = yaml.load(f, Loader=yaml.FullLoader)

        self.root_canvas_id = get_root_canvas_id(token)

        self.headers = yaml_contents["headers"]
        self.headers["Authorization"] = token
        self.create_processGroup = yaml_contents["create_processGroup"]
        self.create_processGroup["component"]["parentGroupId"] = ROOT_CANVAS_ID
        self.instance_template = yaml_contents['instance_template']
        self.data = f'username={NIFI_USER}&password={NIFI_PASSWORD}'

    def create_user_group(self, username):
        """
            creates process group in nifi with given username
        """
        self.create_processGroup["component"]["name"] = username
        self.create_processGroup["component"]["parentGroupId"] = self.root_canvas_id
        response = requests.post(f"{NIFI_IP}/nifi-api/process-groups/{self.root_canvas_id}/process-groups",
                                 headers=self.headers, data=json.dumps(self.create_processGroup), verify=False)
        new_group = json.loads(response.text)
        group_id = new_group["id"]

        return group_id

    def create_dataflow_group(self, user_id, dataflow_name):
        # creates the dataflow process group inside user process group
        self.create_processGroup["component"]["name"] = dataflow_name
        self.create_processGroup["component"]["parentGroupId"] = user_id
        response = requests.post(f"{NIFI_IP}/nifi-api/process-groups/{user_id}/process-groups",
                                 headers=self.headers, data=json.dumps(self.create_processGroup), verify=False)
        print(response.text)
        new_group = json.loads(response.text)
        group_id = new_group["id"]

        return group_id

    def add_template(self, template_id, group_id):
        # adds the template into the given process group id
        xpos, ypos = -4290.9440641914625, 4190.661030747181
        self.instance_template["originX"] = xpos
        self.instance_template["originY"] = ypos
        self.instance_template["templateId"] = template_id
        response = requests.post(f'{NIFI_IP}/nifi-api/process-groups/{group_id}/template-instance',
                                 headers=self.headers, data=json.dumps(self.instance_template), verify=False)
        template_created = json.loads(response.text)
        return template_created

    def get_configure_processor_id(self, template_info, proc_name):
        # gets the id of processors "ApplyConfig"
        processor_id = None
        for i in range(len(template_info['flow']['processors'])):
            if template_info['flow']['processors'][i]["component"]["name"] == proc_name:
                processor_id = template_info['flow']['processors'][i]["component"]["id"]
        return processor_id

    def update_configure_processor(self, processor_id, confidence, sections, tenant_id, dataflow_id, data_asset_id,
                                   languages, echa_reach_call):
        response = requests.get(f"{NIFI_IP}/nifi-api/processors/{processor_id}", headers=self.headers, data=self.data,
                                verify=False)
        config_processor = json.loads(response.text)
        config_processor["component"]["config"]["properties"]["confidence_level"] = confidence
        config_processor["component"]["config"]["properties"]["sections"] = ",".join(sections)
        config_processor["component"]["config"]["properties"]["tenant_id"] = tenant_id
        config_processor["component"]["config"]["properties"]["flowID"] = dataflow_id
        config_processor["component"]["config"]["properties"]["dataassetId"] = data_asset_id
        config_processor["component"]["config"]["properties"]["languages"] = ",".join(languages)
        try:
            config_processor["component"]["config"]["properties"]["echa_reach_call"] = echa_reach_call
        except:
            pass

        processor_updated = requests.put(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                         headers=self.headers, data=json.dumps(config_processor), verify=False)

        return processor_updated

    def get_userSDS_id(self, template_info):
        # get the id of receive S3 process group
        for i in range(len(template_info['flow']['processGroups'])):
            if template_info['flow']['processGroups'][i]["component"]["name"] == "RECEIVE S3":
                group_id = template_info['flow']['processGroups'][i]["component"]["id"]

        # get the processors inside the recieve s3 process group
        # and find the GetUserSDS processor
        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{group_id}/processors",
                                headers=self.headers, data=self.data, verify=False)
        processors = json.loads(response.text)

        for processor in processors["processors"]:
            if processor["component"]["name"] == "GetUserSDS":
                processor_id = processor["id"]
        return processor_id

    def update_userSDS_processor(self, processor_id, dataflow_id):
        # updates the userSDS processor i.e. adds the dataflow id to input_directory
        response = requests.get(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                headers=self.headers, data=self.data, verify=False)
        userSDS = json.loads(response.text)

        userSDS["component"]["config"]["properties"][
            'Input Directory'] = f"/tmp/uploaded_files/{dataflow_id}"
        processor_updated = requests.put(
            f"{NIFI_IP}/nifi-api/processors/{processor_id}", headers=self.headers, data=json.dumps(userSDS),
            verify=False)
        return processor_updated

    def delete_dataflow(self, dataflow_id):
        # detelte the dataflow from the user process group
        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}",
                                headers=self.headers, data=self.data, verify=False)

        while response.status_code == 200:
            config_processor = json.loads(response.text)

            client_id = config_processor["id"]
            version = config_processor["revision"]["version"]

            delete_response = requests.delete(
                f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}?version={version}&clientId={client_id}",
                headers=self.headers, verify=False)

            # to check if the dataflow is deleted or not
            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}",
                                    headers=self.headers, data=self.data, verify=False)

        return delete_response

    def get_processors_from_template(self, template_info):
        """
            gets all the processors, input ports and output ports from the process groups
            and the processors from the template
        """
        all_processors = []

        # get all the processors, input ports and outpu ports from process group
        for process_group in template_info['flow']['processGroups']:
            group_id = process_group["id"]
            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{group_id}/processors",
                                    headers=self.headers, data=self.data, verify=False)
            processors = json.loads(response.text)

            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{group_id}/output-ports",
                                    headers=self.headers, data=self.data, verify=False)
            output_ports = json.loads(response.text)

            response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{group_id}/input-ports",
                                    headers=self.headers, data=self.data, verify=False)
            input_ports = json.loads(response.text)

            all_processors.extend(processors["processors"])
            all_processors.extend(output_ports["outputPorts"])
            all_processors.extend(input_ports["inputPorts"])

        # get all the processors in the template
        for processor in template_info['flow']['processors']:
            processor_id = processor["id"]
            response = requests.get(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                    headers=self.headers, data=self.data, verify=False)
            processor_json = json.loads(response.text)

            all_processors.append(processor_json)

        return all_processors

    def get_processors_from_dataflow(self, dataflow_id):
        all_processors = list()
        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/processors",
                                headers=self.headers, data=self.data, verify=False)
        processors = json.loads(response.text)

        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/output-ports",
                                headers=self.headers, data=self.data, verify=False)
        output_ports = json.loads(response.text)

        response = requests.get(f"{NIFI_IP}/nifi-api/process-groups/{dataflow_id}/input-ports",
                                headers=self.headers, data=self.data, verify=False)
        input_ports = json.loads(response.text)

        all_processors.extend(processors["processors"])
        all_processors.extend(output_ports["outputPorts"])
        all_processors.extend(input_ports["inputPorts"])

        return all_processors

    def start_all_processors(self, processors):
        # start all the processors, input ports and output ports
        for proc in processors:
            start = {
                'revision': {
                    'version': proc["revision"]["version"],
                },
                "status": {
                    "runStatus": "RUNNING"
                },
                'component': {
                    'id': proc['id'],
                    'state': "RUNNING"
                },
                'id': proc['id']
            }

            processor_id = proc["component"]["id"]
            if proc["component"]["type"] == "OUTPUT_PORT":
                response = requests.put(f"{NIFI_IP}/nifi-api/output-ports/{processor_id}",
                                        headers=self.headers, data=json.dumps(start), verify=False)
            elif proc["component"]["type"] == "INPUT_PORT":
                response = requests.put(f"{NIFI_IP}/nifi-api/input-ports/{processor_id}",
                                        headers=self.headers, data=json.dumps(start), verify=False)
            else:
                response = requests.put(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                        headers=self.headers, data=json.dumps(start), verify=False)

        processor_started = {"sucess"}

        return processor_started if response.ok else False

    def stop_all_processors(self, processors):
        for proc in processors:
            start = {
                'revision': {
                    'version': proc["revision"]["version"],
                },
                "status": {
                    "runStatus": "STOPPED"
                },
                'component': {
                    'id': proc['id'],
                    'state': "STOPPED"
                },
                'id': proc['id']
            }

            processor_id = proc["component"]["id"]
            if proc["component"]["type"] == "OUTPUT_PORT":
                response = requests.put(f"{NIFI_IP}/nifi-api/output-ports/{processor_id}",
                                        headers=self.headers, data=json.dumps(start), verify=False)
            elif proc["component"]["type"] == "INPUT_PORT":
                response = requests.put(f"{NIFI_IP}/nifi-api/input-ports/{processor_id}",
                                        headers=self.headers, data=json.dumps(start), verify=False)
            else:
                response = requests.put(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                        headers=self.headers, data=json.dumps(start), verify=False)

        processor_stopped = {"sucess"}

        return processor_stopped if response.ok else False

    def stop_config_processor(self, processor_id):
        response = requests.get(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                headers=self.headers, data=self.data, verify=False)
        processor_json = json.loads(response.text)
        start = {
            'revision': {
                'version': processor_json["revision"]["version"],
            },
            "status": {
                "runStatus": "STOPPED"
            },
            'component': {
                'id': processor_json['id'],
                'state': "STOPPED"
            },
            'id': processor_json['id']
        }

        response = requests.put(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                headers=self.headers, data=json.dumps(start), verify=False)

        return "STOPPED"

    def start_config_processor(self, processor_id):
        response = requests.get(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                headers=self.headers, data=self.data, verify=False)
        processor_json = json.loads(response.text)
        start = {
            'revision': {
                'version': processor_json["revision"]["version"],
            },
            "status": {
                "runStatus": "RUNNING"
            },
            'component': {
                'id': processor_json['id'],
                'state': "RUNNING"
            },
            'id': processor_json['id']
        }

        response = requests.put(f"{NIFI_IP}/nifi-api/processors/{processor_id}",
                                headers=self.headers, data=json.dumps(start), verify=False)

        return "RUNNING"

    def enable_controller_services(self, dataflow_id):
        """
            input: dataflow_id
            action: gets all the controller services and if disabled
            then the state is updated to enabled
        """
        response = requests.get(f"{NIFI_IP}/nifi-api/flow/process-groups/{dataflow_id}/controller-services",
                                headers=self.headers, data=self.data, verify=False)
        controller_services = json.loads(response.text)

        for controller_service in controller_services["controllerServices"]:
            if controller_service["component"]["state"] == "DISABLED":
                cid = controller_service["id"]
                controller_service["component"]["state"] = "ENABLED"

                response = requests.put(f"{NIFI_IP}/nifi-api/controller-services/{cid}", headers=self.headers,
                                        data=json.dumps(controller_service), verify=False)

        return {"controller services enabled"}

    def disable_controller_services(self, dataflow_id):
        """
            input: dataflow_id
            action: gets all the controller services and if disabled
            then the state is updated to enabled
        """
        response = requests.get(f"{NIFI_IP}/nifi-api/flow/process-groups/{dataflow_id}/controller-services",
                                headers=self.headers, data=self.data, verify=False)
        controller_services = json.loads(response.text)

        for controller_service in controller_services["controllerServices"]:
            if controller_service["parentGroupId"] == dataflow_id:
                if controller_service["component"]["state"] == "ENABLED":
                    cid = controller_service["component"]["id"]
                    new_obj = {'revision': {'version': 1},
                               'component': {'id': cid,
                                             'state': 'DISABLED'}}
                    controller_service["component"]["state"] = "DISABLED"

                    response = requests.put(f"{NIFI_IP}/nifi-api/controller-services/{cid}", headers=self.headers,
                                            data=json.dumps(new_obj), verify=False)

        return {"controller services disabled"}

    def delete_flowfiles(self, dataflow_id):
        all_connections = []

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