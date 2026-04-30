from fastapi import FastAPI

from backend.app.schemas.requst_responce_schema import SkyResponse, SkyRequest

app = FastAPI()

@app.get("/sky", response_model=SkyResponse)

async def get_sky(request: SkyRequest) -> SkyResponse:
    pass