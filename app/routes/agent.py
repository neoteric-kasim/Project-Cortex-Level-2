import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import query_index

router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(req: ChatRequest):
    try:
        question = req.question.strip()

        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        print(f"👉 Question: {question}")

        response = query_index(question)

        if not response:
            raise HTTPException(status_code=500, detail="No response from model")

        answer = str(response).strip()

        print(f"✅ Answer: {answer}")

        return {
            "answer": answer
        }

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        print("🔥 FULL ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )