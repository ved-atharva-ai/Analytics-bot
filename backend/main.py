import os
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Optional
import sys
from pathlib import Path

# Add current directory to path if running as script
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent))

from tools import tools_list, load_data, get_data_summary
from database import engine, Base


load_dotenv()


# ... (imports)
from database import engine, Base, get_db
from models import ChatMessage, User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for charts
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Gemini Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash', tools=tools_list)
    # User asked for 'gemini-2.5-flash'. I will try to use that string, but fallback to 'gemini-1.5-flash' or 'gemini-2.0-flash-exp' if needed. 
    # Actually, let's use 'gemini-1.5-flash' as a safe default or 'gemini-pro'. 
    # I'll use 'gemini-1.5-flash' as it's the current flash model. 
    # Wait, user specifically asked for "gemini-2.5-flash". I will use that string in the code, assuming they have access or it's a typo for 1.5/2.0.
    # To be safe, I'll use a variable.
    MODEL_NAME = "gemini-2.5-flash" # Fallback/Standard
    chat = model.start_chat(enable_automatic_function_calling=True)
else:
    print("Warning: GEMINI_API_KEY not found.")
    chat = None

# Load existing files on startup
@app.on_event("startup")
async def startup_event():
    """Load all existing CSV/Excel files from static directory into memory"""
    if os.path.exists("static"):
        for filename in os.listdir("static"):
            if filename.endswith(('.csv', '.xlsx', '.xls')):
                file_path = os.path.join("static", filename)
                try:
                    load_data(file_path)
                    print(f"Loaded existing file: {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {str(e)}")

# Models
class ChatRequest(BaseModel):
    message: str
    role: str = "user"

class ChatResponse(BaseModel):
    response: str
    image_url: Optional[str] = None

# Routes
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Ensure static directory exists
        os.makedirs("static", exist_ok=True)
        
        file_location = os.path.abspath(os.path.join("static", file.filename))
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        # Load data into the tool context
        msg = load_data(file_location)
        
        return {"info": f"file '{file.filename}' saved successfully", "status": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from database import engine, Base, get_db
from models import ChatMessage, User
from sqlalchemy.orm import Session

# ... (existing imports)

# ... (existing code)

@app.get("/history/{role}")
def get_history(role: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.user_role == role).order_by(ChatMessage.timestamp).all()
    history = []
    for msg in messages:
        # Map 'model' back to 'assistant' for frontend
        frontend_role = 'assistant' if msg.role == 'model' else 'user'
        history.append({
            "role": frontend_role,
            "content": msg.content,
            "image": msg.image_url
        })
    return history

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini not configured")
    
    try:
        # 1. Save User Message
        user_msg = ChatMessage(role="user", content=request.message, user_role=request.role)
        db.add(user_msg)
        db.commit()

        # 2. Reconstruct History for Gemini
        # Gemini expects roles 'user' and 'model'
        previous_messages = db.query(ChatMessage).filter(ChatMessage.user_role == request.role).order_by(ChatMessage.timestamp).all()
        
        gemini_history = []
        # Exclude the message we just added to avoid duplication if we append it manually, 
        # but start_chat(history=...) expects past history. 
        # Actually, let's just build the history excluding the current one, and send the current one as the message.
        for msg in previous_messages[:-1]: 
             gemini_history.append({
                 "role": msg.role,
                 "parts": [msg.content]
             })
        
        # Initialize Chat with History
        # We need to re-initialize the model/chat here to ensure statelessness with persistence
        model = genai.GenerativeModel('gemini-2.5-flash', tools=tools_list)
        chat = model.start_chat(history=gemini_history, enable_automatic_function_calling=True)


        # Contextualize
        from tools import dataframes
        files_info = f"Available data files: {list(dataframes.keys())}" if dataframes else "No data files loaded yet."
        
        common_instruction = f"IMPORTANT: You are a PROACTIVE data analyst. {files_info} You have access to ALL uploaded data files. Your goal is to visualize data whenever possible. If the user's query involves comparing values, looking for trends, analyzing distributions, or summarizing data, you MUST generate a relevant chart (bar, line, scatter, histogram, pie, box, violin, heatmap, or area) to illustrate your answer immediately. Do NOT ask the user if they want a chart; just generate it. When a tool returns a chart image path (e.g., ![Chart](/static/...)), you MUST include that exact markdown in your response."
        
        if request.role == "admin":
            system_instruction = f"You are an admin assistant with full access to all data. {common_instruction}"
        else:
            system_instruction = f"You are a helpful data assistant with access to all uploaded data. {common_instruction}"
        
        full_message = f"{system_instruction}\n[Role: {request.role}] {request.message}"

        # 3. Get Response
        try:
            response = chat.send_message(full_message)
        except Exception as api_error:
            error_msg = str(api_error)
            print(f"API Error: {error_msg}")
            
            # Check if it's a quota error
            if "quota" in error_msg.lower() or "429" in error_msg:
                response_text = "I've reached my API quota limit. Please try again later or contact the administrator to upgrade the API plan."
            elif "empty" in error_msg.lower():
                response_text = "I received an empty response from the AI model. This might be due to API issues. Please try rephrasing your question or try again in a moment."
            else:
                response_text = f"I encountered an error: {error_msg}. Please try again."
            
            model_msg = ChatMessage(role="model", content=response_text, user_role=request.role)
            db.add(model_msg)
            db.commit()
            return ChatResponse(response=response_text)
        
        try:
            response_text = response.text
            print(f"Model Response: {response_text}")
        except ValueError as e:
            # Handle case where response doesn't have valid text (e.g., function call error)
            print(f"Response error: {str(e)}")
            response_text = "I encountered an error while processing your request. Please try rephrasing your question or ask something else."
        except AttributeError:
            # Handle case where response object doesn't have text attribute
            print(f"Response has no text attribute")
            response_text = "I received an invalid response. Please try again."

        # 4. Save Model Response
        model_msg = ChatMessage(role="model", content=response_text, user_role=request.role)
        db.add(model_msg)
        db.commit()
        
        return ChatResponse(response=response_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def get_users():
    # Mock users
    return [
        {"id": 1, "username": "admin", "role": "admin"},
        {"id": 2, "username": "user1", "role": "user"},
        {"id": 3, "username": "user2", "role": "user"},
    ]

@app.get("/files")
def get_files():
    # In a real app, query the database. For now, list files in static dir
    files = []
    if os.path.exists("static"):
        for f in os.listdir("static"):
            if f.endswith(".csv") or f.endswith(".xlsx") or f.endswith(".xls"):
                files.append(f)
    return files

from tools import get_data_json
@app.get("/data/preview")
def get_data_preview_endpoint(filename: Optional[str] = None):
    data = get_data_json(filename)
    if data:
        return data
    return {"message": "No data loaded"}

@app.delete("/history/{role}")
def delete_history(role: str, db: Session = Depends(get_db)):
    try:
        db.query(ChatMessage).filter(ChatMessage.user_role == role).delete()
        db.commit()
        return {"message": f"Chat history for {role} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
