# AnalyticBot - AI-Powered Data Visualization Chatbot

A full-stack chatbot application that combines data analysis and visualization capabilities. Upload CSV/Excel files and interact with an AI assistant that automatically generates charts and provides insights using Gemini AI.

## Features

- 🤖 **AI-Powered Analysis**: Powered by Google Gemini 2.5 Flash
- 📊 **Automatic Visualizations**: Generates charts proactively based on your questions
- 📁 **Multiple File Support**: Upload and work with multiple CSV/Excel files simultaneously
- 💾 **Persistent Chat History**: All conversations saved to PostgreSQL database
- 👥 **Dual Role System**: Separate Admin and User interfaces
- 🎨 **Modern UI**: Beautiful, responsive interface with custom scrollbars and animations
- 📈 **Flexible Charts**: Supports bar, line, scatter, histogram, pie, box, violin, heatmap, and area charts
- 🔍 **Advanced Filtering**: Filter and aggregate data before visualization
- 🗑️ **Chat Management**: Delete history and start new conversations

## Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Framer Motion (animations)
- React Markdown (message rendering)
- Axios (API calls)

### Backend
- FastAPI
- Python 3.12
- Google Generative AI (Gemini)
- PostgreSQL
- SQLAlchemy
- Pandas, Matplotlib, Seaborn

## Prerequisites

- Python 3.12 or higher
- Node.js 18 or higher
- PostgreSQL 12 or higher
- Google Gemini API key ([Get one here](https://ai.google.dev/))

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
GEMINI_API_KEY=your_gemini_api_key_here
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
pip install -r backend/requirements.txt
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Option 1: Using the Run Script (Recommended)

```bash
# Make the script executable (first time only)
chmod +x run_app.sh

# Run the application
./run_app.sh
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
2. **Upload Data**: Click to upload CSV or Excel files
3. **View Files**: See all uploaded files in the list
4. **Preview Data**: Click on any file to preview its contents
5. **Manage Users**: View active users

### Chat Interface

1. Navigate to **Chat** from the sidebar
2. **Ask Questions**: Type natural language questions about your data
3. **View Charts**: Charts are automatically generated and displayed
4. **New Chat**: Click "New Chat" to clear history and start fresh

### Example Questions

- "What is the average age of students?"
- "Show me a histogram of student ages"
- "Count students by gender"
- "Show breakdown of students whose mother's job is teacher by sex"
- "Create a scatter plot of age vs final grade"
- "What's the correlation between study time and grades?"

## Project Structure

```
Analytic-bot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── tools.py             # AI tools for chart generation
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ChatInterface.jsx    # Chat UI
│   │   │   └── AdminDashboard.jsx   # Admin UI
│   │   ├── App.jsx          # Main app component
│   │   └── index.css        # Global styles
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── static/
│   └── charts/              # Generated chart images
├── .env                     # Environment variables
├── run_app.sh              # Application launcher
└── README.md               # This file
```

## API Endpoints

### Data Management
- `POST /upload` - Upload CSV/Excel file
- `GET /files` - List all uploaded files
- `GET /data/preview?filename={name}` - Preview file data

### Chat
- `POST /chat` - Send message to chatbot
- `GET /history/{role}` - Get chat history for role
- `DELETE /history/{role}` - Delete chat history

### Users
- `GET /users` - Get list of users

## Configuration

### Gemini API Models

The application uses `gemini-2.5-flash` by default. To change the model, edit `backend/main.py`:

```python
model = genai.GenerativeModel('gemini-2.5-flash', tools=tools_list)
```

Available models:
- `gemini-2.5-flash` (fastest, newest)
- `gemini-2.0-flash-exp` (experimental)
- `gemini-1.5-flash` (stable)

### Database

To change database settings, update the `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

## Troubleshooting

### Port Already in Use

If ports 8000 or 5173 are in use:

```bash
# Kill processes on port 8000
fuser -k 8000/tcp

# Kill processes on port 5173
fuser -k 5173/tcp
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

### Gemini API Quota Exceeded

Free tier limits:
- 20 requests per day per model
- Resets every 24 hours

Solutions:
- Wait for quota reset
- Use a different API key
- Upgrade to paid plan

### Charts Not Displaying

1. Check browser console for errors
2. Verify static files are being served: http://localhost:8000/static/charts/
3. Clear chat history and try again

## Development

### Adding New Chart Types

Edit `backend/tools.py` and add your chart type to the `create_visualization` function:

```python
elif chart_type == 'your_new_type':
    # Your chart generation code
    sns.your_plot(data=plot_data, x=x_column, y=y_column)
```

### Modifying UI

Frontend components are in `frontend/src/pages/`:
- `ChatInterface.jsx` - Chat interface
- `AdminDashboard.jsx` - Admin dashboard

Styles are in `frontend/src/index.css` using Tailwind CSS.

## License

This project is for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review terminal logs for error messages
3. Ensure all dependencies are installed correctly

## Credits

- Built with React, FastAPI, and Google Gemini AI
- Chart generation using Matplotlib and Seaborn
- UI components with Tailwind CSS and Framer Motion
