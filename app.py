from __future__ import annotations

import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\.")
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from typing import List

from reddit_client import fetch_thread
from summariser import analyse_thread
from models import AnalysisResult

app = FastAPI(title="Reddit Thread Summariser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummariseRequest(BaseModel):
    url: str = Field(description="Reddit post URL to analyse")


class ThreadMeta(BaseModel):
    title: str
    subreddit: str
    score: int
    num_comments: int


class SummariseResponse(AnalysisResult):
    thread: ThreadMeta


@app.post("/api/summarise", response_model=SummariseResponse)
def summarise(request: SummariseRequest) -> SummariseResponse:
    try:
        thread = fetch_thread(request.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    try:
        result = analyse_thread(thread)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return SummariseResponse(
        **result.model_dump(),
        thread=ThreadMeta(
            title=thread.title,
            subreddit=thread.subreddit,
            score=thread.score,
            num_comments=thread.num_comments,
        ),
    )
