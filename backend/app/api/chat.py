"""
Conversational AI Chatbot Router for FreshMart.
Exposes role-scoped conversational guidance powered by Ollama (Llama 3.1 8B).
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.auth_models import User
from app.schemas.chat_schemas import ChatMessageRequest, ChatMessageResponse
from app.schemas.common_schemas import HTTPError
from app.core.llm import ollama_client
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

def get_allowed_domains_for_user(user: User) -> List[str]:
    """
    Computes human-readable business domain names based on granted permissions.
    The backend is the authority.
    """
    perms = set(user.permission_codes)
    domains = []
    if "VIEW_HR" in perms or "VIEW_EMPLOYEE_SALARY" in perms:
        domains.append("HRMS (Human Resources)")
    if "VIEW_CRM" in perms:
        domains.append("CRM (Customers & Leads)")
    if "VIEW_SALES" in perms:
        domains.append("Sales & Revenue")
    if "VIEW_INVENTORY" in perms or "VIEW_PURCHASES" in perms:
        domains.append("ERP & Inventory")
    if "VIEW_FINANCE" in perms or "VIEW_PROFIT" in perms or "VIEW_EXPENSES" in perms:
        domains.append("Finance & P&L")
    if "MANAGE_USERS" in perms or "MANAGE_ROLES" in perms:
        domains.append("System Administration")
    return domains

@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send Conversational Business Inquiry",
    description=(
        "Role-scoped conversational AI chat endpoint powered by Ollama Llama 3.1 8B:\n"
        "1. Authenticates user identity and role from backend JWT.\n"
        "2. Injects authoritative system context with permitted business domains.\n"
        "3. Queries local Ollama LLM with role-scoped context.\n"
        "4. Returns AI response with role and permitted domain metadata."
    ),
    operation_id="sendChatMessage",
    responses={
        200: {
            "model": ChatMessageResponse,
            "description": "Conversational assistant response generated successfully."
        },
        401: {
            "model": HTTPError,
            "description": "Unauthorized: Missing, invalid, or expired JWT access token."
        },
        422: {
            "description": "Validation Error: Request message payload could not be validated."
        },
        503: {
            "model": HTTPError,
            "description": "Service Unavailable: Local Ollama LLM engine is offline or unreachable."
        }
    }
)
async def send_chat_message(
    chat_req: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Phase 5 AI Chatbot Endpoint.
    1. Authenticates user identity and role from backend JWT.
    2. Enforces role-awareness and backend authority.
    3. Queries local Ollama LLM with role-scoped system context.
    4. Returns AI response with role and permitted domain metadata.
    """
    allowed_domains = get_allowed_domains_for_user(current_user)

    system_prompt = (
        f"You are the enterprise AI Analytics Assistant for FreshMart.\n"
        f"Current Authenticated User: {current_user.full_name} ({current_user.username})\n"
        f"Role: {current_user.role.role_name}\n"
        f"Authorized Business Domains: {', '.join(allowed_domains) if allowed_domains else 'None'}\n\n"
        f"Instructions:\n"
        f"- Always be professional, concise, and helpful.\n"
        f"- Acknowledge the user's role ({current_user.role.role_name}) when answering.\n"
        f"- In Phase 5, provide natural language business guidance and acknowledge their question.\n"
        f"- Note: In upcoming phases (MCP & SQL Agent), you will automatically query the live database to retrieve real-time tables and charts."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chat_req.message}
    ]

    try:
        reply = await ollama_client.generate_chat(
            messages=messages,
            model=settings.OLLAMA_AGENT_MODEL,
            temperature=0.3,
            timeout=120.0
        )
    except Exception as e:
        # Fallback to secondary model if primary had an issue
        try:
            reply = await ollama_client.generate_chat(
                messages=messages,
                model=settings.OLLAMA_SQL_MODEL,
                temperature=0.3,
                timeout=120.0
            )
        except Exception as fallback_err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Local LLM engine error: {str(e)} | Fallback error: {str(fallback_err)}"
            )

    return ChatMessageResponse(
        reply=reply,
        conversation_id=chat_req.conversation_id,
        user_role=current_user.role.role_name,
        user_name=current_user.full_name,
        allowed_domains=allowed_domains,
        model_used=settings.OLLAMA_AGENT_MODEL,
        timestamp=datetime.utcnow()
    )
