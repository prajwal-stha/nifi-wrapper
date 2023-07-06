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
from src.models.saifty_error import SAIFTYError
from src.services.receive_bearer import get_bearer_token
from src.controllers.upload_controller import UploadController


router = APIRouter()


@router.post(
    "/fileUpload/",
    responses={
        200: {"description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
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
