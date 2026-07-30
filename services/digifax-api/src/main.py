from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.controllers.intake_controller import router as intake_router
from src.infrastructure.controllers.tenant_config_controller import router as tenant_config_router
from src.infrastructure.controllers.terminology_controller import router as terminology_router
from src.infrastructure.controllers.fhir_profile_controller import router as fhir_profile_router
from src.infrastructure.controllers.compliance_controller import router as compliance_router
from src.infrastructure.controllers.encryption_controller import router as encryption_router
from src.infrastructure.controllers.metering_controller import router as metering_router

app = FastAPI(
    title="DigiFax Backend REST API",
    description="Hexagonal Clean Architecture backend for ingestion, extraction, and EHR delivery.",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(intake_router)
app.include_router(tenant_config_router)
app.include_router(terminology_router)
app.include_router(fhir_profile_router)
app.include_router(compliance_router)
app.include_router(encryption_router)
app.include_router(metering_router)


@app.get("/")
def health_check() -> dict[str, str]:
    """Exposes simple health and status checkpoints."""
    return {"status": "healthy", "service": "digifax-api"}


@app.get("/healthz")
def live_check() -> str:
    """Liveness probe checkpoint."""
    return "OK"
