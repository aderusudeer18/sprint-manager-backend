import os
from fastapi import APIRouter
from google import genai
from apis.schemas.ai import PromptRequest
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# PromptRequest moved to apis/schemas/ai.py


@router.post("/generate")
def send_task_to_gemini(request: PromptRequest):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=request.prompt
    )
    return {"result": response.text}
