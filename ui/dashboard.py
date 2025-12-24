import streamlit as st
import pandas as pd
import httpx
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Engineering Simulation Platform",
    page_icon="🤖",
    layout="wide"
)

# Helpers
def get_api_status():
    try:
        r = httpx.get(f"{API_URL}/health", timeout=2)
        return r.status_code == 200
    except:
        return False

def get_runs():
    try:
        r = httpx.get(f"{API_URL}/runs")
        if r.status_code == 200:
            return r.json().get("runs", [])
        return []
    except:
        return []

def get_run_details(run_id, endpoint):
    try:
        r = httpx.get(f"{API_URL}/runs/{run_id}/{endpoint}")
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

# Sidebar
st.sidebar.title("🚀 Simulation Platform")
api_up = get_api_status()

if api_up:
    st.sidebar.success("API Connected")
else:
    st.sidebar.error("API Error: Is the backend running?")
    st.info("Run `make api` in terminal.")

# Runs List
runs = get_runs()
if not runs:
    st.sidebar.warning("No runs found.")
    selected_run_id = None
else:
    # Convert to df for display? Or just list
    run_options = {f"{r['run_id']} ({r['status']})": r['run_id'] for r in runs}
    selected_label = st.sidebar.selectbox("Select Run", list(run_options.keys()))
    selected_run_id = run_options[selected_label]

# Main Content
if selected_run_id:
    st.title(f"Run Analysis: {selected_run_id}")
    
    # 1. Fetch Data
    metrics = get_run_details(selected_run_id, "metrics")
    insights = get_run_details(selected_run_id, "insights")
    
    # 2. Metrics View
    if metrics:
        st.subheader("📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        perf = metrics.get("performance_metrics", {})
        
        col1.metric("Max Temp", f"{perf.get('max_temperature', 0):.4f}")
        col2.metric("Mean Temp", f"{perf.get('mean_temperature', 0):.4f}")
        col3.metric("Stability Ratio", f"{perf.get('stability_ratio', 0):.4f}")
        col4.metric("Converged", str(metrics.get("quality_metrics", {}).get("converged", "?")))
        
        with st.expander("Full Metrics JSON"):
            st.json(metrics)
    else:
        st.warning("Metrics/Validation unavailable for this run.")

    # 3. AI Insights View
    st.subheader("🤖 AI Insights")
    if insights:
        # Display Markdown
        st.markdown(insights.get("markdown", "No markdown content."))
        
        with st.expander("Raw AI JSON"):
            st.json(insights.get("json"))
    else:
        st.info("No AI insights generated yet. Run `make insights`.")

else:
    st.markdown("### Welcome to the Engineering Simulation Platform")
    st.markdown("""
    Select a simulation run from the sidebar to view:
    - 📊 Validated Metrics
    - 🔍 Physics Validation Status
    - 🤖 AI-Generated Engineering Insights
    """)
