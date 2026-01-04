from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
from typing import Optional
from datetime import datetime
from pathlib import Path

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Database configuration
DB_FILE = "central_db.db"

# Branch name mapping
BRANCH_NAMES = {
    "1290": "Wadi Elmlouk",
    "1390": "Nahia"
}

# Governorate is always "Giza"
GOVERNORATE = "Giza"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_FILE)

def get_branch_name(branch_id):
    """Get branch name from branch_id"""
    branch_str = str(branch_id)
    return BRANCH_NAMES.get(branch_str, f"Branch {branch_id}")

# Load data from database functions
def load_employee_data():
    """Load employee data from attendance_table"""
    conn = get_db_connection()
    query = """
        SELECT 
            branch_id as "Branch ID",
            employee_id as "Employee ID",
            disk_hours as "Working hours",
            first_time_seen as "First time seen",
            last_time_seen as "Last time seen",
            date as "Date"
        FROM attendance_table
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Add hardcoded fields
    df["Governorate"] = GOVERNORATE
    df["Branch Name"] = df["Branch ID"].apply(get_branch_name)
    
    # Convert date to ISO format string
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%dT00:00:00")
    
    return df

def load_shutter_data():
    """Load shutter data from shutter_table"""
    conn = get_db_connection()
    query = """
        SELECT 
            branch_id as "Branch ID",
            event_type as "event",
            event_time as "time stamp",
            date as "Date"
        FROM shutter_table
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Add hardcoded fields
    df["Governorate"] = GOVERNORATE
    df["Branch Name"] = df["Branch ID"].apply(get_branch_name)
    
    # Convert date to ISO format string if exists
    if "Date" in df.columns and df["Date"].notna().any():
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%dT00:00:00")
    
    # Format time stamp
    if "time stamp" in df.columns:
        df["time stamp"] = pd.to_datetime(df["time stamp"]).dt.strftime("%H:%M:%S")
    
    return df

