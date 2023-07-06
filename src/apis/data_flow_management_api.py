# coding: utf-8

from asyncio import start_unix_server
from tabnanny import check
from typing import Dict, List
from venv import create  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    HTTPException,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
    BackgroundTasks
)

from src.models.create_data_flow200_response import CreateDataFlow200Response
from src.models.data_flow_request import DataFlowRequest
from src.models.saifty_error import SAIFTYError
from src.controllers.update_controller import UpdateController

from src.apis.app.db.tasks import get_user_process_group, create_user_process_group, create_new_route, \
    get_template_by_name, get_all_templates, get_route_for_user, delete_route, update_deletion_flag, \
    create_new_route_in_background
from src.services.receive_bearer import get_bearer_token, check_connection
import urllib3
import ast
import pandas as pd



router = APIRouter()
print("CONNECTION SUCCESSFUL") if check_connection() else print("CONNECTION NOT ESTABLISHED")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@router.post(
    "/dataflows/{userId}",
    responses={
        200: {"model": CreateDataFlow200Response, "description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        501: {"description": "if bad request"},
        404: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Data Flow Management"],
    summary="Endpoint to create a new data flow from a document extraction",
    response_model_by_alias=True,
)
async def create_data_flow(
    background_tasks: BackgroundTasks,
    userId: str=Path(None, description="The ID of the dataflow"),
    data_flow_request: DataFlowRequest=Body(None, description="Data flow that has not been created yet (empty ID)"),
) -> CreateDataFlow200Response:
    token = get_bearer_token()
    controller = UpdateController(token)

    template = data_flow_request.flow_type
    name = data_flow_request.name

    template_id = get_template_by_name(template)
    if template_id:
        #get user group
        user_process_group = get_user_process_group(user_id=userId)
        if not user_process_group: 
            #create user process group in robots and add database entry
            user_process_group = controller.create_user_group(userId)
            create_user_process_group(userId, user_process_group)
        
        # get group id of the dataflow processor
        dataflow_id = controller.create_dataflow_group(user_process_group, name)

        response = CreateDataFlow200Response(dataflowId=dataflow_id)

        background_tasks.add_task(create_new_route_in_background,
                                  template_id,
                                  dataflow_id,
                                  userId,
                                  controller,
                                  data_flow_request)
        return response
    else:
        all_templates = ", ".join([item.dict()["template_name"] for item in get_all_templates()])
        print(all_templates)
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SAIFTYError(transaction=f"Template {data_flow_request.flow_type} not found", error_name="Template not found", error_details=f"Available Templates: {all_templates}").dict())
        

@router.delete(
    "/dataflows/delete/{dataFlow_id}/{userId}",
    responses={
        200: {"description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        404: {"description": "if provided data flow not found"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Data Flow Management"],
    summary="Delete the dataflow by using the ID",
    response_model_by_alias=True,
)
async def delete_data_flow(
    dataFlow_id: str = Path(None, description="The ID of the dataflow"),
    userId: str = Path(None, description="user email"),
):
    token = get_bearer_token()
    controller = UpdateController(token)
    update_deletion_flag(dataFlow_id)
    # get_dataflows()
    # controller.delete_dataflow_group(dataFlow_id)
    # try: 
    #     delete_route(dataFlow_id)
    # except: 
    #     pass
    
    return Response(content=None, status_code=200)


@router.put(
    "/dataflows/{dataFlow_id}/{userId}",
    responses={
        200: {"description": "if successful connection"},
        401: {"description": "if unauthorized connection"},
        404: {"description": "if provided data flow not found"},
        501: {"description": "if bad request"},
        200: {"model": SAIFTYError, "description": "Unexpected Error"},
    },
    tags=["Data Flow Management"],
    summary="Update an existing data flow by sending a new DataFlow object",
    response_model_by_alias=True,
)
async def update_data_flow(
    dataFlow_id: str = Path(None, description=""),
    userId: str = Path(None, description="The ID of the dataflow"),
    data_flow_request: DataFlowRequest = Body(None, description="Existing data flow with refreshed information"),
):
    token = get_bearer_token()
    controller = UpdateController(token)
    data_asset_id = data_flow_request.data["store"]["dataassetId"]
    languages = data_flow_request.data["extract"]["languages"]
    sections = data_flow_request.data["extract"]["sections"]
    confidence_level = data_flow_request.data["validate"]["confidence"]
    echa_reach_call = data_flow_request.data["validate"]["echa_reach_call"]
    
    processor_id = get_route_for_user(dataflow_id=dataFlow_id, user_id=userId)
    controller.stop_config_processor(processor_id)
    controller.update_configure_processor(processor_id, confidence_level, sections, userId, dataFlow_id, data_asset_id, languages, echa_reach_call)
    controller.start_config_processor(processor_id)

    return Response(content=None, status_code=200)