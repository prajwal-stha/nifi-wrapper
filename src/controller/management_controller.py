from src.services.management_workflow import ManagementFlow

class ManagementController():
    def __init__(self, token):
        self.management_flow = ManagementFlow(token)
        
    def delete_flowfiles(self):
        self.management_flow.delete_flowfiles()

    def delete_all_dataflows(self, process_group_id):
        self.management_flow.delete_all_dataflows(process_group_id)