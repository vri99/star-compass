from typing import Annotated

from fastapi import Depends, APIRouter

from backend.app.repository.constellation_repository import ConstellationRepository
from backend.app.schemas.requst_responce_schema import SkyRequest, SkyResponse
from backend.app.services.service_interfaces import ObserverContext, SkyMapperServiceInterface
from backend.app.services.sky_calculator_service import SkyCalculatorService
from backend.app.services.sky_mapper_service import SkyMapperService

router = APIRouter()


def get_sky_mapper() -> SkyMapperServiceInterface:
    return SkyMapperService(SkyCalculatorService(), ConstellationRepository())


@router.get("/sky", response_model=SkyResponse)
async def get_sky(
        request: Annotated[SkyRequest, Depends()],
        sky_mapper: Annotated[SkyMapperServiceInterface, Depends(get_sky_mapper)],
) -> SkyResponse:
    observer_context: ObserverContext = ObserverContext(
        date=request.observed_at,
        longitude=request.longitude,
        latitude=request.latitude,
    )

    return sky_mapper.build_response(observer_context)
