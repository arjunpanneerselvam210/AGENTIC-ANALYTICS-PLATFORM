"""
Shared common schemas and error response models for FreshMart OpenAPI documentation.
"""

from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field

class HTTPError(BaseModel):
    """Standard RFC 7807-compatible error response detail."""
    detail: str = Field(
        ...,
        description="Human-readable explanation of why the request failed.",
        example="Access Denied: You do not have permission 'VIEW_EMPLOYEE_SALARY'."
    )

class ValidationErrorLocation(BaseModel):
    """Field location and validation message for 422 Unprocessable Entity."""
    loc: List[Union[str, int]] = Field(..., description="Path to invalid field in request", example=["body", "question"])
    msg: str = Field(..., description="Validation failure explanation", example="Field required")
    type: str = Field(..., description="Pydantic validation error type", example="missing")

class HTTPValidationError(BaseModel):
    """Schema for FastAPI standard 422 Unprocessable Entity response."""
    detail: List[ValidationErrorLocation] = Field(..., description="List of validation errors found in request body or parameters")
