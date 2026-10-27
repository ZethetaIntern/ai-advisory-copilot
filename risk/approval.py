"""
Approval Workflow State Machine

Enforces: DRAFT -> APPROVED (or REJECTED) 
Export/PDF generation raises an error unless status == APPROVED.

This is a CODE-LEVEL enforcement, not a prompt instruction.
"""
import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"


class AuditEntry(BaseModel):
    timestamp: str
    adviser_id: str
    action: str
    previous_status: str
    new_status: str
    changes: Optional[str] = None
    notes: Optional[str] = None


class AdvisoryPlan(BaseModel):
    """A financial plan that requires adviser approval before client delivery."""
    plan_id: str
    client_id: str
    client_name: str
    status: ApprovalStatus = ApprovalStatus.DRAFT
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Plan content
    risk_profile: Dict[str, Any] = {}
    goals: List[Dict[str, Any]] = []
    fund_recommendations: List[Dict[str, Any]] = []
    
    # Audit trail
    audit_log: List[AuditEntry] = []
    
    # Disclosures (auto-appended)
    disclosures: List[str] = Field(default_factory=lambda: [
        "This plan recommends Direct mutual fund plans only. No commissions are earned by the adviser from fund houses.",
        "The adviser is a SEBI-registered Investment Adviser and acts in a fiduciary capacity.",
        "Mutual fund investments are subject to market risks. Read all scheme-related documents carefully.",
        "Past performance is not indicative of future results. All projections are based on historical data and assumptions.",
        "The return assumptions used are for planning purposes only and do not constitute a guarantee or promise of returns.",
    ])
    
    def submit_for_review(self, adviser_id: str, notes: str = "") -> None:
        """Move from DRAFT to PENDING_REVIEW."""
        if self.status != ApprovalStatus.DRAFT and self.status != ApprovalStatus.REVISION_REQUESTED:
            raise ValueError(
                f"Cannot submit for review: plan is in '{self.status.value}' state. "
                f"Only DRAFT or REVISION_REQUESTED plans can be submitted."
            )
        
        prev = self.status.value
        self.status = ApprovalStatus.PENDING_REVIEW
        self.updated_at = datetime.now().isoformat()
        self.audit_log.append(AuditEntry(
            timestamp=self.updated_at,
            adviser_id=adviser_id,
            action="SUBMIT_FOR_REVIEW",
            previous_status=prev,
            new_status=self.status.value,
            notes=notes,
        ))
    
    def approve(self, adviser_id: str, notes: str = "") -> None:
        """Approve the plan. Only PENDING_REVIEW plans can be approved."""
        if self.status != ApprovalStatus.PENDING_REVIEW:
            raise ValueError(
                f"Cannot approve: plan is in '{self.status.value}' state. "
                f"Only PENDING_REVIEW plans can be approved."
            )
        
        prev = self.status.value
        self.status = ApprovalStatus.APPROVED
        self.updated_at = datetime.now().isoformat()
        self.audit_log.append(AuditEntry(
            timestamp=self.updated_at,
            adviser_id=adviser_id,
            action="APPROVE",
            previous_status=prev,
            new_status=self.status.value,
            notes=notes,
        ))
    
    def reject(self, adviser_id: str, reason: str) -> None:
        """Reject the plan."""
        if self.status != ApprovalStatus.PENDING_REVIEW:
            raise ValueError(
                f"Cannot reject: plan is in '{self.status.value}' state. "
                f"Only PENDING_REVIEW plans can be rejected."
            )
        
        prev = self.status.value
        self.status = ApprovalStatus.REJECTED
        self.updated_at = datetime.now().isoformat()
        self.audit_log.append(AuditEntry(
            timestamp=self.updated_at,
            adviser_id=adviser_id,
            action="REJECT",
            previous_status=prev,
            new_status=self.status.value,
            notes=reason,
        ))
    
    def request_revision(self, adviser_id: str, changes: str) -> None:
        """Request changes to the plan."""
        if self.status != ApprovalStatus.PENDING_REVIEW:
            raise ValueError(
                f"Cannot request revision: plan is in '{self.status.value}' state."
            )
        
        prev = self.status.value
        self.status = ApprovalStatus.REVISION_REQUESTED
        self.updated_at = datetime.now().isoformat()
        self.audit_log.append(AuditEntry(
            timestamp=self.updated_at,
            adviser_id=adviser_id,
            action="REQUEST_REVISION",
            previous_status=prev,
            new_status=self.status.value,
            changes=changes,
        ))
    
    def export_pdf(self, output_path: Optional[str] = None) -> bytes:
        """Export as PDF. RAISES ERROR if not approved."""
        if self.status != ApprovalStatus.APPROVED:
            raise PermissionError(
                f"BLOCKED: Cannot generate client-facing PDF. "
                f"Plan status is '{self.status.value}', must be 'APPROVED'. "
                f"The adviser must approve this plan before it can be shared with the client."
            )
        from app.pdf_export import generate_advisory_pdf
        if output_path is None:
            output_path = os.path.join("reports", f"Advisory_Report_{self.client_id}.pdf")
        generate_advisory_pdf(self.to_dict(), output_path)
        with open(output_path, "rb") as f:
            return f.read()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return self.model_dump()
    
    def save(self, directory: str = "reports") -> str:
        """Save plan to JSON file."""
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"plan_{self.plan_id}.json")
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        return filepath
