# coding: utf-8

from typing import Dict, List  # noqa: F401
from src.services.receive_bearer import check_connection
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


router = APIRouter()


@router.get(
    "/health/status/check/", 
    responses={
        204: {"description": "Wrapper and NIFI Reachable"},
        424: {"description": "NIFI Not Reachable"},
        500: {"description": "Internal Server Error"},
    },
    tags=["Health"],
    response_model_by_alias=True,
)
async def health_check(
) -> None:
    """check the server health"""
    
    if check_connection():
        return Response(content=None, status_code=200)
    else: 
        return Response(content=None, status_code=424)
