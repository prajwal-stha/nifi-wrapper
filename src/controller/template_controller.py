from src.services.template_workflow import TemplateWorkflow


class TemplateController():
    def __init__(self, token):
        self.template_workflow = TemplateWorkflow(token)

    def get_template_info(self, template_path):
        template_name, template_id = self.template_workflow.upload_template(
            template_path)
        return template_name, template_id
    
    def delete_template(self, template_id):
        response = self.template_workflow.delete_template(template_id)
        return response
