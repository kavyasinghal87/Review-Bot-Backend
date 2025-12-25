from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
import os
import sqlite3

# Try to import your logic
try:
    from main import auditor_chain, get_optimized_code
except ImportError as e:
    print(f"CRITICAL ERROR: Could not find functions in main.py: {e}")
    sys.exit(1)

app = FastAPI()

# Enable CORS for the website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)''')
    conn.commit()
    conn.close()

init_db()

class LoginRequest(BaseModel):
    name: str
    email: str

class CodeRequest(BaseModel):
    code: str

# --- New Registration Endpoint ---
@app.post("/register")
async def register_visitor(request: LoginRequest):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO visitors (name, email) VALUES (?, ?)", 
                  (request.name, request.email))
        conn.commit()
        conn.close()
        return {"status": "SUCCESS"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.post("/audit")
async def audit_code(request: CodeRequest):
    try:
        result = auditor_chain.invoke({"code": request.code})
        return result
    except Exception as e:
        return {"status": "ERROR", "errors": [str(e)]}

@app.post("/optimize")
async def optimize_code(request: CodeRequest):
    try:
        faster_code = get_optimized_code(request.code)
        return {"optimized_code": faster_code}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    # Bind to 0.0.0.0 for Render production
    uvicorn.run(app, host="0.0.0.0", port=port)