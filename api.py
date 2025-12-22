from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys

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

class CodeRequest(BaseModel):
    code: str

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
    # Use 127.0.0.1 for more stability on Windows
    uvicorn.run(app, host="127.0.0.1", port=8000)