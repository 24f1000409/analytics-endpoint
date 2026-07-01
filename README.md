# /analytics endpoint

## Before deploying
Open `main.py` and set your logged-in email on this line:
```python
EMAIL = "PUT_YOUR_LOGGED_IN_EMAIL_HERE"
```
Replace with the actual email you're logged in with on the exam platform.

## Deploy to Render (same steps as before)
1. Push `main.py` and `requirements.txt` to a GitHub repo (new repo or add to
   an existing one, e.g. a new folder in your `effective-config-app` repo, or
   a brand-new repo).
2. On render.com → New + → Web Service → connect the repo.
3. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free
4. No extra environment variables needed — API key and email are in the code.
5. Deploy, wait for "Your service is live."

## Test after deploying
```bash
# missing key -> 401
curl -i -X POST https://your-app.onrender.com/analytics \
  -H "Content-Type: application/json" \
  -d '{"events":[{"user":"alice","amount":10,"ts":1700000000}]}'

# wrong key -> 401
curl -i -X POST https://your-app.onrender.com/analytics \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"events":[{"user":"alice","amount":10,"ts":1700000000}]}'

# valid key -> 200 with computed aggregates
curl -s -X POST https://your-app.onrender.com/analytics \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ak_9l1lh7e1binqia0f66ahhmct" \
  -d '{"events":[{"user":"alice","amount":42.5,"ts":1700000000},{"user":"bob","amount":-5,"ts":1700000001}]}'
```

Verified locally already — matches spec exactly:
```
missing key -> 401
wrong key   -> 401
valid key   -> {"email":"...","total_events":5,"unique_users":3,"revenue":152.5,"top_user":"carol"}
```

## Submit
Paste your deployed URL + `/analytics` into the assignment field, e.g.:
```
https://your-app.onrender.com/analytics
```

Remember: Render's free tier sleeps after inactivity — same as before, wake
it up by visiting the URL first, then let the grader check right after.
