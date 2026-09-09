from dataclasses import dataclass

from app.models import SimilarBug


@dataclass
class DuplicateMatch:
    bug_id: str
    title: str
    component: str
    status: str
    resolution: str
    similarity: float
    summary: str
    resolution_summary: str


class DuplicateDetectionAgent:
    def analyze(self, matches: list[SimilarBug], limit: int = 5) -> list[DuplicateMatch]:
        candidates = sorted(matches, key=lambda match: match.score, reverse=True)
        duplicates: list[DuplicateMatch] = []

        for match in candidates:
            if match.score < 0.35:
                continue

            duplicates.append(
                DuplicateMatch(
                    bug_id=match.bug_id,
                    title=match.title or "Historical defect",
                    component=match.component or "Unknown",
                    status=match.status or "Unknown",
                    resolution=match.resolution or "Unknown",
                    similarity=match.score,
                    summary=self._summary(match.text),
                    resolution_summary=self._resolution_summary(match),
                )
            )

            if len(duplicates) >= limit:
                break

        return duplicates

    def _resolution_summary(self, match: SimilarBug) -> str:
        resolution = (match.resolution or "").strip()
        status = (match.status or "").strip()

        if resolution and resolution.lower() != "unknown":
            return f"Historical resolution: {resolution}."
        if status and status.lower() != "unknown":
            return f"Historical status: {status}. Review this issue before creating a new fix path."
        return "No resolution summary is available in the historical record."

    def _summary(self, text: str, limit: int = 200) -> str:
        clean = " ".join(text.split())
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."
