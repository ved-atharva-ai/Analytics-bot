# AnalyticBot - AI-Powered Data Visualization Chatbot

A full-stack chatbot application that combines data analysis and visualization capabilities. Upload CSV/Excel files and interact with an AI assistant that automatically generates charts and provides insights using NVIDIA AI.

## Features

- 🤖 **AI-Powered Analysis**: Powered by NVIDIA API (openai/gpt-oss-120b)
- 📊 **Automatic Visualizations**: Generates charts proactively based on your questions
- 📁 **CSV/Excel Support**: Upload and analyze data files
- 💾 **Persistent Chat History**: All conversations saved to PostgreSQL database
- 👥 **Admin Interface**: Upload data and manage the system
- 🎨 **Modern UI**: Beautiful, responsive interface with animations
- 📈 **Flexible Charts**: Supports bar, line, scatter, histogram, pie, box, violin, heatmap, and area charts
- 🔍 **Advanced Filtering**: Filter, group, and aggregate data before visualization
- 🗑️ **Chat Management**: Delete history and start new conversations
- 🔄 **Intelligent Fallback**: Automatically handles model quirks and ensures charts are generated

## Tech Stack

### Frontend
- React (Vite)
- React Router
- React Markdown (message rendering)
- Framer Motion (animations)
- Axios (API calls)
- Lucide React (icons)

### Backend
- FastAPI
- Python 3.12
- NVIDIA API (OpenAI-compatible)
- PostgreSQL
- SQLAlchemy
- Pandas, Matplotlib, Seaborn

## Prerequisites

