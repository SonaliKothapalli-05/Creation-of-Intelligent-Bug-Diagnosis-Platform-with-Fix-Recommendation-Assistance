import json
from datetime import datetime
from pathlib import Path


# Always use the project's root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

HISTORY_FILE = PROJECT_ROOT / "data" / "analysis_history.json"


def save_analysis(report: str, analysis: dict) -> None:
    """Save a completed bug analysis for future analytics."""

    # Make sure data folder exists
    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    records = []

    # Read existing history
    if HISTORY_FILE.exists():
        try:
            with open(
                HISTORY_FILE,
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

    # Create new record
    record = {
        "timestamp": datetime.now().isoformat(),
        "report": report,
        "analysis": analysis
    }

    records.append(record)

    # Save updated history
    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"History saved successfully: {HISTORY_FILE}"
    )


def load_analysis_history() -> list:
    """Load all previously saved bug analyses."""

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data if isinstance(data, list) else []

    except (
        json.JSONDecodeError,
        OSError
    ):
        return []