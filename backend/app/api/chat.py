"""
Conversational AI Chatbot Router for FreshMart.
Exposes role-scoped conversational guidance powered by Ollama (Llama 3.1 8B).
"""

from datetime import datetime
from typing import List
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.time_utils import get_current_ist


from app.core.security import get_current_user
from app.db.postgres_session import get_postgres_db
from app.models.auth_models import User, UserChatSession
from app.schemas.chat_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionItem,
    ChatSessionSaveRequest,
    ChatSessionListResponse
)
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
        timestamp=get_current_ist()
    )



@router.get(
    "/sessions",
    response_model=ChatSessionListResponse,
    summary="Get User Chat & Analytics Sessions History",
    description="Returns all previously archived conversation sessions for the authenticated user, ordered by most recent first."
)
def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Retrieves all persisted previous sessions for the logged-in user."""
    sessions = (
        db.query(UserChatSession)
        .filter(UserChatSession.user_id == current_user.user_id)
        .order_by(UserChatSession.updated_at.desc())
        .limit(50)
        .all()
    )

    items = []
    for s in sessions:
        try:
            parsed_items = json.loads(s.session_data) if s.session_data else []
        except Exception:
            parsed_items = []
        items.append(
            ChatSessionItem(
                id=s.id,
                title=s.title,
                started_at=s.started_at,
                queries_count=s.queries_count,
                items=parsed_items,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
        )

    return ChatSessionListResponse(sessions=items, total=len(items))


@router.post(
    "/sessions",
    response_model=ChatSessionItem,
    summary="Save or Archive Chat & Analytics Session",
    description="Saves or updates a conversation session in the server database for persistent history."
)
def save_user_chat_session(
    req: ChatSessionSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Archives or updates an analytics conversation session for the authenticated user."""
    session_record = (
        db.query(UserChatSession)
        .filter(UserChatSession.id == req.id, UserChatSession.user_id == current_user.user_id)
        .first()
    )

    serialized_data = json.dumps(req.items, default=str)

    if session_record:
        session_record.title = req.title
        session_record.queries_count = req.queries_count
        session_record.started_at = req.started_at
        session_record.session_data = serialized_data
        session_record.updated_at = get_current_ist()
    else:
        session_record = UserChatSession(
            id=req.id,
            user_id=current_user.user_id,
            title=req.title,
            queries_count=req.queries_count,
            started_at=req.started_at,
            session_data=serialized_data,
            created_at=get_current_ist(),
            updated_at=get_current_ist()
        )

        db.add(session_record)

    db.commit()
    db.refresh(session_record)

    try:
        parsed_items = json.loads(session_record.session_data) if session_record.session_data else []
    except Exception:
        parsed_items = []

    return ChatSessionItem(
        id=session_record.id,
        title=session_record.title,
        started_at=session_record.started_at,
        queries_count=session_record.queries_count,
        items=parsed_items,
        created_at=session_record.created_at,
        updated_at=session_record.updated_at
    )


@router.delete(
    "/sessions/{session_id}",
    summary="Delete Archived Chat Session",
    description="Deletes a specific archived session belonging to the authenticated user."
)
def delete_user_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Deletes an archived chat session."""
    session_record = (
        db.query(UserChatSession)
        .filter(UserChatSession.id == session_id, UserChatSession.user_id == current_user.user_id)
        .first()
    )
    if not session_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    db.delete(session_record)
    db.commit()
    return {"success": True, "deleted_id": session_id}