- Python 3.12 or higher
- Node.js 18 or higher
- PostgreSQL 12 or higher
- NVIDIA API key ([Get one here](https://build.nvidia.com/))

## Installation

### 1. Clone the Repository

```bash
cd ~/my-project/Analytic-bot
```

### 2. Set Up PostgreSQL Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE analytic_bot;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE analytic_bot TO postgres;
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
NVIDIA_API_KEY=your_nvidia_api_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/analytic_bot
```

**Note**: If your password contains special characters like `@`, URL-encode them:
- `@` becomes `%40`
- `#` becomes `%23`
- etc.

### 4. Install Backend Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install fastapi uvicorn openai sqlalchemy psycopg2-binary pandas matplotlib seaborn python-dotenv
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Option 1: Using the Run Script (Recommended)

**Linux/Mac:**
```bash
# Make the script executable (first time only)
chmod +x run_app.sh

# Run the application
./run_app.sh
```

**Windows:**
Double-click `run_app.bat` or run it from the command line:
```cmd
run_app.bat
```

This will start both the backend (port 8000) and frontend (port 5173).

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python backend/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Accessing the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Usage Guide

### Admin Dashboard

1. Navigate to **Admin Dashboard** from the sidebar
2. **Upload Data**: Click to upload CSV or Excel files (currently using student-mat.csv)
3. **View Files**: See all uploaded files in the list
4. **Preview Data**: Click on any file to preview its contents

### Chat Interface

1. Navigate to **Chat** from the sidebar
2. **Ask Questions**: Type natural language questions about your data
3. **View Charts**: Charts are automatically generated and displayed inline
4. **New Chat**: Click "New Chat" to clear history and start fresh

### Example Questions

**General Statistics:**
- "What is the average age of students?"
- "Show me the gender distribution"
- "How many students are there?"

**Visualizations:**
- "Compare health status distribution"
- "Show me age distribution"
- "Create a chart of study time vs final grades"

**Analysis:**
- "How does internet access affect grades?"
- "What's the relationship between study time and final grades?"
- "How effective is school support for struggling students?"
- "Compare performance between urban and rural students"

**Advanced:**
- "Show me correlation between mother's education and student grades"
- "How does alcohol consumption affect academic performance?"
- "Compare students who want higher education vs those who don't"

## Project Structure

```
Analytic-bot/
├── backend/
│   ├── main.py              # FastAPI application with NVIDIA API integration
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── tools.py             # AI tools for chart generation
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ChatInterface.jsx    # Chat UI
│   │   │   └── AdminDashboard.jsx   # Admin UI
│   │   ├── components/
│   │   │   └── Layout.jsx           # Main layout
│   │   ├── App.jsx          # Main app component
│   │   └── index.css        # Global styles
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── static/
│   ├── charts/              # Generated chart images
│   └── student-mat.csv      # Student performance dataset
├── .env                     # Environment variables
├── run_app.sh              # Application launcher (Linux/Mac)
├── run_app.bat             # Application launcher (Windows)
└── README.md               # This file
```

## API Endpoints

### Data Management
- `POST /upload` - Upload CSV/Excel file
- `GET /files` - List all uploaded files
- `GET /data/preview?filename={name}` - Preview file data

### Chat
- `POST /chat` - Send message to chatbot (includes role parameter)
- `GET /history/{role}` - Get chat history for role
- `DELETE /history/{role}` - Delete chat history

### Users
- `GET /users` - Get list of users

## Configuration

### NVIDIA API Models

The application uses `openai/gpt-oss-120b` by default. This is configured in `backend/main.py`:

```python
MODEL_NAME = "openai/gpt-oss-120b"
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)
```

### Database

To change database settings, update the `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

## Dataset Information

The application currently uses `student-mat.csv` dataset with 395 students and the following columns:

**Demographics:** school, sex, age, address, famsize, Pstatus  
**Parents:** Medu, Fedu, Mjob, Fjob  
**Academic:** studytime, failures, schoolsup, famsup, paid, activities, higher  
**Social:** guardian, traveltime, romantic, famrel, freetime, goout  
**Health:** Dalc, Walc, health, absences  
**Grades:** G1, G2, G3 (final grade)

## Troubleshooting

### Port Already in Use

If ports 8000 or 5173 are in use:

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Or use the pkill command
pkill -9 -f "python.*main.py"
pkill -9 -f vite
```

### Database Connection Error

1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check if the database exists:
   ```bash
   psql -U postgres -l
   ```

3. Verify password encoding in `.env` (special characters must be URL-encoded)

### API Issues

**Empty Response Error:**
- The system automatically handles empty responses with a helpful fallback message

**Rate Limiting:**
- NVIDIA API has rate limits depending on your plan
- The system will show appropriate error messages

### Charts Not Displaying

1. Check browser console (F12) for errors
2. Verify backend is serving static files: http://localhost:8000/static/charts/
3. Check backend logs for chart generation errors
4. Try clearing chat history and asking again

**Common Causes:**
- Column names with typos (e.g., "study_time" vs "studytime")
- Using wrong dataset reference
- Network issues loading images

## Advanced Features

### Intelligent Fallback System

The system includes an intelligent fallback mechanism that:
- Detects when the AI model returns JSON instead of calling tools
- Automatically parses the JSON and calls the appropriate functions
- Handles multiple parameter name variations (`file`, `filename`, `file_name`, `file_path`)
- Generates appropriate response text with the chart

### Supported Tool Functions

**`create_visualization`**
- Creates various chart types
- Supports filtering, grouping, and aggregation
- Parameters: `chart_type`, `x_column`, `y_column`, `title`, `filename`, `aggregation`, `group_by`, `filter_column`, `filter_value`

**`get_data_summary`**
- Returns summary of loaded datasets
- Shows column names and sample data

## Development

### Adding New Chart Types

Edit `backend/tools.py` and add your chart type to the `create_visualization` function:

```python
elif chart_type == 'your_new_type':
    # Your chart generation code
    sns.your_plot(data=plot_data, x=x_column, y=y_column)
```

### Modifying the UI

Frontend components are in `frontend/src/`:
- `pages/ChatInterface.jsx` - Chat interface
- `pages/AdminDashboard.jsx` - Admin dashboard
- `components/Layout.jsx` - Main layout and sidebar

## License

This project is for educational purposes.

## Credits

- Built with React, FastAPI, and NVIDIA AI
- Chart generation using Matplotlib and Seaborn
- UI components with Framer Motion and Lucide React
- Student performance dataset from UCI Machine Learning Repository

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review terminal/backend logs for error messages
3. Ensure all dependencies are installed correctly
4. Verify NVIDIA API key is valid and has quota remaining
