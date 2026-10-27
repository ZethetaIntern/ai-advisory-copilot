"""Tests for the approval workflow state machine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk.approval import AdvisoryPlan, ApprovalStatus


class TestApprovalStateMachine:
    def _make_plan(self):
        return AdvisoryPlan(
            plan_id="test_001",
            client_id="fresh_grad",
            client_name="Arjun Mehta",
        )
    
    def test_initial_state_is_draft(self):
        plan = self._make_plan()
        assert plan.status == ApprovalStatus.DRAFT
    
    def test_submit_for_review(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        assert plan.status == ApprovalStatus.PENDING_REVIEW
        assert len(plan.audit_log) == 1
    
    def test_approve(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        plan.approve("adviser_01", "Looks good")
        assert plan.status == ApprovalStatus.APPROVED
        assert len(plan.audit_log) == 2
    
    def test_reject(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        plan.reject("adviser_01", "Needs changes")
        assert plan.status == ApprovalStatus.REJECTED
    
    def test_cannot_approve_draft(self):
        plan = self._make_plan()
        with pytest.raises(ValueError, match="DRAFT"):
            plan.approve("adviser_01")
    
    def test_cannot_approve_rejected(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        plan.reject("adviser_01", "No good")
        with pytest.raises(ValueError):
            plan.approve("adviser_01")
    
    def test_pdf_export_blocked_when_not_approved(self):
        plan = self._make_plan()
        with pytest.raises(PermissionError, match="BLOCKED"):
            plan.export_pdf()
    
    def test_pdf_export_blocked_when_pending(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        with pytest.raises(PermissionError, match="BLOCKED"):
            plan.export_pdf()
    
    def test_pdf_export_allowed_when_approved(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        plan.approve("adviser_01")
        # Should not raise
        plan.export_pdf()
    
    def test_revision_workflow(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        plan.request_revision("adviser_01", "Change allocation")
        assert plan.status == ApprovalStatus.REVISION_REQUESTED
        # Can resubmit after revision
        plan.submit_for_review("adviser_01", "Updated allocation")
        assert plan.status == ApprovalStatus.PENDING_REVIEW
    
    def test_audit_log_tracks_all_changes(self):
        plan = self._make_plan()
        plan.submit_for_review("adviser_01")
        plan.request_revision("adviser_01", "Fix")
        plan.submit_for_review("adviser_01", "Fixed")
        plan.approve("adviser_02")
        
        assert len(plan.audit_log) == 4
        assert plan.audit_log[0].action == "SUBMIT_FOR_REVIEW"
        assert plan.audit_log[1].action == "REQUEST_REVISION"
        assert plan.audit_log[2].action == "SUBMIT_FOR_REVIEW"
        assert plan.audit_log[3].action == "APPROVE"
    
    def test_disclosures_auto_included(self):
        plan = self._make_plan()
        assert len(plan.disclosures) >= 4
        assert any("Direct" in d or "direct" in d for d in plan.disclosures)
        assert any("past performance" in d.lower() for d in plan.disclosures)
        assert any("market risk" in d.lower() for d in plan.disclosures)
