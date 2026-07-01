from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# CORS: allow the exam page to call this endpoint directly from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# IMPORTANT: Starlette's CORSMiddleware only attaches CORS headers to
# responses that flow back through it normally. If an unhandled exception
# escapes all the way to Starlette's ServerErrorMiddleware, the resulting
# 500 response bypasses CORSMiddleware entirely and the browser reports it
# as a (misleading) "CORS blocked" error instead of a 500. This catch-all
# handler converts any unexpected exception into a normal JSONResponse so
# it passes back through CORSMiddleware and keeps the CORS headers intact.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# --- Fill these in before deploying ---
API_KEY = "ak_9l1lh7e1binqia0f66ahhmct"
EMAIL = "24f1000409@ds.study.iitm.ac.in"
# ---------------------------------------


class Event(BaseModel):
    user: str
    amount: float
    ts: Optional[int] = None


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(
    payload: AnalyticsRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")

    events = payload.events
    total_events = len(events)
    unique_users = len({e.user for e in events})

    # revenue: sum of amounts where amount > 0 only
    revenue = sum(e.amount for e in events if e.amount > 0)

    # top_user: user whose positive-amount total is highest
    user_totals: Dict[str, float] = {}
    for e in events:
        if e.amount > 0:
            user_totals[e.user] = user_totals.get(e.user, 0) + e.amount

    top_user: Optional[str] = None
    if user_totals:
        top_user = max(user_totals.items(), key=lambda item: item[1])[0]

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }


@app.get("/")
def root():
    return {"status": "ok", "endpoint": "POST /analytics"}
