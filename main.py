from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    user_totals: dict[str, float] = {}
    for e in events:
        if e.amount > 0:
            user_totals[e.user] = user_totals.get(e.user, 0) + e.amount

    top_user = max(user_totals, key=user_totals.get) if user_totals else None

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
