import os
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Optional
import sys
import json
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

# NVIDIA API Setup (OpenAI-compatible)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if NVIDIA_API_KEY:
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_API_KEY
    )
    MODEL_NAME = "openai/gpt-oss-120b"
    print(f"NVIDIA API configured with model: {MODEL_NAME}")
else:
    print("Warning: NVIDIA_API_KEY not found.")
    client = None

# OpenAI-compatible tool definitions
tools_openai_format = [
    {
        "type": "function",
        "function": {
            "name": "create_visualization",
            "description": "Create various types of charts and visualizations from data. Supports filtering, grouping, and aggregations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "scatter", "hist", "pie", "box", "violin", "heatmap", "area", "count"],
                        "description": "Type of chart to create"
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column name for X-axis"
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Column name for Y-axis (optional for some charts)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title",
                        "default": "Chart"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Data file to use (defaults to active file)"
                    },
                    "filter_column": {
                        "type": "string",
                        "description": "Column to filter on (optional)"
                    },
                    "filter_value": {
                        "type": "string",
                        "description": "Value to filter for (optional)"
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": ["count", "sum", "mean", "median", "min", "max"],
                        "description": "Aggregation function (optional)"
                    },
                    "group_by": {
                        "type": "string",
                        "description": "Column to group by before aggregation (optional)"
                    }
                },
                "required": ["chart_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_data_summary",
            "description": "Get a summary of all loaded data files including columns and sample data",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

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
    role: str = "admin"

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
    if not NVIDIA_API_KEY:
        raise HTTPException(status_code=500, detail="NVIDIA API not configured")
    
    try:
        # 1. Save User Message
        user_msg = ChatMessage(role="user", content=request.message, user_role=request.role)
        db.add(user_msg)
        db.commit()

        # 2. Reconstruct History for OpenAI format
        # OpenAI expects roles 'user' and 'assistant'
        previous_messages = db.query(ChatMessage).filter(ChatMessage.user_role == request.role).order_by(ChatMessage.timestamp).all()
        
        messages = []
        
        # Add system message with context
        import tools
        files_info = f"Available data files: {list(tools.dataframes.keys())}. Active file: {tools.active_file}" if tools.dataframes else "No data files loaded yet."
        
        system_instruction = f"""You are a PROACTIVE data analyst assistant. {files_info}

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. **NEVER** write fake image paths like ![Chart](/static/something.png) in your response
2. **ONLY** include image markdown that was returned by the create_visualization tool
3. If you want to show a chart, you MUST call the create_visualization function first
4. Wait for the tool to return the actual image path, then include that exact path in your response
5. DO NOT make up or invent image filenames - only use what the tool returns

DATA ACCESS:
- Available files: {list(tools.dataframes.keys()) if tools.dataframes else 'None'}
- Active file: {tools.active_file if tools.active_file else 'None'}
- If user doesn't specify a file, use the Active file

VISUALIZATION REQUIREMENTS:
- For comparisons, trends, distributions, or data analysis → CALL create_visualization tool
- Available chart types: bar, line, scatter, hist, pie, box, violin, heatmap, area, count
- Example: To compare groups, use chart_type='bar', x_column='group_column', y_column='value_column', aggregation='mean'
- For filtering: use filter_column and filter_value parameters
- For grouping: use group_by parameter

RESPONSE FORMAT:
- First call the tool (if visualization needed)
- Then write your analysis
- Include the EXACT image markdown returned by the tool (e.g., ![Chart](/static/charts/uuid.png))
- Never reference images that don't exist"""
        
        messages.append({"role": "system", "content": system_instruction})
        
        # Build conversation history (excluding the current message)
        for msg in previous_messages[:-1]:
            role = "assistant" if msg.role == "model" else msg.role
            messages.append({"role": role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})

        # 3. Get Response with tool calling
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools_openai_format,
                tool_choice="auto",
                temperature=1,
                top_p=1,
                max_tokens=4096,
                stream=False
            )
            
            # Handle tool calls
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                # Execute tool calls
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[TOOL CALL] {function_name} with args: {function_args}")
                    
                    # Execute the function
                    if function_name == "create_visualization":
                        from tools import create_visualization
                        function_response = create_visualization(**function_args)
                    elif function_name == "get_data_summary":
                        from tools import get_data_summary
                        function_response = get_data_summary()
                    else:
                        function_response = f"Unknown function: {function_name}"
                    
                    # Add function response to messages
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response)
                    })
                
                # Get final response after tool execution
                second_response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=1,
                    top_p=1,
                    max_tokens=4096,
                    stream=False
                )
                response_text = second_response.choices[0].message.content
            else:
                response_text = response_message.content
            
            # Handle empty responses
            if not response_text or response_text.strip() == "":
                print("[WARNING] Model returned empty response, using fallback")
                response_text = "I understand you want to analyze the data. Let me help you with that. Could you please rephrase your question or be more specific about what you'd like to see?"
            
            # FALLBACK: Detect if model returned JSON instead of calling tool
            if response_text and response_text.strip().startswith('{') and 'chart_type' in response_text:
                try:
                    params = json.loads(response_text.strip())
                    print(f"[FALLBACK] Model returned JSON, auto-calling create_visualization with: {params}")
                    
                    # Extract parameters
                    chart_params = {
                        'chart_type': params.get('chart_type', 'bar'),
                        'x_column': params.get('x_column'),
                        'y_column': params.get('y_column'),
                        'title': params.get('title', 'Chart'),
                        'filename': params.get('filename') or params.get('file_name') or params.get('file_path') or params.get('file'),
                        'aggregation': params.get('aggregation'),
                        'group_by': params.get('group_by'),
                        'filter_column': params.get('filter_column'),
                        'filter_value': params.get('filter_value')
                    }
                    # Remove None values
                    chart_params = {k: v for k, v in chart_params.items() if v is not None}
                    
                    from tools import create_visualization
                    chart_result = create_visualization(**chart_params)
                    
                    # Generate a proper response
                    response_text = f"Here's the visualization you requested:\n\n{chart_result}\n\nThe chart shows the distribution of {chart_params.get('x_column', 'data')} from the dataset."
                except Exception as e:
                    print(f"[FALLBACK ERROR] Failed to parse JSON and create chart: {e}")
                    response_text = "I understand you want a visualization. Let me create that for you."
            
            print(f"Model Response: {response_text}")
            
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
