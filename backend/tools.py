import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import uuid
import pypdf
import re

STATIC_DIR = "static/charts"
os.makedirs(STATIC_DIR, exist_ok=True)

# Global dictionary to hold loaded dataframes
# Key: filename, Value: DataFrame
dataframes = {}
# Global list to hold text chunks for RAG
# Each item: {"text": str, "source": str, "page": int}
knowledge_base = []
active_file = None

def load_data(file_path):
    global dataframes, active_file, knowledge_base
    filename = os.path.basename(file_path)
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            dataframes[filename] = df
            active_file = filename
            return f"Data loaded successfully. File '{filename}' is now active."
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
            dataframes[filename] = df
            active_file = filename
            return f"Data loaded successfully. File '{filename}' is now active."
        elif file_path.endswith('.pdf'):
            return load_pdf(file_path)
        else:
            return "Unsupported file format."
    except Exception as e:
        return f"Error loading data: {str(e)}"

def load_pdf(file_path):
    global knowledge_base
    filename = os.path.basename(file_path)
    try:
        reader = pypdf.PdfReader(file_path)
        text_chunks = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Simple chunking by paragraphs or fixed size
                # Here we just split by double newlines for paragraphs
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if len(para.strip()) > 50:  # Ignore very short chunks
                        knowledge_base.append({
                            "text": para.strip(),
                            "source": filename,
                            "page": i + 1
                        })
        
        return f"PDF loaded successfully. Extracted {len(knowledge_base)} text chunks from '{filename}'."
    except Exception as e:
        return f"Error loading PDF: {str(e)}"

def query_knowledge_base(query: str):
    """
    Search the knowledge base for relevant text chunks based on the query.
    Uses simple keyword matching.
    """
    print(f"[TOOL CALLED] query_knowledge_base: query='{query}'")
    global knowledge_base
    
    if not knowledge_base:
        return "Knowledge base is empty. Please upload a PDF file first."
    
    # Simple keyword scoring
    query_terms = set(re.findall(r'\w+', query.lower()))
    scored_chunks = []
    
    for chunk in knowledge_base:
        chunk_text = chunk['text'].lower()
        score = sum(1 for term in query_terms if term in chunk_text)
        if score > 0:
            scored_chunks.append((score, chunk))
    
    # Sort by score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 5 chunks
    top_chunks = scored_chunks[:5]
    
    if not top_chunks:
        return "No relevant information found in the uploaded documents."
    
    result = "Found relevant information:\n\n"
    for score, chunk in top_chunks:
        result += f"--- From {chunk['source']} (Page {chunk['page']}) ---\n"
        result += f"{chunk['text']}\n\n"
        
    return result

def get_data_summary():
    global dataframes
    if not dataframes:
        return "No data loaded."
    
    summary = "Loaded Files:\n"
    for name, df in dataframes.items():
        summary += f"\n--- File: {name} ---\n"
        summary += f"Columns: {df.columns.tolist()}\n"
        summary += f"Head:\n{df.head().to_string()}\n"
    return summary

def get_data_json(filename: str = None):
    global dataframes, active_file
    target_file = filename or active_file
    
    if target_file and target_file in dataframes:
        df = dataframes[target_file]
        return {
            "filename": target_file,
            "columns": df.columns.tolist(),
            "data": df.head(10).to_dict(orient='records'),
            "total_rows": len(df)
        }
    return None

