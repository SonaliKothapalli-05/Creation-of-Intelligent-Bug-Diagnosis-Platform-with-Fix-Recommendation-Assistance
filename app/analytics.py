from collections import Counter

from app.history_store import load_analysis_history


def generate_defect_analytics() -> dict:
    """
    Analyze all previously submitted bug analyses
    and identify recurring defect patterns.
    """

    history = load_analysis_history()

    if not history:
        return {
            "total_bugs": 0,
            "severity_distribution": {},
            "priority_distribution": {},
            "component_frequency": {},
            "exception_frequency": {},
            "recurring_themes": [],
            "systemic_patterns": [],
        }

    severity_counter = Counter()
    priority_counter = Counter()
    component_counter = Counter()
    exception_counter = Counter()

    # --------------------------------------------------------
    # Analyze every saved bug
    # --------------------------------------------------------

    for record in history:

        analysis = record.get("analysis", {})

        # -----------------------------
        # Triage
        # -----------------------------

        triage = analysis.get("triage", {})

        severity = triage.get("severity")
        priority = triage.get("priority")
        component = triage.get("component")

        if severity and severity != "Unknown":
            severity_counter[str(severity)] += 1

        if priority and priority != "Unknown":
            priority_counter[str(priority)] += 1

        if component and component != "Unknown":
            component_counter[str(component)] += 1

        # -----------------------------
        # Log Analysis
        # -----------------------------

        log_analysis = analysis.get(
            "log_analysis",
            {}
        )

        exception_type = log_analysis.get(
            "exception_type"
        )

        if (
            exception_type
            and exception_type != "Unknown"
        ):
            exception_counter[
                str(exception_type)
            ] += 1

    # --------------------------------------------------------
    # Recurring Themes
    # --------------------------------------------------------

    recurring_themes = []

    for component, count in component_counter.most_common():

        if count >= 2:

            recurring_themes.append({
                "theme": (
                    f"Recurring issues in {component}"
                ),
                "component": component,
                "occurrences": count
            })

    for exception_type, count in (
        exception_counter.most_common()
    ):

        if count >= 2:

            recurring_themes.append({
                "theme": (
                    f"Recurring {exception_type} errors"
                ),
                "exception_type": exception_type,
                "occurrences": count
            })

    # --------------------------------------------------------
    # Systemic Patterns
    # --------------------------------------------------------

    systemic_patterns = []

    for component, count in component_counter.items():

        if count >= 3:

            systemic_patterns.append({
                "pattern": "High-frequency component",
                "component": component,
                "occurrences": count,
                "description": (
                    f"{component} appears frequently "
                    "in submitted defects and may "
                    "indicate a systemic issue."
                )
            })

    for exception_type, count in (
        exception_counter.items()
    ):

        if count >= 3:

            systemic_patterns.append({
                "pattern": "Repeated exception type",
                "exception_type": exception_type,
                "occurrences": count,
                "description": (
                    f"{exception_type} occurs repeatedly "
                    "and may require deeper investigation."
                )
            })

    # --------------------------------------------------------
    # Final Analytics Result
    # --------------------------------------------------------

    return {
        "total_bugs": len(history),

        "severity_distribution": dict(
            severity_counter
        ),

        "priority_distribution": dict(
            priority_counter
        ),

        "component_frequency": dict(
            component_counter.most_common()
        ),

        "exception_frequency": dict(
            exception_counter.most_common()
        ),

        "recurring_themes": recurring_themes,

        "systemic_patterns": systemic_patterns,
    }