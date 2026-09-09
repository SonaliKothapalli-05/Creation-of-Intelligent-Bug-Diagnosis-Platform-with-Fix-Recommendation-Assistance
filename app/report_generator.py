from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_report(data):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    # ===========================
    # TITLE
    # ===========================

    story.append(
        Paragraph(
            "<font size='22' color='darkblue'><b>AI SMART BUG ANALYZER & FIX ADVISOR</b></font>",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            "<font size='15'><b>Bug Analysis Report</b></font>",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 20))

    # ===========================
    # BUG REPORT
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Bug Report</font></b>", styles["Heading2"])
    )

    story.append(Spacer(1, 8))

    report = data.get("report", "No bug report provided.")

    story.append(
        Paragraph(report.replace("\n", "<br/>"), styles["BodyText"])
    )

    story.append(Spacer(1, 20))

    # ===========================
    # TRIAGE ANALYSIS
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Triage Analysis</font></b>", styles["Heading2"])
    )

    story.append(Spacer(1, 8))

    triage = data.get("triage", {})

    triage_table = Table(
        [
            ["Field", "Value"],
            ["Severity", triage.get("severity", "-")],
            ["Priority", triage.get("priority", "-")],
            ["Component", triage.get("component", "-")],
            [
                "Confidence",
                f"{round(triage.get('confidence', 0) * 100)}%",
            ],
            ["Reasoning", triage.get("reasoning", "-")],
        ],
        colWidths=[160, 320],
    )

    triage_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (0, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(triage_table)

    story.append(Spacer(1, 20))

    # ===========================
    # LOG ANALYSIS
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Log Analysis</font></b>", styles["Heading2"])
    )

    story.append(Spacer(1, 8))

    log = data.get("log_analysis", {})

    log_table = Table(
        [
            ["Field", "Value"],
            ["Exception Type", log.get("exception_type", "-")],
            ["Failure Point", log.get("failure_point", "-")],
            ["Affected Code Path", log.get("affected_code_path", "-")],
            [
                "Confidence",
                f"{round(log.get('confidence', 0) * 100)}%",
            ],
            ["Reasoning", log.get("reasoning", "-")],
        ],
        colWidths=[160, 320],
    )

    log_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (0, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(log_table)

    story.append(Spacer(1, 20))

    # ===========================
    # ROOT CAUSE ANALYSIS
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Root Cause Analysis</font></b>", styles["Heading2"])
    )

    story.append(Spacer(1, 8))

    root_cause = data.get("root_cause", {})

    root_table = Table(
        [
            ["Field", "Value"],
            ["Hypothesis", root_cause.get("hypothesis", "-")],
            ["Confidence", f"{round(root_cause.get('confidence', 0) * 100)}%"],
            ["Reasoning", root_cause.get("reasoning", "-")],
        ],
        colWidths=[160, 320],
    )

    root_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (0, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(root_table)
    story.append(Spacer(1, 10))

    for item in root_cause.get("supporting_evidence", [])[:3]:
        story.append(
            Paragraph(
                f"<b>Evidence Bug {item.get('bug_id', '-')}:</b> {item.get('title', '-')}",
                styles["BodyText"],
            )
        )
        story.append(
            Paragraph(
                f"Similarity: {round(item.get('similarity', 0) * 100)}% | Resolution: {item.get('resolution', '-')}",
                styles["BodyText"],
            )
        )
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 20))

    # ===========================
    # REMEDIATION
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Recommended Fix</font></b>", styles["Heading2"])
    )

    story.append(Spacer(1, 8))

    remediation = data.get("remediation", {})

    story.append(
        Paragraph(
            f"<b>Recommendation:</b> {remediation.get('recommendation', '-')}",
            styles["BodyText"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Confidence:</b> {round(remediation.get('confidence', 0) * 100)}%",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 8))

    for item in remediation.get("action_items", []):
        story.append(Paragraph(f"- {item}", styles["BodyText"]))

    story.append(Spacer(1, 20))

    # ===========================
    # DUPLICATES
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Duplicate Detection</font></b>", styles["Heading2"])
    )

    duplicates = data.get("duplicate_matches", [])

    if duplicates:
        for item in duplicates[:5]:
            story.append(
                Paragraph(
                    f"<b>Bug {item.get('bug_id', '-')}:</b> {item.get('title', '-')}",
                    styles["BodyText"],
                )
            )
            story.append(
                Paragraph(
                    f"Similarity: {round(item.get('similarity', 0) * 100)}% | {item.get('resolution_summary', '-')}",
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 8))
    else:
        story.append(Paragraph("No likely duplicates found.", styles["BodyText"]))

    story.append(Spacer(1, 20))

    # ===========================
    # SIMILAR BUGS
    # ===========================

    story.append(
        Paragraph(
            "<b><font size='16'>Similar Historical Bugs</font></b>",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 10))

    matches = data.get("matches", [])

    if matches:
        for index, match in enumerate(matches, start=1):

            story.append(
                Paragraph(
                    f"<b>{index}. Bug #{match.get('bug_id','')}</b>",
                    styles["Heading3"],
                )
            )

            story.append(
                Paragraph(
                    f"<b>Title:</b> {match.get('title','')}",
                    styles["BodyText"],
                )
            )

            story.append(
                Paragraph(
                    f"<b>Match Score:</b> {round(match.get('score',0)*100)}%",
                    styles["BodyText"],
                )
            )

            story.append(Spacer(1, 10))

    else:
        story.append(
            Paragraph("No similar bugs found.", styles["BodyText"])
        )

    story.append(Spacer(1, 20))

    # ===========================
    # SUMMARY
    # ===========================

    story.append(
        Paragraph("<b><font size='16'>Report Summary</font></b>", styles["Heading2"])
    )

    summary_table = Table(
        [
            ["Item", "Value"],
            ["Similar Bugs Retrieved", str(len(matches))],
            ["AI Agents Executed", "2"],
            ["Retrieval Method", "Semantic Search (RAG)"],
            ["Status", "Analysis Completed Successfully"],
        ],
        colWidths=[220, 260],
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (0, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(summary_table)

    story.append(Spacer(1, 30))

    # ===========================
    # FOOTER
    # ===========================

    story.append(
        Paragraph(
            "<font color='grey'><i>Generated by AI Smart Bug Analyzer & Fix Advisor</i></font>",
            styles["Normal"],
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