def create_visualization(
    chart_type: str,
    x_column: str = None,
    y_column: str = None,
    title: str = "Chart",
    filename: str = None,
    filter_column: str = None,
    filter_value: str = None,
    aggregation: str = None,
    group_by: str = None
):
    """
    Flexible chart generation tool that can handle filtering, grouping, and aggregations.
    
    Args:
        chart_type: Type of chart - 'bar', 'line', 'scatter', 'hist', 'pie', 'box', 'violin', 'heatmap', 'area', 'count'
        x_column: Column for X-axis
        y_column: Column for Y-axis (optional for some charts)
        title: Chart title
        filename: Data file to use (defaults to active file)
        filter_column: Column to filter on (optional)
        filter_value: Value to filter for (optional)
        aggregation: Aggregation function - 'count', 'sum', 'mean', 'median', 'min', 'max' (optional)
        group_by: Column to group by before aggregation (optional)
    
    Examples:
        - Count of students by sex: chart_type='bar', x_column='sex', aggregation='count'
        - Students with mother='teacher' by sex: chart_type='bar', x_column='sex', filter_column='Mjob', filter_value='teacher', aggregation='count'
        - Average age by school: chart_type='bar', x_column='school', y_column='age', aggregation='mean'
    """
    print(f"[TOOL CALLED] create_visualization: type={chart_type}, x={x_column}, y={y_column}, filter={filter_column}={filter_value}, agg={aggregation}, group={group_by}")
    
    global dataframes, active_file
    target_file = filename or active_file
    
    if not target_file or target_file not in dataframes:
        return "Error: No data loaded or file not found."

    df = dataframes[target_file].copy()
    
    try:
        # Apply filter if specified
        if filter_column and filter_value:
            df = df[df[filter_column] == filter_value]
            print(f"[FILTER] Filtered {len(df)} rows where {filter_column}={filter_value}")
        
        # Handle aggregations
        if aggregation and group_by:
            if aggregation == 'count':
                plot_data = df.groupby(group_by).size().reset_index(name='count')
                x_column = group_by
                y_column = 'count'
            else:
                plot_data = df.groupby(group_by)[y_column].agg(aggregation).reset_index()
                x_column = group_by
        elif aggregation == 'count' and x_column:
            plot_data = df[x_column].value_counts().reset_index()
            plot_data.columns = [x_column, 'count']
            y_column = 'count'
        else:
            plot_data = df
        
        # Create figure
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="darkgrid")
        
        # Generate chart based on type
        if chart_type == 'bar':
            if y_column:
                sns.barplot(data=plot_data, x=x_column, y=y_column)
            else:
                plot_data[x_column].value_counts().plot(kind='bar')
                
        elif chart_type == 'count':
            # Special case for count plots
            if filter_column and filter_value:
                sns.countplot(data=df, x=x_column)
            else:
                sns.countplot(data=plot_data, x=x_column)
                
        elif chart_type == 'line':
            sns.lineplot(data=plot_data, x=x_column, y=y_column)
            
        elif chart_type == 'scatter':
            sns.scatterplot(data=plot_data, x=x_column, y=y_column)
            
        elif chart_type == 'hist':
            sns.histplot(data=plot_data, x=x_column, bins=20)
            
        elif chart_type == 'box':
            sns.boxplot(data=plot_data, x=x_column, y=y_column)
            
        elif chart_type == 'violin':
            sns.violinplot(data=plot_data, x=x_column, y=y_column)
            
        elif chart_type == 'pie':
            if aggregation == 'count' or not y_column:
                data = plot_data[x_column].value_counts() if x_column in plot_data.columns else plot_data['count']
                plt.pie(data, labels=data.index, autopct='%1.1f%%')
            else:
                plt.pie(plot_data[y_column], labels=plot_data[x_column], autopct='%1.1f%%')
                
        elif chart_type == 'heatmap':
            if not x_column and not y_column:
                sns.heatmap(plot_data.select_dtypes(include=['number']).corr(), annot=True, cmap='coolwarm')
            else:
                pivot_data = plot_data.pivot_table(values=y_column, index=x_column, columns=group_by, aggfunc=aggregation or 'mean')
                sns.heatmap(pivot_data, annot=True, cmap='coolwarm')
                
        elif chart_type == 'area':
            plot_data.plot.area(x=x_column, y=y_column)
        
        # Set title
        filter_text = f" (filtered: {filter_column}={filter_value})" if filter_column and filter_value else ""
        plt.title(f"{title}{filter_text}")
        plt.tight_layout()
        
        # Save chart
        chart_filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(STATIC_DIR, chart_filename)
        plt.savefig(filepath)
        plt.close()
        
        chart_path = f"![Chart](/static/charts/{chart_filename})"
        print(f"[TOOL RETURN] {chart_path}")
        return chart_path
        
    except Exception as e:
        error_msg = f"Error generating chart: {str(e)}"
        print(f"[TOOL ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return error_msg

# Tool definitions for Gemini
# Tool definitions for Gemini
tools_list = [create_visualization, get_data_summary, query_knowledge_base]
