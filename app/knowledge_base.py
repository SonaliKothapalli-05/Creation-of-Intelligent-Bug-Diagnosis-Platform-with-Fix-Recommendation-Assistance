import json
from datetime import datetime
from pathlib import Path

from app.embeddings import get_embedding_service
from app.models import BugChunk
from app.vector_store import get_vector_store


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESOLVED_BUGS_FILE = (
    PROJECT_ROOT / "data" / "resolved_bugs.json"
)


def add_resolved_bug(
    bug_id: str,
    title: str,
    description: str,
    component: str,
    severity: str,
    priority: str,
    root_cause: str,
    resolution: str,
    stack_trace: str = "",
) -> dict:
    """
    Add a confirmed resolved bug to the existing
    historical knowledge base.
    """

    # --------------------------------------------------------
    # Validate required information
    # --------------------------------------------------------

    if not bug_id.strip():
        raise ValueError("Bug ID is required.")

    if not title.strip():
        raise ValueError("Bug title is required.")

    if not description.strip():
        raise ValueError("Bug description is required.")

    if not resolution.strip():
        raise ValueError("Resolution is required.")

    # --------------------------------------------------------
    # Create searchable knowledge-base text
    # --------------------------------------------------------

    searchable_text = "\n".join(
        part
        for part in [
            f"Bug ID: {bug_id}",
            f"Title: {title}",
            f"Description: {description}",
            f"Component: {component}",
            f"Severity: {severity}",
            f"Priority: {priority}",
            f"Root Cause: {root_cause}",
            f"Resolution: {resolution}",
            f"Stack Trace: {stack_trace}",
            "Status: Resolved",
        ]
        if part
    )

    # --------------------------------------------------------
    # Create BugChunk
    # --------------------------------------------------------

    chunk = BugChunk(
        chunk_id=f"resolved-{bug_id}",
        bug_id=bug_id,
        text=searchable_text,
        metadata={
            "bug_id": bug_id,
            "title": title,
            "component": component or "Unknown",
            "severity": severity or "Unknown",
            "priority": priority or "Unknown",
            "status": "Resolved",
            "resolution": resolution,
            "root_cause": root_cause or "Unknown",
            "source": "resolved_bug",
        },
    )

    # --------------------------------------------------------
    # Generate embedding using existing service
    # --------------------------------------------------------

    embedding = get_embedding_service().embed(
        [chunk.text]
    )[0]

    # --------------------------------------------------------
    # Add to existing vector store
    # --------------------------------------------------------

    store = get_vector_store()

    store.add(
        [chunk],
        [embedding]
    )

    # --------------------------------------------------------
    # Also maintain a resolved-bug registry
    # --------------------------------------------------------

    RESOLVED_BUGS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    records = []

    if RESOLVED_BUGS_FILE.exists():

        try:

            with open(
                RESOLVED_BUGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                records = json.load(file)

            if not isinstance(records, list):
                records = []

        except (
            json.JSONDecodeError,
            OSError
        ):
            records = []

    record = {
        "timestamp": datetime.now().isoformat(),
        "bug_id": bug_id,
        "title": title,
        "description": description,
        "component": component,
        "severity": severity,
        "priority": priority,
        "root_cause": root_cause,
        "resolution": resolution,
        "stack_trace": stack_trace,
        "status": "Resolved",
    }

    # Replace an existing resolved record
    # with the same bug ID.
    records = [
        item
        for item in records
        if str(item.get("bug_id")) != str(bug_id)
    ]

    records.append(record)

    with open(
        RESOLVED_BUGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    return {
        "success": True,
        "bug_id": bug_id,
        "status": "Resolved",
        "chunk_id": chunk.chunk_id,
        "message": (
            "Resolved bug added to the "
            "historical knowledge base."
        ),
    }