import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import os

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/")
if not API_BASE.endswith("/"):
    API_BASE += "/"

# Custom CSS for Fawry Plus branding and styling
st.markdown("""
<style>
    /* Fawry Plus Brand Colors */
    :root {
        --fawry-yellow: #FFD700;
        --fawry-blue: #0066CC;
        --fawry-maroon: #800020;
        --fawry-light-blue: #E6F2FF;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, var(--fawry-blue) 0%, var(--fawry-maroon) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .page-header {
        background: linear-gradient(135deg, var(--fawry-blue) 0%, var(--fawry-yellow) 100%);
        padding: 0.75rem 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 102, 204, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .page-header h1 {
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        margin: 0;
        font-size: 1.5rem;
    }
    
    .page-header p {
        margin: 0.25rem 0 0 0;
        font-size: 0.85rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--fawry-blue);
    }
    
    .metric-card h3 {
        font-size: 0.9rem;
        color: #666;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        margin: 0;
    }
    
    .filter-section {
        background: white;
        padding: 0.75rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    .stMetric {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid var(--fawry-blue);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    
    .stMetric label {
        font-size: 0.85rem;
        color: #666;
        font-weight: 500;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--fawry-blue);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--fawry-yellow) 0%, #FFE44D 50%, var(--fawry-light-blue) 100%);
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        background: transparent;
    }
    
    .logo-container {
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    
    .logo-container img {
        max-width: 60%;
        height: auto;
        border-radius: 8px;
    }
    
    .brand-name {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--fawry-blue);
        margin-top: 0.5rem;
        text-align: center;
    }
    
    .brand-tagline {
        font-size: 0.9rem;
        color: #666;
        text-align: center;
        margin-top: 0.25rem;
        font-style: italic;
    }
    
    /* Main content area adjustment */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Navigation buttons styling */
    .nav-button-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Fawry Plus Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏦"
)

# Fawry Plus Brand Color Palette
COLORS = {
    'primary': '#0066CC',      # Fawry Blue
    'secondary': '#FFD700',     # Fawry Yellow
    'accent': '#800020',        # Fawry Maroon
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#0066CC',
    'gradient1': ['#0066CC', '#FFD700'],      # Blue to Yellow
    'gradient2': ['#FFD700', '#800020'],      # Yellow to Maroon
    'gradient3': ['#0066CC', '#800020'],      # Blue to Maroon
    'gradient4': ['#E6F2FF', '#FFE44D']       # Light Blue to Light Yellow
}

# ========== EMPLOYEES PAGE (Enhanced) ==========
def employees_page():
    # Fawry Plus branded header
    st.markdown('<div class="page-header"><h1>👥 Employee Analytics Dashboard</h1><p style="opacity: 0.9;">Track attendance, working hours, and employee performance</p></div>', unsafe_allow_html=True)
    
    # Filters at the top (moved from sidebar)
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Filters")
    
    # First row of filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 1. Governorate filter
        selected_governorate = None
        try:
            governorates = requests.get(f"{API_BASE}/employees/governorates").json()
            if governorates:
                governorate_options = ["All"] + sorted(governorates)
                selected_governorate_str = st.selectbox(
                    "📍 Governorate",
                    options=governorate_options,
                    key="emp_governorate"
                )
                selected_governorate = None if selected_governorate_str == "All" else selected_governorate_str
        except:
            governorates = []
            selected_governorate = None
    
    with col2:
        # 2. Branch Name filter (with "All" option)
        branch_id = None
        try:
            params = {}
            if selected_governorate:
                params["governorate"] = selected_governorate
            branch_names_data = requests.get(f"{API_BASE}/employees/branch-names", params=params).json()
            
            if branch_names_data:
                branch_options = ["All"] + [f"{b['Branch Name']} ({b['Branch ID']})" for b in branch_names_data]
                selected_branch_str = st.selectbox(
                    "🏢 Branch Name",
                    options=branch_options,
                    key="emp_branch_name"
                )
                
                if selected_branch_str != "All":
                    # Extract branch ID from selection
                    branch_id = int(selected_branch_str.split("(")[1].split(")")[0])
            else:
                branch_options = ["All"]
                st.selectbox("🏢 Branch Name", options=branch_options, key="emp_branch_name")
        except Exception as e:
            st.error(f"Error fetching branches: {e}")
            branch_id = None
    
    with col3:
        # Graphs Interval filter
        graph_interval = st.selectbox(
            "📊 Graphs Interval",
            options=["All", "Daily", "Weekly", "Monthly"],
            key="emp_graph_interval"
        )
    
    # Second row of filters
    col5, col6 = st.columns(2)
    
    with col5:
        # Get available dates
        try:
            params = {}
            if branch_id:
                params["branch"] = branch_id
            if selected_governorate:
                params["governorate"] = selected_governorate
            dates_str = requests.get(f"{API_BASE}/employees/dates", params=params).json()
            dates = [datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, '%Y-%m-%d').date() for d in dates_str]
            dates = sorted(set(dates))
        except Exception as e:
            st.error(f"Error fetching dates: {e}")
            dates = []
        
        # Date range selection
        if dates:
            start_date = st.date_input(
                "📅 Start Date",
                value=dates[0] if dates else None,
                min_value=min(dates) if dates else None,
                max_value=max(dates) if dates else None,
                key="emp_start_date"
            )
        else:
            start_date = None
            
    with col6:
        if dates:
            end_date = st.date_input(
                "📅 End Date",
                value=dates[-1] if dates else None,
                min_value=start_date if start_date else (min(dates) if dates else None),
                max_value=max(dates) if dates else None,
                key="emp_end_date"
            )
        else:
            end_date = None
        
    # Get employees list based on selected dates
    employees = []
    if start_date and end_date:
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            params = {"start_date": start_str, "end_date": end_str}
            if branch_id:
                params["branch"] = branch_id
            if selected_governorate:
                params["governorate"] = selected_governorate
            data = requests.get(f"{API_BASE}/employees/data", params=params).json()
            if data:
                df_temp = pd.DataFrame(data)
                employees = sorted(df_temp["Employee ID"].dropna().unique().tolist())
        except:
            employees = []
        
    # Employee filter in col4
    with col4:
        if employees:
            employee_options = ["All"] + sorted(employees)
            selected_employee_str = st.selectbox(
            "👤 Employee ID",
                options=employee_options,
            key="emp_employee"
        )
            employee_id = None if selected_employee_str == "All" else selected_employee_str
        else:
            st.selectbox("👤 Employee ID", options=["All"], key="emp_employee")
            employee_id = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content - Line chart for average working time across date interval
    if start_date and end_date:
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            # Get data for the date range
            params = {"start_date": start_str, "end_date": end_str}
            if branch_id:
                params["branch"] = branch_id
            if selected_governorate:
                params["governorate"] = selected_governorate
            if employee_id:  # Only add employee filter if a specific employee is selected
                params["employee"] = employee_id
            
            data = requests.get(
                f"{API_BASE}/employees/data",
                params=params
            ).json()
            
            if data:
                df = pd.DataFrame(data)
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
                
                # Calculate KPI metrics
                # API returns "First time seen" and "Last time seen" (with spaces)
                first_time_col = "First time seen" if "First time seen" in df.columns else "first_time_seen"
                last_time_col = "Last time seen" if "Last time seen" in df.columns else "last_time_seen"
                
                if first_time_col in df.columns and last_time_col in df.columns:
                    # Calculate average arrival and leaving times
                    df[first_time_col] = pd.to_datetime(df[first_time_col])
                    df[last_time_col] = pd.to_datetime(df[last_time_col])
                    # Calculate mean time by converting to seconds since midnight
                    if not df[first_time_col].isna().all():
                        avg_arrival_seconds = (df[first_time_col].dt.hour * 3600 + df[first_time_col].dt.minute * 60 + df[first_time_col].dt.second).mean()
                        avg_arrival_hour = int(avg_arrival_seconds // 3600)
                        avg_arrival_min = int((avg_arrival_seconds % 3600) // 60)
                        # Format as 12-hour time with AM/PM
                        if avg_arrival_hour >= 12:
                            am_pm = "PM"
                            display_hour = avg_arrival_hour - 12 if avg_arrival_hour > 12 else 12
                        else:
                            am_pm = "AM"
                            display_hour = avg_arrival_hour if avg_arrival_hour > 0 else 12
                        avg_arrival = f"{display_hour}:{avg_arrival_min:02d} {am_pm}"
                    else:
                        avg_arrival = "N/A"
                    
                    if not df[last_time_col].isna().all():
                        avg_leaving_seconds = (df[last_time_col].dt.hour * 3600 + df[last_time_col].dt.minute * 60 + df[last_time_col].dt.second).mean()
                        avg_leaving_hour = int(avg_leaving_seconds // 3600)
                        avg_leaving_min = int((avg_leaving_seconds % 3600) // 60)
                        # Format as 12-hour time with AM/PM
                        if avg_leaving_hour >= 12:
                            am_pm = "PM"
                            display_hour = avg_leaving_hour - 12 if avg_leaving_hour > 12 else 12
                        else:
                            am_pm = "AM"
                            display_hour = avg_leaving_hour if avg_leaving_hour > 0 else 12
                        avg_leaving = f"{display_hour}:{avg_leaving_min:02d} {am_pm}"
                    else:
                        avg_leaving = "N/A"
                else:
                    avg_arrival = "N/A"
                    avg_leaving = "N/A"
                
                avg_working_hours = df["Working hours"].mean() if "Working hours" in df.columns else 0
                
                # Display KPI Cards
                # If specific employee is selected, show 4 KPIs (Arrival, Leaving, Working Time, Active Employees)
                # If "All" is selected, show only 2 KPIs (Working Time, Active Employees)
                if employee_id:
                    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                    
                    with kpi_col1:
                        st.metric("Arrival Time", avg_arrival)
                    
                    with kpi_col2:
                        st.metric("Leaving Time", avg_leaving)
                    
                    with kpi_col3:
                        hours = int(avg_working_hours)
                        minutes = int((avg_working_hours - hours) * 60)
                        st.metric("Working Time", f"{hours} hours")
                    
                    with kpi_col4:
                        # Active Counters/Employees - count unique employees in the dataset
                        active_employees = df["Employee ID"].nunique() if "Employee ID" in df.columns else 0
                        st.metric("Active Counters/Employees", active_employees)
                else:
                    # "All" employees selected - don't show arrival/leaving time
                    kpi_col1, kpi_col2 = st.columns(2)
                    
                    with kpi_col1:
                        hours = int(avg_working_hours)
                        minutes = int((avg_working_hours - hours) * 60)
                        st.metric("Working Time", f"{hours} hours")
                    
                    with kpi_col2:
                        # Active Counters/Employees - count unique employees in the dataset
                        active_employees = df["Employee ID"].nunique() if "Employee ID" in df.columns else 0
                        st.metric("Active Counters/Employees", active_employees)
                
                if employee_id:
                    # Show chart for specific employee
                    # Calculate average working hours per date
                    df_daily = df.groupby("Date")["Working hours"].mean().reset_index()
                    df_daily["Date"] = pd.to_datetime(df_daily["Date"])
                    df_daily = df_daily.sort_values("Date")
                    
                    # Line chart: Average working time across date interval
                    st.markdown("### 📈 Average Working Time Over Date Interval")
                    branch_display = f"Branch {branch_id}" if branch_id else "All Branches"
                    fig_line = px.line(
                        df_daily,
                        x="Date",
                        y="Working hours",
                        title=f"Average Working Hours for Employee {employee_id} ({branch_display})",
                        markers=True,
                        color_discrete_sequence=[COLORS['primary']],
                        labels={"Working hours": "Working Hours (hours)", "Date": "Date"}
                    )
                    fig_line.update_traces(
                        line=dict(width=3),
                        marker=dict(size=8)
                    )
                    fig_line.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=500,
                        xaxis_title="Date",
                        yaxis_title="Average Working Hours (hours)",
                        xaxis=dict(tickformat="%Y-%m-%d", dtick=86400000.0)
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    # Show summary when "All" is selected
                    st.markdown("### 📊 All Employees Summary")
                    
                    # Summary metrics (additional to KPI cards)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_employees = df["Employee ID"].nunique()
                        st.metric("Total Employees", total_employees)
                    with col2:
                        hours = int(avg_working_hours)
                        minutes = int((avg_working_hours - hours) * 60)
                        st.metric("Average Working Hours", f"{hours}h {minutes:02d}m")
                    with col3:
                        total_records = len(df)
                        st.metric("Total Records", total_records)
                    
                    # Chart showing average working hours per date for all employees
                    df_daily_all = df.groupby("Date")["Working hours"].mean().reset_index()
                    df_daily_all["Date"] = pd.to_datetime(df_daily_all["Date"])
                    df_daily_all = df_daily_all.sort_values("Date")
                    
                    branch_display = f"Branch {branch_id}" if branch_id else "All Branches"
                    st.markdown("### 📈 Average Working Time Over Date Interval (All Employees)")
                    fig_line = px.line(
                        df_daily_all,
                        x="Date",
                        y="Working hours",
                        title=f"Average Working Hours - All Employees ({branch_display})",
                        markers=True,
                        color_discrete_sequence=[COLORS['primary']],
                        labels={"Working hours": "Average Working Hours (hours)", "Date": "Date"}
                    )
                    fig_line.update_traces(
                        line=dict(width=3),
                        marker=dict(size=8)
                    )
                    fig_line.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=500,
                        xaxis_title="Date",
                        yaxis_title="Average Working Hours (hours)",
                        xaxis=dict(tickformat="%Y-%m-%d", dtick=86400000.0)
                )
                st.plotly_chart(fig_line, use_container_width=True)
                
                # Generate Reports Section
                st.markdown("---")
                st.markdown("### 📥 Generate Reports")
                
                # Report: Attendance report
                try:
                    # Create attendance report with relevant columns
                    df_attendance_report = df.copy()
                    
                    # Select and rename columns for the report
                    report_columns = []
                    if "Employee ID" in df_attendance_report.columns:
                        report_columns.append("Employee ID")
                    if "Branch ID" in df_attendance_report.columns:
                        report_columns.append("Branch ID")
                    if "Branch Name" in df_attendance_report.columns:
                        report_columns.append("Branch Name")
                    if "Date" in df_attendance_report.columns:
                        report_columns.append("Date")
                    if "First time seen" in df_attendance_report.columns:
                        report_columns.append("First time seen")
                    if "Last time seen" in df_attendance_report.columns:
                        report_columns.append("Last time seen")
                    if "Working hours" in df_attendance_report.columns:
                        report_columns.append("Working hours")
                    
                    if report_columns:
                        df_attendance_report = df_attendance_report[report_columns].copy()
                        # Rename columns for better readability
                        column_mapping = {
                            "First time seen": "Arrival Time",
                            "Last time seen": "Leaving Time",
                            "Working hours": "Working Hours (hours)"
                        }
                        df_attendance_report = df_attendance_report.rename(columns=column_mapping)
                        df_attendance_report = df_attendance_report.sort_values(["Date", "Employee ID"] if "Date" in df_attendance_report.columns and "Employee ID" in df_attendance_report.columns else ["Employee ID"] if "Employee ID" in df_attendance_report.columns else [])
                        
                        csv_attendance = df_attendance_report.to_csv(index=False)
                        st.download_button(
                            label="📄 Attendance Report",
                            data=csv_attendance,
                            file_name=f"attendance_report_{start_date}_to_{end_date}.csv",
                            mime="text/csv",
                            key="employee_attendance_report"
                        )
                    else:
                        # Fallback: use all data
                        csv_attendance = df.to_csv(index=False)
                        st.download_button(
                            label="📄 Attendance Report",
                            data=csv_attendance,
                            file_name=f"attendance_report_{start_date}_to_{end_date}.csv",
                            mime="text/csv",
                            key="employee_attendance_report"
                        )
                except Exception as e:
                    st.download_button(
                        label="📄 Attendance Report",
                        data="",
                        file_name="attendance_report.csv",
                        mime="text/csv",
                        key="employee_attendance_report",
                        disabled=True
                    )
                
                # Show data table
                st.markdown("### 📋 Employee Data")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No data available for the selected filters.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    else:
        st.info("Please select date range to view the data.")

# ========== SHUTTER STATE PAGE (Enhanced) ==========
def shutter_state_page():
    st.markdown('<div class="page-header"><h1>🚪 Shutter State Dashboard</h1><p style="opacity: 0.9;">Monitor branch opening and closing times</p></div>', unsafe_allow_html=True)
    
    # Filters at the top (moved from sidebar)
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Filters")
    
    # First row of filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 1. Governorate filter (first)
        selected_governorate = None
        try:
            governorates = requests.get(f"{API_BASE}/shutter/governorates").json()
            if governorates:
                governorate_options = ["All"] + sorted(governorates)
                selected_governorate_str = st.selectbox(
                    "📍 Governorate",
                    options=governorate_options,
                    key="shutter_governorate"
                )
                selected_governorate = None if selected_governorate_str == "All" else selected_governorate_str
        except:
            governorates = []
            selected_governorate = None
    
    with col2:
        # 2. Branch Name filter (with "All" option)
        branch_id = None
        try:
            params = {}
            if selected_governorate:
                params["governorate"] = selected_governorate
            branch_names_data = requests.get(f"{API_BASE}/shutter/branch-names", params=params).json()
            
            if branch_names_data:
                branch_options = ["All"] + [f"{b['Branch Name']} ({b['Branch ID']})" for b in branch_names_data]
                selected_branch_str = st.selectbox(
                    "🏢 Branch Name",
                    options=branch_options,
                    key="shutter_branch_name"
                )
                
                if selected_branch_str != "All":
                    # Extract branch ID from selection
                    branch_id = int(selected_branch_str.split("(")[1].split(")")[0])
            else:
                branch_options = ["All"]
                st.selectbox("🏢 Branch Name", options=branch_options, key="shutter_branch_name")
        except Exception as e:
            st.error(f"Error fetching branches: {e}")
            branch_id = None
    
    with col3:
        # View mode selection
        view_mode = st.radio(
            "📊 View Mode",
            ["Single Date Timeline", "Date Interval Analysis"],
            key="shutter_view_mode",
            horizontal=True
        )
    
    # Second row of filters
    col4, col5, col6 = st.columns(3)
    
    # Get available dates
    try:
        params = {}
        if branch_id:
            params["branch"] = branch_id
        if selected_governorate:
            params["governorate"] = selected_governorate
        dates_str = requests.get(f"{API_BASE}/shutter/dates", params=params).json()
        dates = [datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, '%Y-%m-%d').date() for d in dates_str]
        dates = sorted(set(dates))
    except Exception as e:
        st.error(f"Error fetching dates: {e}")
        dates = []
    
    if view_mode == "Single Date Timeline":
        with col4:
            # Single date selection
            selected_date = st.date_input(
                "📅 Date",
                value=dates[-1] if dates else None,
                min_value=min(dates) if dates else None,
                max_value=max(dates) if dates else None,
                key="shutter_date"
            )
            
        with col5:
            # 4. Shutter State filter - Always show "All, open, closed"
            shutter_state = None
            if selected_date:
                # Always show these options
                state_options = ["All", "open", "closed"]
                selected_state_str = st.selectbox(
                    "🚪 Shutter State",
                    options=state_options,
                    key="shutter_state"
                )
                shutter_state = None if selected_state_str == "All" else selected_state_str
            else:
                st.selectbox("🚪 Shutter State", options=["All", "open", "closed"], key="shutter_state")
                shutter_state = None
        
        start_date = None
        end_date = None
    else:
        with col4:
            # Date range selection
            if dates:
                start_date = st.date_input(
                    "📅 Start Date",
                    value=dates[0] if dates else None,
                    min_value=min(dates) if dates else None,
                    max_value=max(dates) if dates else None,
                    key="shutter_start_date"
                )
            else:
                start_date = None
                
        with col5:
            if dates:
                end_date = st.date_input(
                    "📅 End Date",
                    value=dates[-1] if dates else None,
                    min_value=start_date if start_date else (min(dates) if dates else None),
                    max_value=max(dates) if dates else None,
                    key="shutter_end_date"
                )
            else:
                end_date = None
        
            selected_date = None
            shutter_state = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    if view_mode == "Single Date Timeline":
        # Single date timeline view
        if selected_date:
            try:
                date_str = selected_date.isoformat()
                params = {"date": date_str}
                if branch_id:
                    params["branch"] = branch_id
                # Only filter by event if it's not "closed" (closed is handled separately)
                if shutter_state and shutter_state.lower() != "closed":
                    params["event"] = shutter_state
                if selected_governorate:
                    params["governorate"] = selected_governorate
                
                data = requests.get(f"{API_BASE}/shutter/data", params=params).json()
                
                if data:
                    df_filtered = pd.DataFrame(data)
                    
                    # Calculate KPI metrics
                    total_events = len(df_filtered)
                    unique_branches = df_filtered["Branch ID"].nunique() if "Branch ID" in df_filtered.columns else 0
                    
                    # Get latest shutter state
                    if "event" in df_filtered.columns and "time stamp" in df_filtered.columns:
                        df_sorted = df_filtered.sort_values("time stamp", ascending=False)
                        latest_state = df_sorted.iloc[0]["event"] if len(df_sorted) > 0 else "N/A"
                    else:
                        latest_state = "N/A"
                    
                    # Display KPI Cards
                    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
                    
                    with kpi_col1:
                        st.metric("Shutter State", latest_state)
                    
                    with kpi_col2:
                        st.metric("Total Events", total_events)
                    
                    with kpi_col3:
                        st.metric("Branches", unique_branches)
                    
                    # If "closed" is selected, show list of closed branches instead of chart
                    if shutter_state and shutter_state.lower() == "closed":
                        try:
                            params_closed = {"date": selected_date.isoformat()}
                            if selected_governorate:
                                params_closed["governorate"] = selected_governorate
                            
                            closed_branches = requests.get(f"{API_BASE}/shutter/closed-branches", params=params_closed).json()
                            
                            if closed_branches:
                                st.markdown("### 🚫 Closed Branches")
                                st.markdown("Branches that did not have an 'open' event on the selected date:")
                                df_closed = pd.DataFrame(closed_branches)
                                st.dataframe(
                                    df_closed,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Branch ID": st.column_config.NumberColumn("Branch ID", format="%d"),
                                        "Branch Name": st.column_config.TextColumn("Branch Name")
                                    }
                                )
                            else:
                                st.info("No closed branches found for the selected date. All branches had an 'open' event.")
                        except Exception as e:
                            st.warning(f"Could not fetch closed branches: {e}")
                    else:
                        # Shutter state chart: states on x-axis, time on y-axis, different colors per branch
                        st.markdown("### 📊 Shutter States by Time")
                        if "time stamp" in df_filtered.columns and "Branch ID" in df_filtered.columns:
                            df_timeline = df_filtered.copy()
                            df_timeline = df_timeline.sort_values('time stamp')
                            
                            # Get unique branches for color mapping
                            branches = sorted(df_timeline["Branch ID"].unique())
                            branch_colors = [COLORS['primary'], COLORS['secondary'], COLORS['info'], COLORS['warning'], COLORS['danger'], COLORS['success']]
                            
                            # State names
                            state_names = ['Opened', 'Partially Closed', 'Closed']
                            
                            # If multiple branches, use grouped bar chart approach
                            if len(branches) > 1:
                                # Create a grouped bar chart where each branch has its own column per state
                                # Prepare data structure: state -> branch -> list of times
                                state_branch_data = {}
                                
                                for state_name in state_names:
                                    state_branch_data[state_name] = {}
                                    for branch in branches:
                                        state_branch_data[state_name][branch] = []
                                
                                # Process all events
                                for _, row in df_timeline.iterrows():
                                    branch = row['Branch ID']
                                    event = row['event']
                                    time_stamp = row['time stamp']
                                    
                                    # Normalize event name
                                    event_normalized = event.lower()
                                    if 'open' in event_normalized:
                                        state_name = 'Opened'
                                    elif 'partial' in event_normalized:
                                        state_name = 'Partially Closed'
                                    elif 'close' in event_normalized:
                                        state_name = 'Closed'
                                    else:
                                        continue
                                    
                                    # Convert time to minutes
                                    try:
                                        time_obj = pd.to_datetime(time_stamp, format='%H:%M:%S')
                                        minutes = time_obj.hour * 60 + time_obj.minute
                                        state_branch_data[state_name][branch].append((minutes, time_stamp))
                                    except:
                                        continue
                                
                                # Create DataFrame for grouped bar chart
                                chart_data = []
                                for state_name in state_names:
                                    for branch in branches:
                                        times_data = state_branch_data[state_name][branch]
                                        if times_data:
                                            # If multiple events, create separate rows
                                            for minutes, time_label in times_data:
                                                chart_data.append({
                                                    'State': state_name,
                                                    'Branch': f'Branch {branch}',
                                                    'Time': minutes,
                                                    'TimeLabel': time_label,
                                                    'BranchID': branch
                                                })
                                
                                if chart_data:
                                    df_chart = pd.DataFrame(chart_data)
                                    
                                    # Create grouped bar chart using plotly express
                                    fig_timeline = px.bar(
                                        df_chart,
                                        x='State',
                                        y='Time',
                                        color='Branch',
                                        barmode='group',
                                        color_discrete_map={f'Branch {b}': branch_colors[i % len(branch_colors)] 
                                                           for i, b in enumerate(branches)},
                                        text='TimeLabel',
                                        title=f"Shutter States by Time - {selected_date}",
                                        labels={'Time': 'Time (minutes from midnight)', 'State': 'State'}
                                    )
                                    
                                    # Customize layout
                                    fig_timeline.update_traces(
                                        textposition='outside',
                                        textfont=dict(size=9),
                                        width=0.3  # Bar width
                                    )
                                    
                                    fig_timeline.update_layout(
                                        yaxis=dict(
                                            tickmode='array',
                                            tickvals=list(range(0, 1440, 60)),
                                            ticktext=[f"{h:02d}:00" for h in range(24)],
                                            title="Time (HH:MM)"
                                        ),
                                        plot_bgcolor='white',
                                        paper_bgcolor='white',
                                        height=600,
                                        showlegend=True,
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                        xaxis=dict(title="State")
                                    )
                                    
                                    # Update hover template
                                    for trace in fig_timeline.data:
                                        branch_id = trace.name.replace('Branch ', '')
                                        trace.hovertemplate = f'<b>{trace.name}</b><br>State: %{{x}}<br>Time: %{{text}}<extra></extra>'
                                    
                                    st.plotly_chart(fig_timeline, use_container_width=True)
                                else:
                                    # No data to display
                                    fig_timeline = go.Figure()
                                    fig_timeline.add_annotation(
                                        text="No shutter events found for the selected filters",
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False
                                    )
                                    fig_timeline.update_layout(
                                        title=f"Shutter States by Time - {selected_date}",
                                        height=600
                                    )
                                    
                                    st.plotly_chart(fig_timeline, use_container_width=True)
                            else:
                                # Single branch: use simpler visualization
                                branch = branches[0]
                                branch_color = branch_colors[0]
                                fig_timeline = go.Figure()
                                
                                state_positions = {'Opened': 0, 'Partially Closed': 1, 'Closed': 2}
                                
                                for _, row in df_timeline.iterrows():
                                    event = row['event']
                                    time_stamp = row['time stamp']
                                    
                                    # Normalize event name
                                    event_normalized = event.lower()
                                    if 'open' in event_normalized:
                                        state_name = 'Opened'
                                    elif 'partial' in event_normalized:
                                        state_name = 'Partially Closed'
                                    elif 'close' in event_normalized:
                                        state_name = 'Closed'
                                    else:
                                        state_name = event.title()
                                    
                                    try:
                                        time_obj = pd.to_datetime(time_stamp, format='%H:%M:%S')
                                        minutes = time_obj.hour * 60 + time_obj.minute
                                        
                                        fig_timeline.add_trace(go.Scatter(
                                            x=[state_positions.get(state_name, 0)],
                                            y=[minutes],
                                            mode='markers+text',
                                            name=state_name,
                                            marker=dict(size=15, color=branch_color, symbol='circle', line=dict(width=2, color='white')),
                                            text=[time_stamp],
                                            textposition='middle right',
                                            textfont=dict(size=10, color=branch_color),
                                            hovertemplate=f'<b>Branch {branch}</b><br>State: {state_name}<br>Time: {time_stamp}<extra></extra>'
                                        ))
                                    except:
                                        continue
                                
                                fig_timeline.update_layout(
                                    title=f"Shutter States by Time - Branch {branch} on {selected_date}",
                                    xaxis=dict(
                                        tickmode='array',
                                        tickvals=[0, 1, 2],
                                        ticktext=['Opened', 'Partially Closed', 'Closed'],
                                        title="State"
                                    ),
                                    yaxis=dict(
                                        tickmode='array',
                                        tickvals=list(range(0, 1440, 60)),
                                        ticktext=[f"{h:02d}:00" for h in range(24)],
                                        title="Time (HH:MM)"
                                    ),
                                    plot_bgcolor='white',
                                    paper_bgcolor='white',
                                    height=600,
                                    showlegend=True
                                )
                                
                                st.plotly_chart(fig_timeline, use_container_width=True)
                        elif "time stamp" in df_filtered.columns:
                            # Fallback if no Branch ID
                            st.warning("Branch ID not available in data")
                    
                        # Generate Reports Section
                        st.markdown("---")
                        st.markdown("### 📥 Generate Reports")
                        
                        col_report1, col_report2, col_report3 = st.columns(3)
                        
                        with col_report1:
                            # Report 1: Closed branches for specific date
                            try:
                                params_closed = {"date": selected_date.isoformat()}
                                if selected_governorate:
                                    params_closed["governorate"] = selected_governorate
                                closed_branches_data = requests.get(f"{API_BASE}/shutter/closed-branches", params=params_closed).json()
                                if closed_branches_data:
                                    df_closed_report = pd.DataFrame(closed_branches_data)
                                    csv_closed = df_closed_report.to_csv(index=False)
                                    st.download_button(
                                        label="📄 Closed Branches Report",
                                        data=csv_closed,
                                        file_name=f"closed_branches_{selected_date}.csv",
                                        mime="text/csv",
                                        key="shutter_closed_report"
                                    )
                                else:
                                    st.download_button(
                                        label="📄 Closed Branches Report",
                                        data="Branch ID,Branch Name\n",
                                        file_name=f"closed_branches_{selected_date}.csv",
                                        mime="text/csv",
                                        key="shutter_closed_report",
                                        disabled=True
                                    )
                            except:
                                st.download_button(
                                    label="📄 Closed Branches Report",
                                    data="",
                                    file_name="closed_branches.csv",
                                    mime="text/csv",
                                    key="shutter_closed_report",
                                    disabled=True
                                )
                        
                        with col_report2:
                            # Report 2: Opened branches with opening time
                            try:
                                params_open = {"date": selected_date.isoformat(), "event": "open"}
                                if branch_id:
                                    params_open["branch"] = branch_id
                                if selected_governorate:
                                    params_open["governorate"] = selected_governorate
                                open_data = requests.get(f"{API_BASE}/shutter/data", params=params_open).json()
                                if open_data:
                                    df_open_report = pd.DataFrame(open_data)
                                    # Select relevant columns
                                    if "Branch ID" in df_open_report.columns and "time stamp" in df_open_report.columns:
                                        df_open_report = df_open_report[["Branch ID", "time stamp", "event"]].copy()
                                        df_open_report.columns = ["Branch ID", "Opening Time", "Event"]
                                        csv_open = df_open_report.to_csv(index=False)
                                        st.download_button(
                                            label="📄 Opened Branches Report",
                                            data=csv_open,
                                            file_name=f"opened_branches_{selected_date}.csv",
                                            mime="text/csv",
                                            key="shutter_opened_report"
                                        )
                                    else:
                                        st.download_button(
                                            label="📄 Opened Branches Report",
                                            data="Branch ID,Opening Time,Event\n",
                                            file_name=f"opened_branches_{selected_date}.csv",
                                            mime="text/csv",
                                            key="shutter_opened_report",
                                            disabled=True
                                        )
                                else:
                                    st.download_button(
                                        label="📄 Opened Branches Report",
                                        data="Branch ID,Opening Time,Event\n",
                                        file_name=f"opened_branches_{selected_date}.csv",
                                        mime="text/csv",
                                        key="shutter_opened_report",
                                        disabled=True
                                    )
                            except:
                                st.download_button(
                                    label="📄 Opened Branches Report",
                                    data="",
                                    file_name="opened_branches.csv",
                                    mime="text/csv",
                                    key="shutter_opened_report",
                                    disabled=True
                                )
                        
                        with col_report3:
                            # Report 3: Shutter states for single date
                            try:
                                if not (shutter_state and shutter_state.lower() == "closed"):
                                    # Get all shutter states for the selected date
                                    params_states = {"date": selected_date.isoformat()}
                                    if branch_id:
                                        params_states["branch"] = branch_id
                                    if selected_governorate:
                                        params_states["governorate"] = selected_governorate
                                    states_data = requests.get(f"{API_BASE}/shutter/data", params=params_states).json()
                                    if states_data:
                                        df_states_report = pd.DataFrame(states_data)
                                        csv_states = df_states_report.to_csv(index=False)
                                        st.download_button(
                                            label="📄 Shutter States Report",
                                            data=csv_states,
                                            file_name=f"shutter_states_{selected_date}.csv",
                                            mime="text/csv",
                                            key="shutter_states_report"
                                        )
                                    else:
                                        st.download_button(
                                            label="📄 Shutter States Report",
                                            data="",
                                            file_name="shutter_states.csv",
                                            mime="text/csv",
                                            key="shutter_states_report",
                                            disabled=True
                                        )
                                else:
                                    st.download_button(
                                        label="📄 Shutter States Report",
                                        data="",
                                        file_name="shutter_states.csv",
                                        mime="text/csv",
                                        key="shutter_states_report",
                                        disabled=True
                                    )
                            except:
                                st.download_button(
                                    label="📄 Shutter States Report",
                                    data="",
                                    file_name="shutter_states.csv",
                                    mime="text/csv",
                                    key="shutter_states_report",
                                    disabled=True
                                )
                        
                        # Show data table (only if not showing closed branches)
                        if not (shutter_state and shutter_state.lower() == "closed"):
                            st.markdown("### 📋 Event Details")
                            st.dataframe(df_filtered, use_container_width=True)
                else:
                    st.warning("No data for this combination of branch and date.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
        else:
            st.info("Please select a date")
    
    else:
        # Date interval analysis - removed graph of shutter state time as requested
        if start_date and end_date:
            try:
                start_str = start_date.isoformat()
                end_str = end_date.isoformat()
                
                params = {"start_date": start_str, "end_date": end_str}
                if branch_id:
                    params["branch"] = branch_id
                if selected_governorate:
                    params["governorate"] = selected_governorate
                
                data = requests.get(
                    f"{API_BASE}/shutter/data",
                    params=params
                ).json()
                
                if data:
                    df = pd.DataFrame(data)
                    df["Date"] = pd.to_datetime(df["Date"]).dt.date
                    
                    # Calculate KPI metrics
                    total_events = len(df)
                    unique_branches = df["Branch ID"].nunique() if "Branch ID" in df.columns else 0
                    unique_dates = df["Date"].nunique() if "Date" in df.columns else 0
                    
                    # Display KPI Cards
                    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
                    
                    with kpi_col1:
                        st.metric("Total Events", total_events)
                    
                    with kpi_col2:
                        st.metric("Branches", unique_branches)
                    
                    with kpi_col3:
                        st.metric("Days", unique_dates)
                    
                    # Generate Reports Section for Date Interval
                    st.markdown("---")
                    st.markdown("### 📥 Generate Reports")
                    
                    col_report1, col_report2, col_report3 = st.columns(3)
                    
                    with col_report1:
                        # Report 1: Closed branches for date range
                        try:
                            # Get closed branches for each date in range
                            closed_branches_all = []
                            current_date = start_date
                            while current_date <= end_date:
                                params_closed = {"date": current_date.isoformat()}
                                if selected_governorate:
                                    params_closed["governorate"] = selected_governorate
                                closed_data = requests.get(f"{API_BASE}/shutter/closed-branches", params=params_closed).json()
                                for branch in closed_data:
                                    branch["Date"] = current_date.isoformat()
                                    closed_branches_all.append(branch)
                                current_date += pd.Timedelta(days=1)
                            
                            if closed_branches_all:
                                df_closed_report = pd.DataFrame(closed_branches_all)
                                csv_closed = df_closed_report.to_csv(index=False)
                                st.download_button(
                                    label="📄 Closed Branches Report",
                                    data=csv_closed,
                                    file_name=f"closed_branches_{start_date}_to_{end_date}.csv",
                                    mime="text/csv",
                                    key="shutter_closed_report_interval"
                                )
                            else:
                                st.download_button(
                                    label="📄 Closed Branches Report",
                                    data="Branch ID,Branch Name,Date\n",
                                    file_name=f"closed_branches_{start_date}_to_{end_date}.csv",
                                    mime="text/csv",
                                    key="shutter_closed_report_interval",
                                    disabled=True
                                )
                        except Exception as e:
                            st.download_button(
                                label="📄 Closed Branches Report",
                                data="",
                                file_name="closed_branches.csv",
                                mime="text/csv",
                                key="shutter_closed_report_interval",
                                disabled=True
                            )
                    
                    with col_report2:
                        # Report 2: Opened branches with opening time for date range
                        try:
                            params_open = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "event": "open"}
                            if branch_id:
                                params_open["branch"] = branch_id
                            if selected_governorate:
                                params_open["governorate"] = selected_governorate
                            open_data = requests.get(f"{API_BASE}/shutter/data", params=params_open).json()
                            if open_data:
                                df_open_report = pd.DataFrame(open_data)
                                # Select relevant columns
                                if "Branch ID" in df_open_report.columns and "time stamp" in df_open_report.columns:
                                    df_open_report = df_open_report[["Branch ID", "Date", "time stamp", "event"]].copy()
                                    df_open_report.columns = ["Branch ID", "Date", "Opening Time", "Event"]
                                    csv_open = df_open_report.to_csv(index=False)
                                    st.download_button(
                                        label="📄 Opened Branches Report",
                                        data=csv_open,
                                        file_name=f"opened_branches_{start_date}_to_{end_date}.csv",
                                        mime="text/csv",
                                        key="shutter_opened_report_interval"
                                    )
                                else:
                                    st.download_button(
                                        label="📄 Opened Branches Report",
                                        data="Branch ID,Date,Opening Time,Event\n",
                                        file_name=f"opened_branches_{start_date}_to_{end_date}.csv",
                                        mime="text/csv",
                                        key="shutter_opened_report_interval",
                                        disabled=True
                                    )
                            else:
                                st.download_button(
                                    label="📄 Opened Branches Report",
                                    data="Branch ID,Date,Opening Time,Event\n",
                                    file_name=f"opened_branches_{start_date}_to_{end_date}.csv",
                                    mime="text/csv",
                                    key="shutter_opened_report_interval",
                                    disabled=True
                                )
                        except:
                            st.download_button(
                                label="📄 Opened Branches Report",
                                data="",
                                file_name="opened_branches.csv",
                                mime="text/csv",
                                key="shutter_opened_report_interval",
                                disabled=True
                            )
                    
                    with col_report3:
                        # Report 3: Shutter states along days
                        try:
                            csv_states = df.to_csv(index=False)
                            st.download_button(
                                label="📄 Shutter States Report",
                                data=csv_states,
                                file_name=f"shutter_states_{start_date}_to_{end_date}.csv",
                                mime="text/csv",
                                key="shutter_states_report_interval"
                            )
                        except:
                            st.download_button(
                                label="📄 Shutter States Report",
                                data="",
                                file_name="shutter_states.csv",
                                mime="text/csv",
                                key="shutter_states_report_interval",
                                disabled=True
                            )
                    
                    # Show data table only (graph removed as requested)
                    st.markdown("### 📋 Shutter State Data")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No data available for the selected date range.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
        else:
            st.info("Please select date range to view the analysis.")

# ========== CUSTOMERS PAGE (Enhanced) ==========
def customers_page():
    st.markdown('<div class="page-header"><h1>🛒 Customer Analytics Dashboard</h1><p style="opacity: 0.9;">Analyze customer flow, waiting times, and service metrics</p></div>', unsafe_allow_html=True)
    
    # Filters at the top (moved from sidebar)
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Filters")
    
    # First row of filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 1. Governorate filter
        selected_governorate = None
        try:
            governorates = requests.get(f"{API_BASE}/customers/governorates").json()
            if governorates:
                governorate_options = ["All"] + sorted(governorates)
                selected_governorate_str = st.selectbox(
                    "📍 Governorate",
                    options=governorate_options,
                    key="cust_governorate"
                )
                selected_governorate = None if selected_governorate_str == "All" else selected_governorate_str
        except:
            governorates = []
            selected_governorate = None
    
    with col2:
        # 2. Branch Name filter (with "All" option)
        branch_id = None
        try:
            params = {}
            if selected_governorate:
                params["governorate"] = selected_governorate
            branch_names_data = requests.get(f"{API_BASE}/customers/branch-names", params=params).json()
            
            if branch_names_data:
                branch_options = ["All"] + [f"{b['Branch Name']} ({b['Branch ID']})" for b in branch_names_data]
                selected_branch_str = st.selectbox(
                    "🏢 Branch Name",
                    options=branch_options,
                    key="cust_branch_name"
                )
                
                if selected_branch_str != "All":
                    # Extract branch ID from selection
                    branch_id = int(selected_branch_str.split("(")[1].split(")")[0])
            else:
                branch_options = ["All"]
                st.selectbox("🏢 Branch Name", options=branch_options, key="cust_branch_name")
        except Exception as e:
            st.error(f"Error fetching branches: {e}")
            branch_id = None
    
    with col3:
        # Graphs Interval filter
        graph_interval = st.selectbox(
            "📊 Graphs Interval",
            options=["All", "Daily", "Weekly", "Monthly"],
            key="cust_graph_interval"
        )
    
    with col4:
        # View mode filter: Hourly or Daily
        view_mode = st.radio(
            "📊 View Mode",
            ["Daily", "Hourly"],
            key="cust_view_mode",
            horizontal=True
        )
    
    # Second row of filters
    col5, col6 = st.columns(2)
    
    with col5:
        # Get dates for selected branch
        try:
            params = {}
            if branch_id:
                params["branch"] = branch_id
            if selected_governorate:
                params["governorate"] = selected_governorate
            dates_str = requests.get(f"{API_BASE}/customers/dates", params=params).json()
            dates = [datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, '%Y-%m-%d').date() for d in dates_str]
            dates = sorted(set(dates))
        except Exception as e:
            st.error(f"Error fetching dates: {e}")
            dates = []
        
        # Date range selection
        if dates:
            start_date = st.date_input(
                "📅 Start Date",
                value=dates[0] if dates else None,
                min_value=min(dates) if dates else None,
                max_value=max(dates) if dates else None,
                key="cust_start_date"
            )
        else:
            start_date = None
            
    with col6:
        if dates:
            end_date = st.date_input(
                "📅 End Date",
                value=dates[-1] if dates else None,
                min_value=start_date if start_date else (min(dates) if dates else None),
                max_value=max(dates) if dates else None,
                key="cust_end_date"
            )
        else:
            end_date = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content - Charts based on date interval
    if start_date and end_date:
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            # Get data for the date range
            params = {"start_date": start_str, "end_date": end_str}
            if branch_id:
                params["branch"] = branch_id
            if selected_governorate:
                params["governorate"] = selected_governorate
            
            data = requests.get(
                f"{API_BASE}/customers/data",
                params=params
            ).json()
            
            if data:
                df = pd.DataFrame(data)
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
                
                # Calculate KPI metrics
                total_customers = df["customer ID"].nunique() if "customer ID" in df.columns else len(df)
                unique_branches = df["Branch ID"].nunique() if "Branch ID" in df.columns else 0
                avg_waiting = df["waiting time"].mean() if "waiting time" in df.columns else 0
                avg_service = df["service time"].mean() if "service time" in df.columns else 0
                
                # Display KPI Cards
                kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                
                with kpi_col1:
                    st.metric("Current Occupancy", f"{total_customers} Customers")
                
                with kpi_col2:
                    st.metric("Active Counters/Employees", unique_branches)
                
                with kpi_col3:
                    if avg_waiting > 0:
                        # Waiting time is already in minutes from DB
                        waiting_min = int(avg_waiting)
                        waiting_sec = int(round((avg_waiting - waiting_min) * 60))
                        if waiting_sec > 0:
                            st.metric("Avg Waiting Time", f"{waiting_min}m {waiting_sec}s")
                        else:
                            st.metric("Avg Waiting Time", f"{waiting_min} minutes")
                    else:
                        st.metric("Avg Waiting Time", "N/A")
                
                with kpi_col4:
                    if avg_service > 0:
                        # Service time is already in minutes from DB
                        service_min = int(avg_service)
                        service_sec = int(round((avg_service - service_min) * 60))
                        if service_sec > 0:
                            st.metric("Avg Service Time", f"{service_min}m {service_sec}s")
                        else:
                            st.metric("Avg Service Time", f"{service_min} minutes")
                    else:
                        st.metric("Avg Service Time", "N/A")
                
                # Chart 1: Number of customers (Daily or Hourly)
                if view_mode == "Hourly":
                    st.markdown("### 📊 Number of Customers Per Hour")
                    
                    # Extract hour from visit start time
                    if "visit start time" in df.columns:
                        df["Hour"] = pd.to_datetime(df["visit start time"]).dt.hour
                        
                        # Count customers per hour across ALL branches and ALL dates
                        # When "All" branches selected, aggregate across all branches
                        # When multiple dates selected, aggregate across all dates
                        # When "All" branches selected, aggregate across all branches
                        # When multiple dates selected, aggregate across all dates
                        if "customer ID" in df.columns:
                            # Count total number of customer visits per hour (not unique, to aggregate across dates)
                            # This counts each visit, so if same customer visits multiple days, they're counted multiple times
                            df_hourly_customers = df.groupby("Hour").size().reset_index(name="customer ID")
                        else:
                            # Fallback: count rows per hour
                            df_hourly_customers = df.groupby("Hour").size().reset_index(name="customer ID")
                        
                        df_hourly_customers = df_hourly_customers.sort_values("Hour")
                        
                        # Ensure all hours 0-23 are represented (fill missing hours with 0)
                        all_hours = pd.DataFrame({"Hour": range(24)})
                        df_hourly_customers = all_hours.merge(df_hourly_customers, on="Hour", how="left").fillna(0)
                        df_hourly_customers["customer ID"] = df_hourly_customers["customer ID"].astype(int)
                        df_hourly_customers = df_hourly_customers.sort_values("Hour")
                        
                        branch_display = f"Branch {branch_id}" if branch_id else "All Branches"
                        date_display = f"{start_date} to {end_date}" if start_date != end_date else str(start_date)
                        fig_bar = px.bar(
                            df_hourly_customers,
                            x="Hour",
                            y="customer ID",
                            title=f"Number of Customers per Hour ({branch_display}) - {date_display}",
                            color="customer ID",
                            color_continuous_scale=COLORS['gradient2'],
                            labels={"customer ID": "Number of Customers", "Hour": "Hour of Day"}
                        )
                        fig_bar.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            height=400,
                            xaxis=dict(tickmode='linear', dtick=1, title="Hour (0-23)")
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.warning("Visit start time data not available for hourly view")
                else:
                    # Daily view
                    st.markdown("### 📊 Number of Customers Across Days")
                    col_chart, col_summary = st.columns([2, 1])
                    
                    with col_chart:
                        df_daily_customers = df.groupby("Date")["customer ID"].nunique().reset_index() if "customer ID" in df.columns else df.groupby("Date").size().reset_index(name="count")
                        df_daily_customers["Date"] = pd.to_datetime(df_daily_customers["Date"])
                        df_daily_customers = df_daily_customers.sort_values("Date")
                        
                        if "customer ID" in df.columns:
                            customer_col = "customer ID"
                        else:
                            customer_col = "count"
                            df_daily_customers.rename(columns={"count": "customer ID"}, inplace=True)
                        
                        branch_display = f"Branch {branch_id}" if branch_id else "All Branches"
                        fig_bar = px.bar(
                            df_daily_customers,
                            x="Date",
                            y="customer ID",
                            title=f"Number of Customers per Day ({branch_display})",
                            color="customer ID",
                            color_continuous_scale=COLORS['gradient2'],
                            labels={"customer ID": "Number of Customers", "Date": "Date"}
                        )
                        fig_bar.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            height=400,
                            xaxis=dict(tickformat="%Y-%m-%d", dtick=86400000.0)
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                    with col_summary:
                        st.markdown("### 📋 Summary by Branch")
                        # Create summary: number of customers per branch for each date
                        if "Branch ID" in df.columns and "customer ID" in df.columns:
                            # Group by Date and Branch ID to count unique customers
                            df_summary = df.groupby(["Date", "Branch ID"])["customer ID"].nunique().reset_index()
                            df_summary.columns = ["Date", "Branch ID", "Number of Customers"]
                            df_summary = df_summary.sort_values(["Date", "Branch ID"])
                            
                            # Pivot table: Date as index, Branch ID as columns
                            df_pivot = df_summary.pivot_table(
                                index="Date",
                                columns="Branch ID",
                                values="Number of Customers",
                                fill_value=0
                            )
                            df_pivot = df_pivot.reset_index()
                            df_pivot["Date"] = pd.to_datetime(df_pivot["Date"]).dt.date
                            
                            # Format column names
                            df_pivot.columns = [f"Branch {col}" if col != "Date" else "Date" for col in df_pivot.columns]
                            
                            # Display the summary table
                            st.dataframe(
                                df_pivot,
                                use_container_width=True,
                                hide_index=True
                            )
                        elif "Branch ID" in df.columns:
                            # If no customer ID column, count rows instead
                            df_summary = df.groupby(["Date", "Branch ID"]).size().reset_index(name="Number of Customers")
                            df_summary = df_summary.sort_values(["Date", "Branch ID"])
                            
                            # Pivot table
                            df_pivot = df_summary.pivot_table(
                                index="Date",
                                columns="Branch ID",
                                values="Number of Customers",
                                fill_value=0
                            )
                            df_pivot = df_pivot.reset_index()
                            df_pivot["Date"] = pd.to_datetime(df_pivot["Date"]).dt.date
                            
                            # Format column names
                            df_pivot.columns = [f"Branch {col}" if col != "Date" else "Date" for col in df_pivot.columns]
                            
                            st.dataframe(
                                df_pivot,
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("Branch information not available in the data")
                
                # Charts 2 & 3: Average waiting time and service time side by side (only in daily mode)
                if view_mode == "Daily":
                    st.markdown("### ⏳ Average Waiting & Service Time Over Date Interval")
                    col1, col2 = st.columns(2)
                
                # Chart 2: Line chart for average waiting time across date interval
                    with col1:
                        if "waiting time" in df.columns:
                            df_daily_wait = df.groupby("Date")["waiting time"].mean().reset_index()
                            df_daily_wait["Date"] = pd.to_datetime(df_daily_wait["Date"])
                            df_daily_wait = df_daily_wait.sort_values("Date")
                            
                            branch_display = f"Branch {branch_id}" if branch_id else "All Branches"
                            fig_wait_line = px.line(
                                df_daily_wait,
                                x="Date",
                                y="waiting time",
                                title=f"Average Waiting Time ({branch_display})",
                                markers=True,
                                color_discrete_sequence=[COLORS['warning']],
                                labels={"waiting time": "Average Waiting Time (minutes)", "Date": "Date"}
                            )
                            fig_wait_line.update_traces(line=dict(width=3), marker=dict(size=8))
                            # Ensure all dates are shown, including the last one
                            min_date = df_daily_wait["Date"].min()
                            max_date = df_daily_wait["Date"].max()
                            fig_wait_line.update_layout(
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                height=400,
                                xaxis=dict(
                                    tickformat="%Y-%m-%d",
                                    tickmode='linear',
                                    dtick="D1",
                                    range=[min_date - pd.Timedelta(hours=12), max_date + pd.Timedelta(hours=12)]
                                )
                            )
                            st.plotly_chart(fig_wait_line, use_container_width=True)
                        else:
                            st.info("Waiting time data not available")
                
                # Chart 3: Line chart for average service time across date interval
                    with col2:
                        if "service time" in df.columns:
                            df_daily_service = df.groupby("Date")["service time"].mean().reset_index()
                            df_daily_service["Date"] = pd.to_datetime(df_daily_service["Date"])
                            df_daily_service = df_daily_service.sort_values("Date")
                            
                            branch_display = f"Branch {branch_id}" if branch_id else "All Branches"
                            fig_service_line = px.line(
                                df_daily_service,
                                x="Date",
                                y="service time",
                                title=f"Average Service Time ({branch_display})",
                                markers=True,
                                color_discrete_sequence=[COLORS['info']],
                                labels={"service time": "Average Service Time (minutes)", "Date": "Date"}
                            )
                            fig_service_line.update_traces(line=dict(width=3), marker=dict(size=8))
                            # Ensure all dates are shown, including the last one
                            min_date = df_daily_service["Date"].min()
                            max_date = df_daily_service["Date"].max()
                            fig_service_line.update_layout(
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                height=400,
                                xaxis=dict(
                                    tickformat="%Y-%m-%d",
                                    tickmode='linear',
                                    dtick="D1",
                                    range=[min_date - pd.Timedelta(hours=12), max_date + pd.Timedelta(hours=12)]
                                )
                            )
                            st.plotly_chart(fig_service_line, use_container_width=True)
                        else:
                            st.info("Service time data not available")
                else:
                    # In hourly mode, skip waiting/service time charts
                    pass
                
                # Generate Reports Section
                st.markdown("---")
                st.markdown("### 📥 Generate Reports")
                
                # Report: Number of customers across multiple days
                try:
                    # Create summary report with number of customers per day
                    if "customer ID" in df.columns and "Date" in df.columns:
                        df_customer_report = df.groupby("Date")["customer ID"].nunique().reset_index()
                        df_customer_report.columns = ["Date", "Number of Customers"]
                        df_customer_report = df_customer_report.sort_values("Date")
                        
                        # Add branch breakdown if available
                        if "Branch ID" in df.columns:
                            df_branch_report = df.groupby(["Date", "Branch ID"])["customer ID"].nunique().reset_index()
                            df_branch_report.columns = ["Date", "Branch ID", "Number of Customers"]
                            df_branch_report = df_branch_report.sort_values(["Date", "Branch ID"])
                            
                            # Merge with branch names if available
                            if "Branch Name" in df.columns:
                                branch_names_map = df[["Branch ID", "Branch Name"]].drop_duplicates().set_index("Branch ID")["Branch Name"].to_dict()
                                df_branch_report["Branch Name"] = df_branch_report["Branch ID"].map(branch_names_map)
                                df_branch_report = df_branch_report[["Date", "Branch ID", "Branch Name", "Number of Customers"]]
                            
                            csv_customers = df_branch_report.to_csv(index=False)
                        else:
                            csv_customers = df_customer_report.to_csv(index=False)
                        
                        st.download_button(
                            label="📄 Number of Customers Report",
                            data=csv_customers,
                            file_name=f"customers_report_{start_date}_to_{end_date}.csv",
                            mime="text/csv",
                            key="customers_report"
                        )
                    else:
                        # Fallback: use all data
                        csv_customers = df.to_csv(index=False)
                        st.download_button(
                            label="📄 Number of Customers Report",
                            data=csv_customers,
                            file_name=f"customers_report_{start_date}_to_{end_date}.csv",
                            mime="text/csv",
                            key="customers_report"
                        )
                except Exception as e:
                    st.download_button(
                        label="📄 Number of Customers Report",
                        data="",
                        file_name="customers_report.csv",
                        mime="text/csv",
                        key="customers_report",
                        disabled=True
                    )
                
                # Data table
                st.markdown("### 📋 Customer Data")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No data available for the selected date range and branch.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    else:
        st.info("Please select date range to view the charts.")

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "👥 Employees"

# Sidebar with Fawry Plus branding
with st.sidebar:
    # Logo and Branding Section (no white box, smaller logo)
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    
    # Try to load logo images if they exist, otherwise show placeholder
    logo_paths = ["fawry_logo.png", "fawry_plus_logo.png", "logo.png", "images/fawry_logo.png"]
    logo_found = False
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                # Make logo smaller (60% width instead of full width)
                st.image(logo_path, width=150)
                logo_found = True
                break
            except:
                continue
    
    if not logo_found:
        # Create a styled placeholder for the logo (smaller)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0066CC 0%, #FFD700 100%); 
                    padding: 1rem; border-radius: 10px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 1.5rem; font-weight: bold;">
                fawry<span style="font-family: 'Brush Script MT', cursive; color: #800020;">Plus</span>
            </h1>
            <p style="color: white; margin-top: 0.5rem; font-size: 0.8rem;">Branch Analytics Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation Section
    st.markdown("### 🧭 Navigation")
    st.markdown("---")
    
    pages = {
        "👥 Employees": employees_page,
        "🚪 Shutter State": shutter_state_page,
        "🛒 Customers": customers_page,
    }
    
    # Navigation buttons in sidebar
    for page_name, page_func in pages.items():
        if st.button(
            page_name,
            use_container_width=True,
            type="primary" if st.session_state.current_page == page_name else "secondary",
            key=f"sidebar_nav_{page_name}"
        ):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.markdown("---")
    
    # Additional Info Section
    st.markdown("### ℹ️ Dashboard Info")
    st.info("""
    **Fawry Plus Analytics**
    
    Monitor branch operations:
    - Employee attendance
    - Shutter states
    - Customer analytics
    """)
    
    st.markdown("---")
    st.caption("🔄 Auto-refreshes | 📊 Real-time data")

# Main content area
# Run the selected page
pages[st.session_state.current_page]()

st.caption("🔄 Auto-refreshes every 10s | 📁 JSON changes appear instantly | 🎨 Enhanced with Charts & Colors")

