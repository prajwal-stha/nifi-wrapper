# coding: utf-8

from typing import Dict, List
from urllib import response  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)

from src.models.extra_models import TokenModel  # noqa: F401
from src.models.queued_flow_files_dataflow_id_get200_response import QueuedFlowFilesDataflowIdGet200Response
from src.models.dataflows_metrics_dataflow_id_get200_response import DataflowsMetricsDataflowIdGet200Response
from src.models.saifty_error import SAIFTYError
from src.controllers.metrics_controller import MetricController
from src.services.receive_bearer import get_bearer_token
from src.apis.app.db.tasks import get_processed_documents, update_processed_documents
from src.models.dataflows_dataflow_id_processed_documents_get200_response import DataflowsDataflowIdProcessedDocumentsGet200Response


router = APIRouter()



@router.post(
    "/dataflows/{dataflow_id}/processedDocuments",
    responses={
        200: {"description": "Number of documents currently in the flow"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Metrics"],
    response_model_by_alias=True,
)
async def dataflows_dataflow_id_processed_documents_post(
    dataflow_id: str = Path(None, description=""),
):
    update_processed_documents(dataflow_id)

    return {"response": "document added"}



@router.get(
    "/dataflows/metrics/{dataflow_id}",
    responses={
        200: {"model": DataflowsMetricsDataflowIdGet200Response, "description": "All Metrics"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Metrics"],
    response_model_by_alias=True,
)
async def dataflows_metrics_dataflow_id_get(
    dataflow_id: str = Path(None, description=""),
) -> DataflowsMetricsDataflowIdGet200Response:
    #token = get_bearer_token()
    #controller = MetricController(token)

    #queued_flow_files = controller.get_queued_flow_files(dataflow_id)
    processed_documents = get_processed_documents(dataflow_id=dataflow_id)
    response = DataflowsMetricsDataflowIdGet200Response(queuedFlowFiles=processed_documents, no_of_processed_documents=processed_documents)
    return response
