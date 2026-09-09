from app.knowledge_base import add_resolved_bug
from app.analytics import generate_defect_analytics
from typing import Annotated


from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import DEFAULT_TOP_K, FRONTEND_DIR
from app.history_store import save_analysis
from app.orchestrator import MultiAgentOrchestrator
from app.rag import retrieve_similar_bugs
from app.report_generator import generate_report


app = FastAPI(
    title="AI Smart Bug Analyzer",
    version="0.1.0"
)

orchestrator = MultiAgentOrchestrator()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
@app.get("/api/analytics")
def get_analytics() -> dict:
    """
    Return defect pattern analytics
    based on all saved bug analyses.
    """

    return generate_defect_analytics()
@app.post("/api/knowledge-base/add")
async def add_bug_to_knowledge_base(data: dict):
    """
    Add a confirmed resolved bug to the historical
    knowledge base and vector store.
    """

    try:

        result = add_resolved_bug(
            bug_id=str(data.get("bug_id", "")).strip(),
            title=str(data.get("title", "")).strip(),
            description=str(
                data.get("description", "")
            ).strip(),
            component=str(
                data.get("component", "Unknown")
            ).strip(),
            severity=str(
                data.get("severity", "Unknown")
            ).strip(),
            priority=str(
                data.get("priority", "Unknown")
            ).strip(),
            root_cause=str(
                data.get("root_cause", "")
            ).strip(),
            resolution=str(
                data.get("resolution", "")
            ).strip(),
            stack_trace=str(
                data.get("stack_trace", "")
            ).strip(),
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            "ERROR: Failed to add resolved bug:"
        )

        print(error)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to add resolved bug "
                "to knowledge base."
            )
        )

# ============================================================
# READ UPLOADED FILES
# ============================================================

async def _read_upload(
    file: UploadFile | None
) -> str:

    if file is None:
        return ""

    content = await file.read()

    return content.decode(
        "utf-8",
        errors="replace"
    )


# ============================================================
# BUG ANALYSIS
# ============================================================

@app.post("/api/analyze")
async def analyze_bug(
    report_text: Annotated[str, Form()] = "",
    top_k: Annotated[int, Form()] = DEFAULT_TOP_K,
    bug_file: Annotated[UploadFile | None, File()] = None,
    stack_trace_file: Annotated[UploadFile | None, File()] = None,
    log_file: Annotated[UploadFile | None, File()] = None,
):

    print("\n========================================")
    print("NEW BUG ANALYSIS REQUEST")
    print("========================================")

    # Collect submitted information
    parts = [
        report_text,
        await _read_upload(bug_file),
        await _read_upload(stack_trace_file),
        await _read_upload(log_file),
    ]

    combined = "\n\n".join(
        part
        for part in parts
        if part and part.strip()
    )

    print("Received bug report:")
    print(combined[:500])

    # Validate input
    if not combined.strip():
        raise HTTPException(
            status_code=400,
            detail="Submit bug text or at least one file."
        )

    # Retrieve similar bugs
    print("Running RAG retrieval...")

    retrieval = retrieve_similar_bugs(
        combined,
        top_k=max(
            1,
            min(top_k, 10)
        )
    )

    print(
        f"Retrieved {len(retrieval.matches)} "
        "historical matches."
    )

    # Run all AI agents
    print("Running AI agents...")

    analysis = orchestrator.analyze(
        combined,
        retrieval.matches
    )

    print("AI analysis completed.")

    # Combine analysis and retrieval
    result = {
        **analysis,
        **retrieval.model_dump()
    }

    # Save analysis history
    print("----------------------------------------")
    print("Saving analysis history...")

    save_analysis(
        combined,
        result
    )

    print(
        "SUCCESS: Analysis saved to:"
    )

    print(
        "data/analysis_history.json"
    )

    print("----------------------------------------")
    print("Returning analysis result.")
    print("========================================\n")

    return result


# ============================================================
# PDF REPORT
# ============================================================

@app.post("/api/report")
async def download_report(
    data: dict
):

    pdf = generate_report(data)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=Bug_Analysis_Report.pdf"
        },
    )