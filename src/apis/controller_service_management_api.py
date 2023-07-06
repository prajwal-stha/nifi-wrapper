# coding: utf-8

from typing import Dict, List  # noqa: F401

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
from src.models.error import Error
from src.services.receive_bearer import get_bearer_token


router = APIRouter()


@router.get(
    "/controller-services/{controller_service_id}",
    responses={
        200: {"model": CreateDataFlow200Response, "description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        404: {"model": Error, "description": "Unexpected Error"},
    },
    tags=["Upload Api"],
    summary="Endpoint to create a new data flow from a document extraction",
    response_model_by_alias=True,
)
async def start_get_file(
        flow_id: str = Query(None, description="The id of dataflow"),
):
    token = get_bearer_token()
    controller = UploadController(token)

    controller.start_processors(flow_id)

    return {"response": "processors started"}
