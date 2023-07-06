import requests
import json
import yaml

from src.core.config import ROBOTS_IP
from src.services.receive_bearer import get_bearer_token
from src.services.user_workflow import ConfigureUser
from src.services.processor_workflow import ProcessorWorkflow


class UpdateController():
    def __init__(self, token):
        self.token = token
        self.configure_user = ConfigureUser(token)

    def create_user_group(self, username):
        group_id = self.configure_user.create_user_group(username)
        return group_id

    def create_dataflow_group(self, user_id, dataflow_name):
        group_id = self.configure_user.create_dataflow_group(
            user_id, dataflow_name)
        return group_id

    def add_template(self, template_id, group_id):
        template_info = self.configure_user.add_template(template_id, group_id)
        return template_info

    def get_processor_id(self, template_info, proc_name):
        processor_id = self.configure_user.get_configure_processor_id(
            template_info,
            proc_name)
        return processor_id


    def update_configure_processor(self, processor_id, confidence, sections, tenant_id, dataflow_id, data_asset_id, languages, echa_reach_call):
        updated_processor = self.configure_user.update_configure_processor(processor_id, confidence, sections, tenant_id, dataflow_id, data_asset_id, languages, echa_reach_call)

        return updated_processor

    def get_userSDS_processor_id(self, template_info):
        processor_id = self.configure_user.get_userSDS_id(template_info)
        return processor_id

    def update_userSDS_processor(self, processor_id, dataflow_id):
        updated_processor = self.configure_user.update_userSDS_processor(
            processor_id, dataflow_id)
        return updated_processor

    def delete_dataflow_group(self, dataflow_id):
        processor_workflow = ProcessorWorkflow(self.token)
        #all_processors = self.configure_user.get_processors_from_dataflow(dataflow_id)
        all_processors = processor_workflow.get_processors_from_dataflow(dataflow_id)
        self.configure_user.stop_all_processors(all_processors)
        self.configure_user.disable_controller_services(dataflow_id)
        self.configure_user.delete_flowfiles(dataflow_id)
        
        response = self.configure_user.delete_dataflow(dataflow_id)
        return response

    def start_all_processors(self, template_info):
        all_processors = self.configure_user.get_processors_from_template(
            template_info)
        self.configure_user.start_all_processors(all_processors)
    
    def stop_config_processor(self, processor_id): 
        self.configure_user.stop_config_processor(processor_id)
    
    def start_config_processor(self, processor_id):
        self.configure_user.start_config_processor(processor_id)
        

    def enable_controller_services(self, dataflow_id):
        self.configure_user.enable_controller_services(dataflow_id)
