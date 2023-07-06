from src.services.metrics import Metrics


class MetricController():
    def __init__(self, token):
        self.metrics = Metrics(token)

    def get_queued_flow_files(self, dataflow_id):
        queued_flow_files = self.metrics.get_queued_flow_files(dataflow_id)
        return queued_flow_files