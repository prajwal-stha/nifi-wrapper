# coding: utf-8

from typing import Dict, List  # noqa: F401
import os
import shutil

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
    UploadFile,
    File
)

from src.models.extra_models import TokenModel  # noqa: F401
from src.models.create_data_flow200_response import CreateDataFlow200Response
from src.models.saifty_error import SAIFTYError
from src.models.all_templates200_response import AllTemplates200Response

from src.apis.app.db.tasks import create_new_template_with_name, get_all_templates, delete_template, get_template_by_name
from src.services.receive_bearer import get_bearer_token
from src.controllers.template_controller import TemplateController


router = APIRouter()

upload_folder = "/tmp/documents"


def create_file(filedata):
    global upload_folder
    file_object = filedata.file
    # create empty file to copy the file_object to
    if not os.path.exists(upload_folder):
        os.mkdir(upload_folder)
    path = os.path.join(upload_folder, filedata.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file_object, buffer)

    return path


@router.get(
    "/templates/",
    responses={
        200: {"model": AllTemplates200Response, "description": "Templates currently available in the DB"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Template Management"],
    summary="Return all available templates",
    response_model_by_alias=True,
)
async def all_templates(
) -> AllTemplates200Response:
    all_templates = AllTemplates200Response(templates=[item.dict()["template_name"] for item in get_all_templates()])
    
    return all_templates
    
    
@router.post(
    "/templates/",
    responses={
        200: {"model": CreateDataFlow200Response, "description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Template Management"],
    summary="Endpoint to create a new data flow from a document extraction",
    response_model_by_alias=True,
)
async def create_new_template(
    template_name: str = Query(None, description="The name of the template"),
    filedata: UploadFile = File(...)
) -> CreateDataFlow200Response:
    token = get_bearer_token()
    controller = TemplateController(token)

    file_path = create_file(filedata)
    _, template_id = controller.get_template_info(file_path)
    create_new_template_with_name(
        template_name=template_name, template_id=template_id)

    return {"message": "template uploaded"}


@router.delete(
    "/templates/{template_name}",
    responses={
        200: {"model": CreateDataFlow200Response, "description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Template Management"],
    summary="Endpoint to create a new data flow from a document extraction",
    response_model_by_alias=True,
)
async def delete_template_by_id(
    template_name: str = Query(None, description="The name of the template"),
):
    token = get_bearer_token()
    controller = TemplateController(token)

    template_id = get_template_by_name(template_name)
    delete_template(template_id)
    res = controller.delete_template(template_id)
    if res.status_code == 200:
        return {"Template deleted"}
    else:
        return {f"Template with id {template_id} doesn't exist"}