def load_customer_data():
    """Load customer data from customer_table"""
    conn = get_db_connection()
    query = """
        SELECT 
            branch_id as "Branch ID",
            customer_id as "customer ID",
            service_time as "service time",
            waiting_time as "waiting time",
            first_time_seen as "visit start time",
            last_time_seen as "service end time",
            date as "Date"
        FROM customer_table
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Add hardcoded fields
    df["Governorate"] = GOVERNORATE
    df["Branch Name"] = df["Branch ID"].apply(get_branch_name)
    
    # Convert date to ISO format string
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%dT00:00:00")
    
    # Convert timestamps to ISO format
    if "visit start time" in df.columns:
        df["visit start time"] = pd.to_datetime(df["visit start time"]).dt.strftime("%Y-%m-%dT%H:%M:%S")
    if "service end time" in df.columns:
        df["service end time"] = pd.to_datetime(df["service end time"]).dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    return df

@app.get("/")
async def root():
    return {"message": "Multi-page Dashboard API"}

# ========== EMPLOYEES ENDPOINTS ==========
@app.get("/employees/branches")
def get_employee_branches():
    df = load_employee_data()
    # Convert to int for compatibility with existing code
    branch_ids = df["Branch ID"].dropna().unique().tolist()
    return sorted([int(bid) if isinstance(bid, str) else int(bid) for bid in branch_ids])

@app.get("/employees/branch-names")
def get_employee_branch_names(governorate: Optional[str] = None):
    df = load_employee_data()
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    
    # Get branch names from the data
    branch_data = df[["Branch ID", "Branch Name"]].drop_duplicates()
    result = [{"Branch ID": int(row["Branch ID"]), "Branch Name": row["Branch Name"]} 
             for _, row in branch_data.iterrows()]
    return sorted(result, key=lambda x: x["Branch Name"])

@app.get("/employees/governorates")
def get_employee_governorates():
    # Governorate is always "Giza"
    return [GOVERNORATE]

@app.get("/employees/data")
def get_employee_data(
    branch: Optional[int] = None,
    date: Optional[str] = None,
    employee: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    governorate: Optional[str] = None
):
    df = load_employee_data()
    
    # Parse date from ISO format
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    # Filter
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    if date:
        try:
            # Handle ISO format (2025-12-20T00:00:00) or YYYY-MM-DD
            if 'T' in date:
                target_date = pd.to_datetime(date.split('T')[0]).date()
            else:
                target_date = pd.to_datetime(date).date()
            df = df[df["Date_parsed"] == target_date]
        except:
            pass
    elif start_date and end_date:
        # Date range filter
        try:
            if 'T' in start_date:
                start = pd.to_datetime(start_date.split('T')[0]).date()
            else:
                start = pd.to_datetime(start_date).date()
            if 'T' in end_date:
                end = pd.to_datetime(end_date.split('T')[0]).date()
            else:
                end = pd.to_datetime(end_date).date()
            df = df[(df["Date_parsed"] >= start) & (df["Date_parsed"] <= end)]
        except:
            pass
    if employee:
        df = df[df["Employee ID"] == int(employee)]
    
    # Return original columns - convert Branch ID to int for compatibility
    result = df[["Branch ID", "Date", "Employee ID", "First time seen", "Last time seen", "Working hours"]].copy()
    result["Branch ID"] = result["Branch ID"].astype(int)
    return result.to_dict(orient="records")

@app.get("/employees/dates")
def get_employee_dates(branch: Optional[int] = None, governorate: Optional[str] = None):
    df = load_employee_data()
    
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    
    dates = sorted(df["Date_parsed"].dropna().unique())
    return [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in dates]

@app.get("/employees/employees")
def get_employees(branch: Optional[int] = None, date: Optional[str] = None, governorate: Optional[str] = None):
    df = load_employee_data()
    
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    if date:
        try:
            if 'T' in date:
                target_date = pd.to_datetime(date.split('T')[0]).date()
            else:
                target_date = pd.to_datetime(date).date()
            df = df[df["Date_parsed"] == target_date]
        except:
            pass
    
    return sorted([int(eid) for eid in df["Employee ID"].dropna().unique().tolist()])

# ========== SHUTTER STATE ENDPOINTS ==========
@app.get("/shutter/branches")
def get_shutter_branches():
    df = load_shutter_data()
    branch_ids = df["Branch ID"].dropna().unique().tolist()
    return sorted([int(bid) if isinstance(bid, str) else int(bid) for bid in branch_ids])

@app.get("/shutter/branch-names")
def get_shutter_branch_names(governorate: Optional[str] = None):
    df = load_shutter_data()
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    
    branch_data = df[["Branch ID", "Branch Name"]].drop_duplicates()
    result = [{"Branch ID": int(row["Branch ID"]), "Branch Name": row["Branch Name"]} 
             for _, row in branch_data.iterrows()]
    return sorted(result, key=lambda x: x["Branch Name"])

@app.get("/shutter/governorates")
def get_shutter_governorates():
    # Governorate is always "Giza"
    return [GOVERNORATE]

@app.get("/shutter/data")
def get_shutter_data(
    branch: Optional[int] = None,
    date: Optional[str] = None,
    event: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    governorate: Optional[str] = None
):
    df = load_shutter_data()
    
    # Parse date from ISO format
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    # Filter
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    if date:
        try:
            if 'T' in date:
                target_date = pd.to_datetime(date.split('T')[0]).date()
            else:
                target_date = pd.to_datetime(date).date()
            df = df[df["Date_parsed"] == target_date]
        except:
            pass
    elif start_date and end_date:
        # Date range filter
        try:
            if 'T' in start_date:
                start = pd.to_datetime(start_date.split('T')[0]).date()
            else:
                start = pd.to_datetime(start_date).date()
            if 'T' in end_date:
                end = pd.to_datetime(end_date.split('T')[0]).date()
            else:
                end = pd.to_datetime(end_date).date()
            df = df[(df["Date_parsed"] >= start) & (df["Date_parsed"] <= end)]
        except:
            pass
    if event:
        if "event" in df.columns:
            df = df[df["event"] == event]
    
    # Return all columns
    return df.to_dict(orient="records")

@app.get("/shutter/dates")
def get_shutter_dates(branch: Optional[int] = None, governorate: Optional[str] = None):
    df = load_shutter_data()
    
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    
    dates = sorted(df["Date_parsed"].dropna().unique())
    return [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in dates]

@app.get("/shutter/events")
def get_shutter_events(branch: Optional[int] = None, date: Optional[str] = None, governorate: Optional[str] = None):
    df = load_shutter_data()
    
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    if date:
        try:
            if 'T' in date:
                target_date = pd.to_datetime(date.split('T')[0]).date()
            else:
                target_date = pd.to_datetime(date).date()
            df = df[df["Date_parsed"] == target_date]
        except:
            pass
    
    if "event" in df.columns:
        return sorted(df["event"].dropna().unique().tolist())
    return []

@app.get("/shutter/closed-branches")
def get_closed_branches(date: str, governorate: Optional[str] = None):
    """
    Get branches from branch_table that don't have an 'open' event on the selected date.
    These are considered closed branches.
    """
    conn = get_db_connection()
    
    try:
        # Parse date
        if 'T' in date:
            target_date = pd.to_datetime(date.split('T')[0]).date()
        else:
            target_date = pd.to_datetime(date).date()
        
        # Get all branches from branch_table
        query_branches = "SELECT branch_id, branch_name FROM branch_table"
        if governorate:
            query_branches += f" WHERE governorate = '{governorate}'"
        
        df_branches = pd.read_sql_query(query_branches, conn)
        
        # Get branches that have 'open' event on the selected date
        query_open = """
            SELECT DISTINCT branch_id 
            FROM shutter_table 
            WHERE date = ? AND LOWER(event_type) LIKE '%open%'
        """
        df_open = pd.read_sql_query(query_open, conn, params=(target_date,))
        open_branch_ids = set(df_open["branch_id"].astype(str).tolist())
        
        # Find branches that don't have an open event (closed branches)
        closed_branches = []
        for _, row in df_branches.iterrows():
            branch_id_str = str(row["branch_id"])
            if branch_id_str not in open_branch_ids:
                branch_name = row["branch_name"] if pd.notna(row["branch_name"]) else get_branch_name(row["branch_id"])
                closed_branches.append({
                    "Branch ID": int(row["branch_id"]),
                    "Branch Name": branch_name
                })
        
        conn.close()
        return closed_branches
    except Exception as e:
        conn.close()
        return []

# ========== CUSTOMERS ENDPOINTS ==========
@app.get("/customers/branches")
def get_customer_branches():
    df = load_customer_data()
    branch_ids = df["Branch ID"].dropna().unique().tolist()
    return sorted([int(bid) if isinstance(bid, str) else int(bid) for bid in branch_ids])

@app.get("/customers/branch-names")
def get_customer_branch_names(governorate: Optional[str] = None):
    df = load_customer_data()
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    
    branch_data = df[["Branch ID", "Branch Name"]].drop_duplicates()
    result = [{"Branch ID": int(row["Branch ID"]), "Branch Name": row["Branch Name"]} 
             for _, row in branch_data.iterrows()]
    return sorted(result, key=lambda x: x["Branch Name"])

@app.get("/customers/governorates")
def get_customer_governorates():
    # Governorate is always "Giza"
    return [GOVERNORATE]

@app.get("/customers/data")
def get_customer_data(
    branch: Optional[int] = None,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    governorate: Optional[str] = None
):
    df = load_customer_data()
    
    # Parse date from ISO format
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    # Filter
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    if date:
        try:
            if 'T' in date:
                target_date = pd.to_datetime(date.split('T')[0]).date()
            else:
                target_date = pd.to_datetime(date).date()
            df = df[df["Date_parsed"] == target_date]
        except:
            pass
    elif start_date and end_date:
        # Date range filter
        try:
            if 'T' in start_date:
                start = pd.to_datetime(start_date.split('T')[0]).date()
            else:
                start = pd.to_datetime(start_date).date()
            if 'T' in end_date:
                end = pd.to_datetime(end_date.split('T')[0]).date()
            else:
                end = pd.to_datetime(end_date).date()
            df = df[(df["Date_parsed"] >= start) & (df["Date_parsed"] <= end)]
        except:
            pass
    
    # Return all columns
    return df.to_dict(orient="records")

@app.get("/customers/dates")
def get_customer_dates(branch: Optional[int] = None, governorate: Optional[str] = None):
    df = load_customer_data()
    
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    if governorate and "Governorate" in df.columns:
        df = df[df["Governorate"] == governorate]
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    
    dates = sorted(df["Date_parsed"].dropna().unique())
    return [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in dates]

@app.get("/customers/count")
def get_customer_count(branch: Optional[int] = None, date: Optional[str] = None):
    df = load_customer_data()
    
    if "Date" in df.columns:
        df["Date_parsed"] = pd.to_datetime(df["Date"]).dt.date
    
    if branch:
        # Branch ID in DB is VARCHAR, so compare as string
        df = df[df["Branch ID"].astype(str) == str(branch)]
    if date:
        try:
            if 'T' in date:
                target_date = pd.to_datetime(date.split('T')[0]).date()
            else:
                target_date = pd.to_datetime(date).date()
            df = df[df["Date_parsed"] == target_date]
        except:
            pass
    
    # Count customers
    if "customer ID" in df.columns:
        return {"count": df["customer ID"].nunique()}
    elif "Customer ID" in df.columns:
        return {"count": df["Customer ID"].nunique()}
    else:
        return {"count": len(df)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)

