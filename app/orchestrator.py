from app.triage_agent import TriageAgent
from app.log_agent import LogAnalysisAgent
from app.root_cause_agent import RootCauseAgent
from app.duplicate_agent import DuplicateDetectionAgent
from app.remediation_agent import RemediationAgent
from app.models import SimilarBug


class MultiAgentOrchestrator:

    def __init__(self):
        self.triage_agent = TriageAgent()
        self.log_agent = LogAnalysisAgent()
        self.root_cause_agent = RootCauseAgent()
        self.duplicate_agent = DuplicateDetectionAgent()
        self.remediation_agent = RemediationAgent()

    def analyze(self, report: str, historical_matches: list[SimilarBug] | None = None):
        historical_matches = historical_matches or []

        triage = self.triage_agent.analyze(report)
        log = self.log_agent.analyze(report)

        triage_payload = {
            "severity": triage.severity,
            "priority": triage.priority,
            "component": triage.component,
            "confidence": triage.confidence,
            "reasoning": triage.reasoning,
        }

        log_payload = {
            "exception_type": log.exception_type,
            "failure_point": log.failure_point,
            "affected_code_path": log.affected_code_path,
            "confidence": log.confidence,
            "reasoning": log.reasoning,
        }

        root_cause = self.root_cause_agent.analyze(
            report=report,
            matches=historical_matches,
            exception_type=log.exception_type,
            component=triage.component,
        )

        root_cause_payload = {
            "hypothesis": root_cause.hypothesis,
            "confidence": root_cause.confidence,
            "supporting_evidence": root_cause.supporting_evidence,
            "reasoning": root_cause.reasoning,
        }

        duplicate_matches = [
            {
                "bug_id": match.bug_id,
                "title": match.title,
                "component": match.component,
                "status": match.status,
                "resolution": match.resolution,
                "similarity": match.similarity,
                "summary": match.summary,
                "resolution_summary": match.resolution_summary,
            }
            for match in self.duplicate_agent.analyze(historical_matches)
        ]

        remediation = self.remediation_agent.analyze(
            report=report,
            triage=triage_payload,
            log_analysis=log_payload,
            root_cause=root_cause_payload,
            duplicate_matches=duplicate_matches,
        )

        remediation_payload = {
            "recommendation": remediation.recommendation,
            "confidence": remediation.confidence,
            "action_items": remediation.action_items,
            "best_practices": remediation.best_practices,
        }

        return {
            "triage": {
                **triage_payload,
            },

            "log_analysis": {
                **log_payload,
            },

            "root_cause": root_cause_payload,
            "duplicate_matches": duplicate_matches,
            "remediation": remediation_payload,
        }
