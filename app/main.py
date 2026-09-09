from typing import Annotated
from app.orchestrator import MultiAgentOrchestrator
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import DEFAULT_TOP_K, FRONTEND_DIR
from app.rag import retrieve_similar_bugs
from fastapi.responses import Response
from app.report_generator import generate_report

app = FastAPI(title="AI Smart Bug Analyzer", version="0.1.0")
orchestrator = MultiAgentOrchestrator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def _read_upload(file: UploadFile | None) -> str:
    if file is None:
        return ""
    content = await file.read()
    return content.decode("utf-8", errors="replace")


@app.post("/api/analyze")
async def analyze_bug(
    report_text: Annotated[str, Form()] = "",
    top_k: Annotated[int, Form()] = DEFAULT_TOP_K,
    bug_file: Annotated[UploadFile | None, File()] = None,
    stack_trace_file: Annotated[UploadFile | None, File()] = None,
    log_file: Annotated[UploadFile | None, File()] = None,
):
    parts = [
        report_text,
        await _read_upload(bug_file),
        await _read_upload(stack_trace_file),
        await _read_upload(log_file),
    ]

    combined = "\n\n".join(part for part in parts if part.strip())

    if not combined.strip():
        raise HTTPException(
            status_code=400,
            detail="Submit bug text or at least one file."
        )

    # Retrieve similar bugs
    retrieval = retrieve_similar_bugs(
        combined,
        top_k=max(1, min(top_k, 10))
    )

    # Run analysis agents with historical evidence from RAG
    analysis = orchestrator.analyze(combined, retrieval.matches)

    # Return combined response
    return {
        **analysis,
        **retrieval.model_dump()
    }
@app.post("/api/report")
async def download_report(data: dict):

    pdf = generate_report(data)

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=Bug_Analysis_Report.pdf"
        },
    )
