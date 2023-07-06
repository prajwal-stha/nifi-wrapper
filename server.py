from fastapi import FastAPI
from src.apis.data_flow_management_api import router as DataFlowManagementRouter
from src.apis.template_management_api import router as TemplateFlowManagementRouter
from src.apis.metrics_api import router as MetriceManagementRouter
from src.apis.upload_api_api import router as UploadAPI
from src.apis.health_api import router as HealthAPI
from src.apis.management_api import router as ManagementAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="NIFI Wrapper API")

app.add_middleware(CORSMiddleware,
                allow_origins= ["*"],
                allow_credentials=True,
                allow_methods=["POST", "GET", "PUT", "OPTIONS", "PATH"],
                allow_headers=["Authorization", "Content-Type"])


app.include_router(DataFlowManagementRouter)
app.include_router(TemplateFlowManagementRouter)
app.include_router(UploadAPI)
app.include_router(MetriceManagementRouter)
app.include_router(HealthAPI)
app.include_router(ManagementAPI)