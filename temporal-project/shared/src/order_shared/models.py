"""
shared/models.py

PURPOSE:
  Shared data contracts between the Client server
  and the Worker server.

  This file is installed on BOTH servers.
  It defines ONLY data shapes — no logic, no I/O.

ENTERPRISE PATTERN:
  In real teams this would be a versioned Python
  package (e.g. order-contracts==1.2.0) published
  to a private PyPI registry and pinned in both
  servers' requirements.txt.

RULES:
  - Only dataclasses here
  - No imports from activities.py or workflows.py
  - No business logic
  - Changes here affect BOTH servers — version carefully
"""

from dataclasses import dataclass, field


@dataclass
class OrderInput:
    """
    Input passed to OrderWorkflow when it is started.
    Serialized to JSON by Temporal automatically.
    """
    order_id: str
    customer_id: str
    amount: float


@dataclass
class ValidationResult:
    """Returned by the validate_order Activity."""
    valid: bool
    reason: str = ""


@dataclass
class PaymentResult:
    """Returned by the charge_payment Activity."""
    charged: bool
    transaction_id: str
    amount: float


@dataclass
class WorkflowStatus:
    """
    Returned by the get_status Query.
    Structured response — easier to extend than a string.
    """
    status: str          # e.g. "validating", "completed"
    approved: bool
    cancelled: bool
    order_id: str = ""