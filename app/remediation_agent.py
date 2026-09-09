from dataclasses import dataclass


@dataclass
class RemediationResult:
    recommendation: str
    confidence: float
    action_items: list[str]
    best_practices: list[str]


class RemediationAgent:
    def analyze(
        self,
        report: str,
        triage: dict,
        log_analysis: dict,
        root_cause: dict,
        duplicate_matches: list[dict],
    ) -> RemediationResult:
        text = report.lower()
        exception_type = log_analysis.get("exception_type", "Unknown")
        component = triage.get("component", "General")
        severity = triage.get("severity", "Medium")

        action_items = [
            f"Reproduce the defect in the {component} flow using the submitted steps and logs.",
            "Add a regression test that captures the failing path before changing production code.",
        ]

        if exception_type != "Unknown":
            action_items.append(
                f"Trace the {exception_type} source and guard the failing object or input before it is used."
            )

        if "timeout" in text or "timed out" in text:
            action_items.append(
                "Review timeout settings, retry behavior, and dependency health for the failing request path."
            )

        if duplicate_matches:
            action_items.append(
                f"Compare against historical bug {duplicate_matches[0].get('bug_id')} before implementing a new fix."
            )

        recommendation = self._recommendation(component, exception_type, root_cause, duplicate_matches)
        confidence = self._confidence(root_cause, duplicate_matches, severity)

        return RemediationResult(
            recommendation=recommendation,
            confidence=confidence,
            action_items=action_items,
            best_practices=[
                "Keep the fix narrow and close to the failing component boundary.",
                "Validate uploaded/user-provided input before processing it.",
                "Log the failure context without exposing secrets or personal data.",
                "Link the regression test to the historical duplicate or root-cause evidence.",
            ],
        )

    def _recommendation(
        self,
        component: str,
        exception_type: str,
        root_cause: dict,
        duplicate_matches: list[dict],
    ) -> str:
        if duplicate_matches and duplicate_matches[0].get("resolution", "").lower() not in {"", "unknown"}:
            return (
                f"Start from the historical resolution for duplicate candidate "
                f"{duplicate_matches[0].get('bug_id')}: {duplicate_matches[0].get('resolution')}."
            )

        if exception_type != "Unknown":
            return (
                f"Fix the {component} code path by adding validation and error handling around the "
                f"operation that triggers {exception_type}."
            )

        return (
            f"Investigate the {component} code path highlighted by the root cause hypothesis: "
            f"{root_cause.get('hypothesis', 'additional evidence required')}."
        )

    def _confidence(self, root_cause: dict, duplicate_matches: list[dict], severity: str) -> float:
        confidence = float(root_cause.get("confidence", 0.5)) * 0.75

        if duplicate_matches:
            confidence += min(float(duplicate_matches[0].get("similarity", 0)), 1.0) * 0.2

        if severity in {"Critical", "High"}:
            confidence += 0.03

        return round(min(confidence, 0.95), 2)
