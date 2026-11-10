from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.quiz import router as quiz_router
from app.api.v1.plans import router as plans_router
from app.api.v1.orders import router as orders_router
from app.api.v1.documents import router as documents_router
from app.api.v1.admin import router as admin_router
from app.api.v1.health import router as health_router
from app.api.v1.exams import router as exams_router
from app.api.v1.roadmaps import router as roadmaps_router
from app.api.v1.banners import router as banners_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(quiz_router)
api_router.include_router(exams_router)
api_router.include_router(roadmaps_router)
api_router.include_router(banners_router)
api_router.include_router(plans_router)
api_router.include_router(orders_router)
api_router.include_router(documents_router)
api_router.include_router(admin_router)
