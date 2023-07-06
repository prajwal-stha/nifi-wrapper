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
)

from src.services.receive_bearer import get_bearer_token
from src.controllers.management_controller import ManagementController

router = APIRouter()


@router.delete(
    "/delete/system/flowfiles", 
    responses={
        204: {"description": "Wrapper and ROBOTS reachable"},
        424: {"description": "ROBOTS not reachable"},
        500: {"description": "internal server error"},
    },
    tags=["Management"],
    response_model_by_alias=True,
)
async def delete_flowfiles():
    token = get_bearer_token()
    controller = ManagementController(token)

    controller.delete_flowfiles()
    return Response(content=None, status_code=200)
    

@router.delete(
    "/dataflows/{process_group_id}/dataflows", 
    responses={
        204: {"description": "Wrapper and ROBOTS reachable"},
        424: {"description": "ROBOTS not reachable"},
        500: {"description": "internal server error"},
    },
    tags=["Management"],
    response_model_by_alias=True,
)
async def delete_dataflows(
    process_group_id: str = Path(None, description="The ID of the user process group"),
):
    token = get_bearer_token()
    controller = ManagementController(token)

    controller.delete_all_dataflows(process_group_id)
    return Response(content=None, status_code=200)