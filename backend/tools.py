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

def generate_chart_data(
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
    Generate chart configuration and data for frontend rendering.
    Returns structured JSON instead of creating a PNG image.
    
    Args:
        chart_type: Type of chart - 'bar', 'line', 'scatter', 'pie', 'area'
        x_column: Column for X-axis
        y_column: Column for Y-axis (optional for some charts)
        title: Chart title
        filename: Data file to use (defaults to active file)
        filter_column: Column to filter on (optional)
        filter_value: Value to filter for (optional)
        aggregation: Aggregation function - 'count', 'sum', 'mean', 'median', 'min', 'max' (optional)
        group_by: Column to group by before aggregation (optional)
    
    Returns:
        JSON string with chart configuration and data
    """
    print(f"[TOOL CALLED] generate_chart_data: type={chart_type}, x={x_column}, y={y_column}, filter={filter_column}={filter_value}, agg={aggregation}, group={group_by}")
    
    global dataframes, active_file
    target_file = filename or active_file
    
    if not target_file or target_file not in dataframes:
        return json.dumps({"error": "No data loaded or file not found."})

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
        
        # Normalize chart_type (map old types to frontend-compatible types)
        chart_type_map = {
            'hist': 'bar',
            'count': 'bar',
            'box': 'bar',
            'violin': 'bar',
            'heatmap': 'bar'
        }
        normalized_chart_type = chart_type_map.get(chart_type, chart_type)
        
        # Special handling for pie charts
        if normalized_chart_type == 'pie':
            # Pie charts need aggregated data (categories and values)
            if aggregation == 'count' or not y_column:
                # Count occurrences of x_column
                plot_data = df[x_column].value_counts().reset_index()
                plot_data.columns = [x_column, 'value']
                y_column = 'value'
                print(f"[PIE CHART] Auto-aggregated {x_column} into value counts")
            else:
                # Use provided y_column as values
                # Group by x_column and sum/mean the y_column
                if aggregation:
                    plot_data = df.groupby(x_column)[y_column].agg(aggregation).reset_index()
                    plot_data.columns = [x_column, 'value']
                    y_column = 'value'
                else:
                    # Just select the two columns
                    plot_data = df[[x_column, y_column]].copy()
        
        # Limit data to reasonable size for frontend
        if len(plot_data) > 100:
            plot_data = plot_data.head(100)
            print(f"[WARNING] Data truncated to 100 rows for frontend rendering")
        
        # Convert data to list of dictionaries
        data_records = plot_data.to_dict('records')
        
        # Build chart configuration
        filter_text = f" (filtered: {filter_column}={filter_value})" if filter_column and filter_value else ""
        chart_config = {
            "chart_type": normalized_chart_type,
            "data": data_records,
            "x_key": x_column,
            "y_key": y_column,
            "title": f"{title}{filter_text}",
            "x_label": x_column,
            "y_label": y_column or aggregation
        }
        
        result = json.dumps(chart_config)
        print(f"[TOOL RETURN] Chart config with {len(data_records)} data points")
        return result
        
    except Exception as e:
        error_msg = f"Error generating chart data: {str(e)}"
        print(f"[TOOL ERROR] {error_msg}") 
        import traceback
        traceback.print_exc()
        return json.dumps({"error": error_msg})


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

def generate_dashboard(chart_specs: list):
    """
    Generate multiple charts at once for dashboard display.
    
    Args:
        chart_specs: List of chart specifications, each containing:
            - chart_type: 'bar', 'line', 'scatter', 'pie', 'area'
            - x_column: Column for X-axis
            - y_column: Column for Y-axis (optional)
            - title: Chart title
            - aggregation: 'count', 'sum', 'mean', etc. (optional)
    
    Returns:
        JSON string with array of chart configurations
    """
    print(f"[TOOL CALLED] generate_dashboard: {len(chart_specs)} charts requested")
    
    charts = []
    for spec in chart_specs:
        # Build valid parameters only
        params = {
            'chart_type': spec.get('chart_type', 'bar'),
            'title': spec.get('title', 'Chart')
        }
        
        # Add optional parameters only if they exist
        if 'x_column' in spec and spec['x_column']:
            params['x_column'] = spec['x_column']
        if 'y_column' in spec and spec['y_column']:
            params['y_column'] = spec['y_column']
        if 'aggregation' in spec and spec['aggregation']:
            params['aggregation'] = spec['aggregation']
        if 'filename' in spec and spec['filename']:
            params['filename'] = spec['filename']
        if 'filter_column' in spec and spec['filter_column']:
            params['filter_column'] = spec['filter_column']
        if 'filter_value' in spec and spec['filter_value']:
            params['filter_value'] = spec['filter_value']
        if 'group_by' in spec and spec['group_by']:
            params['group_by'] = spec['group_by']
        
        # Call generate_chart_data with filtered params
        result = generate_chart_data(**params)
        try:
            chart_config = json.loads(result)
            if "error" not in chart_config:
                charts.append(chart_config)
        except Exception as e:
            print(f"[ERROR] Failed to parse chart: {e}")
            pass
    
    return json.dumps({"charts": charts})

# Tool definitions for Gemini
# Tool definitions for Gemini
tools_list = [generate_dashboard, generate_chart_data, create_visualization, get_data_summary, query_knowledge_base]

