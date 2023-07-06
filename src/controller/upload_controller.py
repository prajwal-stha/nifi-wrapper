from src.services.processor_workflow import ProcessorWorkflow
from src.services.user_workflow import ConfigureUser


class UploadController():
    def __init__(self, token):
        self.processor_worflow = ProcessorWorkflow(token)
        self.configure_user = ConfigureUser(token)

    def start_processors(self, dataflow_id):
        processors = self.processor_worflow.get_processors_from_dataflow(dataflow_id)
        self.configure_user.start_all_processors(processors)