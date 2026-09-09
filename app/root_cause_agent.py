from dataclasses import dataclass

from app.models import SimilarBug


@dataclass
class RootCauseResult:
    hypothesis: str
    confidence: float
    supporting_evidence: list[dict[str, str | float]]
    reasoning: str


class RootCauseAgent:
    def analyze(
        self,
        report: str,
        matches: list[SimilarBug],
        exception_type: str = "Unknown",
        component: str = "General",
    ) -> RootCauseResult:
        text = report.lower()
        evidence = self._build_evidence(matches[:3])
        confidence = self._confidence(matches, exception_type)

        if exception_type and exception_type != "Unknown":
            hypothesis = (
                f"The most probable root cause is an unhandled {exception_type} "
                f"in the {component} component."
            )
            reasoning = "The submitted evidence includes a recognizable exception and similar historical defects."
        elif "timeout" in text or "timed out" in text:
            hypothesis = (
                f"The most probable root cause is a timeout or slow dependency path "
                f"affecting the {component} component."
            )
            reasoning = "Timeout language in the report points to latency, dependency, or retry handling issues."
        elif "null" in text or "none" in text:
            hypothesis = (
                f"The most probable root cause is missing state validation in the "
                f"{component} component."
            )
            reasoning = "Null-like terms usually indicate an object was used before initialization."
        elif matches:
            top = matches[0]
            hypothesis = (
                f"The most probable root cause resembles historical defect {top.bug_id}: "
                f"{top.title or 'similar failure pattern'}."
            )
            reasoning = "The submitted report is semantically close to historical bug records."
        else:
            hypothesis = (
                f"The most probable root cause is a defect in the {component} flow, "
                "but more stack trace or log evidence is needed."
            )
            reasoning = "No strong historical evidence or exception signature was available."

        return RootCauseResult(
            hypothesis=hypothesis,
            confidence=confidence,
            supporting_evidence=evidence,
            reasoning=reasoning,
        )

    def _build_evidence(self, matches: list[SimilarBug]) -> list[dict[str, str | float]]:
        evidence = []
        for match in matches:
            evidence.append(
                {
                    "bug_id": match.bug_id,
                    "title": match.title or "Historical defect",
                    "component": match.component or "Unknown",
                    "resolution": match.resolution or "Unknown",
                    "similarity": match.score,
                    "summary": self._summary(match.text),
                }
            )
        return evidence

    def _confidence(self, matches: list[SimilarBug], exception_type: str) -> float:
        if not matches:
            return 0.55 if exception_type != "Unknown" else 0.45

        average_score = sum(match.score for match in matches[:3]) / min(len(matches), 3)
        confidence = 0.45 + min(average_score, 1.0) * 0.35

        if exception_type != "Unknown":
            confidence += 0.15

        return round(min(confidence, 0.96), 2)

    def _summary(self, text: str, limit: int = 220) -> str:
        clean = " ".join(text.split())
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."
