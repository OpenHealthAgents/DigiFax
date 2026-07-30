"""
notification_controller.py
FastAPI controller routing tenant configuration and outbound notifications dispatches.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.notification.configure_notification_settings import ConfigureNotificationSettingsUseCase
from src.application.use_cases.notification.send_notification import SendNotificationUseCase
from src.infrastructure.persistence.in_memory_notification_repository import InMemoryNotificationRepository
from src.infrastructure.delivery.mock_notification_dispatcher import MockNotificationDispatcher

router = APIRouter(prefix="/api/notifications", tags=["Notification Management"])

_notification_repo = InMemoryNotificationRepository()
_dispatcher_port = MockNotificationDispatcher()


# --- REQUEST & RESPONSE SCHEMAS ---

class TemplateConfigItem(BaseModel):
    template_id: str
    subject_template: str
    body_template: str


class ConfigureBrandingRequest(BaseModel):
    branding_header: str = Field("", description="Standard header line mapping to top of all outgoing emails")
    branding_footer: str = Field("", description="Standard footer line mapping to bottom of all outgoing emails")
    templates: List[TemplateConfigItem] = Field(default_factory=list)


class EscalationConfig(BaseModel):
    delay_minutes: int
    next_channel: str
    backup_recipient: str


class SendNotificationRequest(BaseModel):
    recipient_id: str = Field(..., description="Target contact string (e.g. email or mobile phone number)")
    template_id: str = Field(..., description="Template key selector")
    template_params: Dict[str, Any] = Field(default_factory=dict, description="Variables values to inject")
    channels: List[str] = Field(..., description="Channels list to dispatch e.g. ['EMAIL', 'SMS']")
    escalation_rules: Optional[List[EscalationConfig]] = Field(default_factory=list)


class DeliveryLogResponse(BaseModel):
    dispatch_time: str
    channel: str
    status: str
    error_message: Optional[str] = None
    retry_count: int


class NotificationRequestResponse(BaseModel):
    notification_id: str
    tenant_id: str
    recipient_id: str
    title: str
    body: str
    channels: List[str]
    delivery_logs: List[DeliveryLogResponse]
    status: str


# --- ROUTERS ---

@router.post("/config", status_code=status.HTTP_200_OK)
def configure_settings(
    req: ConfigureBrandingRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Configures templates and branding parameters for a tenant."""
    use_case = ConfigureNotificationSettingsUseCase(_notification_repo)
    try:
        config = use_case.execute(
            tenant_id=x_tenant_id,
            templates=[t.dict() for t in req.templates],
            branding_header=req.branding_header,
            branding_footer=req.branding_footer
        )
        return {
            "tenant_id": config.tenant_id,
            "branding_header": config.branding_header,
            "branding_footer": config.branding_footer,
            "templates_count": len(config.templates)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send", response_model=NotificationRequestResponse, status_code=status.HTTP_201_CREATED)
def send_notification(
    req: SendNotificationRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Dispatches a clinical notification with retry-tracking, templating, and escalations."""
    use_case = SendNotificationUseCase(_notification_repo, _dispatcher_port)
    try:
        notify_req = use_case.execute(
            tenant_id=x_tenant_id,
            recipient_id=req.recipient_id,
            template_id=req.template_id,
            template_params=req.template_params,
            channels=req.channels,
            escalation_rules=[r.dict() for r in req.escalation_rules] if req.escalation_rules else None
        )
        return NotificationRequestResponse(
            notification_id=notify_req.notification_id,
            tenant_id=notify_req.tenant_id,
            recipient_id=notify_req.recipient_id,
            title=notify_req.title,
            body=notify_req.body,
            channels=notify_req.channels,
            delivery_logs=[
                DeliveryLogResponse(
                    dispatch_time=l.dispatch_time,
                    channel=l.channel,
                    status=l.status,
                    error_message=l.error_message,
                    retry_count=l.retry_count
                ) for l in notify_req.delivery_logs
            ],
            status=notify_req.status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status", response_model=NotificationRequestResponse, status_code=status.HTTP_200_OK)
def get_status(
    notification_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Gets details and delivery tracking logs for a specific notification request."""
    notify_req = _notification_repo.get_request(x_tenant_id, notification_id)
    if not notify_req:
        raise HTTPException(status_code=404, detail="Notification request not found")

    return NotificationRequestResponse(
        notification_id=notify_req.notification_id,
        tenant_id=notify_req.tenant_id,
        recipient_id=notify_req.recipient_id,
        title=notify_req.title,
        body=notify_req.body,
        channels=notify_req.channels,
        delivery_logs=[
            DeliveryLogResponse(
                dispatch_time=l.dispatch_time,
                channel=l.channel,
                status=l.status,
                error_message=l.error_message,
                retry_count=l.retry_count
            ) for l in notify_req.delivery_logs
        ],
        status=notify_req.status
    )
