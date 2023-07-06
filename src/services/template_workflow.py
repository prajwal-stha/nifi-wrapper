import requests
import xml.etree.ElementTree as ET

from src.core.config import NIFI_IP
from src.services.receive_bearer import get_root_canvas_id


class TemplateWorkflow():
    def __init__(self, token):
        self.token = token

    def upload_template(self, template_path):
        """
            input: requires path of the template
            action: uploads the template into the nifi
            output: returns template name and template id
        """
        headers = {}
        headers["Authorization"] = self.token
        root_canvas_id = get_root_canvas_id(self.token)

        response = requests.post(
            f"{NIFI_IP}/nifi-api/process-groups/{root_canvas_id}/templates/upload", headers=headers,
            files={"template": open(template_path, 'rb')}, verify=False)

        # parse xml string and get template id and template name
        tree = ET.fromstring(response.text)
        root = ET.ElementTree(tree).getroot()

        template_name = [element.text for element in root.iter('name')][0]
        template_id = [element.text for element in root.iter('id')][0]

        return template_name, template_id

    def delete_template(self, template_id):
        headers = {}
        headers["Authorization"] = self.token

        delete_response = requests.delete(
            f"{NIFI_IP}/nifi-api/templates/{template_id}", headers=headers, verify=False)

        return delete_response


