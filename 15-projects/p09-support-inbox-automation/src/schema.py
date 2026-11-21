"""
schema.py - the exact shape of the information we pull out of every email.

**Pydantic** - a library where you describe data as a Python class with types.
It then *validates* incoming data: wrong types, missing fields or values outside
an allowed list raise a clear error. Think of it as a form with required boxes
and drop-down menus: the clerk refuses forms that are filled in wrongly.

**Structured extraction** - turning free text (an email) into fields like these.
Asking an LLM for JSON and validating it against this schema is the idea behind
libraries such as Instructor.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Intent = Literal["refund", "delivery_status", "damaged_item", "cancel_order", "billing_issue",
                 "technical_support", "account_access", "feedback", "spam", "other"]
PRODUCTS = ["AquaPure Filter", "SmartKettle 2", "FitBand Pro", "SoundBuds X", "HomeCam 360"]


class Ticket(BaseModel):
    """Everything the workflow needs to know about one email."""
    customer_name: str | None = Field(None, description="the sender's name, if known")
    customer_email: str = Field(..., description="the sender's email address")
    order_id: str | None = Field(None, pattern=r"^ORD-\d{5}$", description="like ORD-12345; null if not given")
    product: str | None = Field(None, description=f"one of {PRODUCTS} or null")
    intents: list[Intent] = Field(..., min_length=1, description="what the customer wants (one or more)")
    urgency: Literal["low", "medium", "high"]
    sentiment: Literal["positive", "neutral", "negative", "angry"]
    summary: str = Field(..., max_length=300, description="one-sentence summary for the agent")

    @field_validator("product")
    @classmethod
    def known_product(cls, v):
        """Reject made-up product names (a common LLM mistake)."""
        if v is not None and v not in PRODUCTS:
            raise ValueError(f"unknown product {v!r}; must be one of {PRODUCTS} or null")
        return v


class Email(BaseModel):
    """The input to the workflow (what n8n or the inbox watcher sends us)."""
    id: str | None = None
    sender: str = Field(..., alias="from")
    subject: str = ""
    body: str
    received_at: str | None = None

    model_config = {"populate_by_name": True}
