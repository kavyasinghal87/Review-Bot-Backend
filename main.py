import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv  # Added this to load variables

# 1. Setup - Secure Loading
load_dotenv()  # This reads the key from your .env file
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY") 

# Check if key is loaded (for debugging)
if not os.environ.get("GOOGLE_API_KEY"):
    print("⚠️ ERROR: No API Key found. Check your .env file!")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

class AuditReport(BaseModel):
    status: str = Field(description="'SUCCESS' or 'ERROR'")
    errors: Optional[List[str]] = Field(description="List of errors found")
    complexity: Optional[str] = Field(description="Time complexity in Big O notation")
    hint: str = Field(description="One-sentence optimization suggestion")

parser = JsonOutputParser(pydantic_object=AuditReport)

# 2. Prompt
auditor_template = """
Analyze the following code snippet:
{code}

If there are bugs, report them. If clean, determine Big O complexity and a hint.
{format_instructions}
"""

auditor_prompt = ChatPromptTemplate.from_template(
    template=auditor_template,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
auditor_chain = auditor_prompt | llm | parser

# 3. Optimization Logic (CRITICAL: Added this for api.py)
def get_optimized_code(original_code):
    opt_prompt = f"Optimize the following code for better Time Complexity. Provide ONLY the optimized code block without explanation:\n\n{original_code}"
    response = llm.invoke(opt_prompt)
    return response.content

# 4. Reliable Interaction Logic
def run_project():
    print("\n--- 🤖 REVIEW-BOT: STAGE 1 ---")
    print("Paste your code below. When finished, type 'DONE' on a new line and press Enter:")
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "DONE":
            break
        lines.append(line)
    
    user_code = "\n".join(lines)
    if not user_code.strip():
        print("No code detected.")
        return

    print("\n🔍 Auditing... (Connecting to Gemini AI)")
    
    try:
        result = auditor_chain.invoke({"code": user_code})
        print(f"DEBUG: AI returned status '{result['status']}'") 

        if result['status'].upper() == 'ERROR':
            print(f"\n❌ BUGS FOUND: {result.get('errors', 'No details provided')}")
        else:
            print(f"\n✅ CODE IS VALID!")
            print(f"📊 Current Complexity: {result.get('complexity', 'Unknown')}")
            print(f"💡 Hint: {result['hint']}")

            choice = input("\nWould you like to optimize this? (y/n): ")
            if choice.lower() == 'y':
                print("\n🚀 GENERATING OPTIMIZED CODE...")
                # Calls the new function we just added
                print(get_optimized_code(user_code))

    except Exception as e:
        print(f"\n⚠️ ERROR: {e}")

if __name__ == "__main__":
    run_project()