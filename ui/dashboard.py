import streamlit as st
import pandas as pd
import httpx
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Engineering Simulation Platform",
    layout="wide"
)

# --- SOFT UI DESIGN SYSTEM ---
DESIGN_CSS = """
<style>
    /* 0. GOOGLE FONTS & RESET */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Poppins', sans-serif !important;
        background-color: #f4f7fe; /* Light Cloud Blue/Grey */
        color: #2b3674;
    }
    
    /* 1. SIDEBAR STYLING - Dark Navy */
    section[data-testid="stSidebar"] {
        background-color: #111c44;
    }
    section[data-testid="stSidebar"] div, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p {
        color: #ffffff !important;
    }
    
    /* 2. MAIN LAYOUT */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }
    
    /* 3. CARDS (Soft, Rounded, White) */
    .stCard {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 1.5rem;
        border: none;
        box-shadow: 0 20px 27px 0 rgba(0, 0, 0, 0.05); /* Soft Switch Shadow */
        margin-bottom: 2rem;
    }
    
    /* 4. HERO CARD (Orange/Pink Gradient) */
    .hero-card {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        border-radius: 20px;
        padding: 1.5rem;
        color: white;
        box-shadow: 0 10px 20px 0 rgba(255, 107, 107, 0.3);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .hero-label {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .hero-value {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .hero-sub {
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        width: fit-content;
        margin-top: 1rem;
    }

    /* 5. METRIC CARD (White) */
    .metric-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.5rem;
        border: none;
        box-shadow: 0 20px 27px 0 rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #a3aed0; /* Muted Grey */
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2b3674; /* Dark Navy */
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #05cd99; /* Success Green */
        font-weight: 600;
        margin-top: 0.5rem;
    }

    /* 6. PILLS & STATUS */
    .status-pill {
        padding: 6px 14px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .status-pill.success { background-color: #E6F7FF; color: #00A3FF; }
    .status-pill.warning { background-color: #FFF7E6; color: #FF9F0A; }
    
    /* 7. CONTENT CONTAINER */
    .content-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 27px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    
    /* 8. TYPOGRAPHY OVERRIDES */
    h1 { font-family: 'Poppins', sans-serif !important; font-weight: 700 !important; font-size: 2.2rem !important; color: #2b3674 !important; }
    h3 { font-family: 'Poppins', sans-serif !important; font-weight: 700 !important; font-size: 1.2rem !important; color: #2b3674 !important; margin-top: 2rem; margin-bottom: 1rem; }
    
</style>
"""
st.markdown(DESIGN_CSS, unsafe_allow_html=True)

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

# --- SIDEBAR NAV ---
st.sidebar.markdown("<h2 style='color:white; margin-bottom:2rem;'>⚡ SimPlatform</h2>", unsafe_allow_html=True)
api_up = get_api_status()

if api_up:
    st.sidebar.caption("● System Online")
else:
    st.sidebar.error("System Offline")

# View Mode
view_mode = st.sidebar.radio("Navigation", ["Dashboard", "Comparison"], label_visibility="collapsed")

# Runs List
runs = get_runs()

def render_charts(runs_data):
    """Renders global charts (Trend across runs)."""
    # st.markdown("<h3>Global Benchmarks</h3>", unsafe_allow_html=True) 
    # Moved inside main view for cleaner layout
    if not runs_data:
        return
    df = pd.DataFrame(runs_data)
    df = df[df['status'] == 'completed']
    if df.empty:
        return
    
    chart_data = df[['run_id', 'stability_ratio']].set_index('run_id')
    st.bar_chart(chart_data)

if not runs:
    st.sidebar.warning("No runs found.")
    current_run = None
else:
    run_options = {f"{r['run_id']}": r['run_id'] for r in runs} # Clean labels
    
    if view_mode == "Dashboard":
        selected_label = st.sidebar.selectbox("Select Run", list(run_options.keys()))
        current_run = run_options[selected_label]
        comparison_run = None
    else:
        st.sidebar.markdown("### Comparison")
        baseline_label = st.sidebar.selectbox("Baseline", list(run_options.keys()), index=0)
        candidate_label = st.sidebar.selectbox("Candidate", list(run_options.keys()), index=min(1, len(run_options)-1))
        
        current_run = run_options[baseline_label]
        comparison_run = run_options[candidate_label]

# --- MAIN CONTENT ---

# 1. DASHBOARD VIEW
if view_mode == "Dashboard" and current_run:
    
    # Header & Metadata Context
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"<h1>Analytics Dashboard</h1>", unsafe_allow_html=True)
        
        # Run Metadata Strip (Credibility)
        metrics_data = get_run_details(current_run, "metrics")
        params = metrics_data.get("parameter_set", {}) if metrics_data else {}
        exec_meta = metrics_data.get("execution_metrics", {}) if metrics_data else {}
        
        # Format timestamps
        ts = exec_meta.get("timestamp", "N/A").replace("T", " ")[:16]
        
        st.markdown(f"""
        <div style="font-family: 'Poppins'; font-size: 0.85rem; color: #707eae; display: flex; gap: 1.5rem; margin-top: -1rem; margin-bottom: 2rem;">
            <span>Run ID: <b style="color:#2b3674">{current_run}</b></span>
            <span>•</span>
            <span>Grid: <b>{params.get('nx', 'N/A')}x{params.get('ny', 'N/A')}</b></span>
            <span>•</span>
            <span>Step: <b>{params.get('dt', 'N/A')}s</b></span>
            <span>•</span>
            <span>Time: <b>{ts}</b></span>
            <span>•</span>
            <span>Duration: <b>{exec_meta.get('runtime_ms', 0):.2f}ms</b></span>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # Trust Indicators (Pills)
        insights = get_run_details(current_run, "insights")
        
        st.markdown(f"""
        <div style="display:flex; justify-content: flex-end; gap: 10px; margin-top: 1rem;">
            <div class="status-pill {'success' if metrics_data else 'warning'}">
                { '● Verified' if metrics_data else '○ Pending' }
            </div>
            <div class="status-pill {'success' if insights else 'warning'}" style="background-color: #EFF4FB; color: #A3AED0;">
                 { '● Assessment Ready' if insights else '○ No Assessment' }
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Metrics Section
    if metrics_data:
        st.markdown("<h3>Run Performance Metrics</h3>", unsafe_allow_html=True)
        perf = metrics_data.get("performance_metrics", {})
        qual = metrics_data.get("quality_metrics", {})
        converged = qual.get("converged")
        
        # 4-Column Grid
        c1, c2, c3, c4 = st.columns(4)
        
        # HERO CARD: Stability (Contextualized)
        with c1:
            st.markdown(f"""
            <div class="hero-card">
                <div class="hero-label">Stability Ratio (CFL)</div>
                <div class="hero-value">{perf.get('stability_ratio', 0):.4f}</div>
                <div class="hero-sub">Threshold &lt; 1.0</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Standard Cards (Clarified Units - Normalized)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Max Temperature</div>
                <div class="metric-value">{perf.get('max_temperature', 0):.4f}</div>
                <div class="metric-sub" style="color:#A3AED0; font-weight:400;">Normalized (T/T_ref)</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Mean Temperature</div>
                <div class="metric-value">{perf.get('mean_temperature', 0):.4f}</div>
                <div class="metric-sub" style="color:#A3AED0; font-weight:400;">Normalized Distribution</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c4:
             st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Physics Validation</div>
                <div class="metric-value" style="font-size:1.4rem;">{ 'Pass' if converged else 'Fail' }</div>
                <div class="metric-sub" style="color: {'#05cd99' if converged else '#EE5D50'}; font-size: 0.75rem;">
                   {'✓ Convergence' if converged else '⚠️ Diverged'} | {'✓ Mass' if converged else '? Mass'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # CHART: Global Context (Add Chart as requested)
        st.markdown("<h3>Metric Profile</h3>", unsafe_allow_html=True)
        chart_data = pd.DataFrame({
            "Metric": ["Max Temp", "Mean Temp", "Stability"],
            "Value": [perf.get('max_temperature', 0), perf.get('mean_temperature', 0), perf.get('stability_ratio', 0)]
        }).set_index("Metric")
        st.bar_chart(chart_data, color="#111c44", height=200)

    # AI Assessment Card (Compact Empty State)
    st.markdown("<h3>Engineering Assessment</h3>", unsafe_allow_html=True)
    
    if insights:
        data = insights.get("json", {})
        
        # Big Content Card
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            
            # Exec Summary
            st.markdown(f"""
            <div style="margin-bottom: 2rem;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #a3aed0; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;">Executive Summary</div>
                <div style="font-size: 1.1rem; line-height: 1.8; color: #2b3674; font-weight: 500;">{data.get('executive_summary', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Risks & Tradeoffs (2 Col)
            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown('<div style="font-weight: 700; color: #2b3674; margin-bottom: 1rem;">⚠️ Risks & Anomalies</div>', unsafe_allow_html=True)
                for risk in data.get("anomalies_or_risks", []):
                    st.markdown(f"""
                    <div style="display:flex; align-items:flex-start; margin-bottom: 1rem; padding: 1rem; bg:transparent;">
                       <span style="font-size: 1.2rem; margin-right: 1rem; line-height:1;">•</span>
                       <span style="color: #707eae; font-weight: 500;">{risk}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with rc2:
                st.markdown('<div style="font-weight: 700; color: #2b3674; margin-bottom: 1rem;">⚖️ Trade-offs</div>', unsafe_allow_html=True)
                for trade in data.get("tradeoffs", []):
                    st.markdown(f"""
                    <div style="display:flex; align-items:flex-start; margin-bottom: 1rem; padding: 1rem; bg:transparent;">
                       <span style="font-size: 1.2rem; margin-right: 1rem; line-height:1;">•</span>
                       <span style="color: #707eae; font-weight: 500;">{trade}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True) 

            # Recs separate
            st.markdown(f"""
            <div class="content-card">
                <div style="font-weight: 700; color: #2b3674; margin-bottom: 1rem;">🧪 Recommended Experiments</div>
                <ul style="color: #707eae; line-height: 1.8; margin-left: 1rem;">
                    {''.join([f'<li>{r}</li>' for r in data.get('recommended_next_experiments', [])])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Compact Empty State (Actionable)
        st.info("ℹ️ AI Assessment not generated for this run.")
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; align-items: center; background: white; padding: 1rem; border-radius: 12px; border: 1px solid #e5e7eb;">
            <div style="font-weight: 600; color: #2b3674;">Action:</div>
            <code style="background: #f4f7fe; color: #2b3674; padding: 0.5rem 1rem; border-radius: 6px;">make insights RUN_ID={current_run}</code>
        </div>
        """, unsafe_allow_html=True)

    # Artifacts Section
    with st.expander("Explore Artifacts & Files"):
         st.markdown(f"- [Metrics JSON]({API_URL}/runs/{current_run}/metrics)")
         st.markdown(f"- [Insights JSON]({API_URL}/runs/{current_run}/insights)")


# 2. COMPARISON VIEW
elif view_mode == "Comparison" and current_run and comparison_run:
    st.markdown("<h1>Run Comparison</h1>", unsafe_allow_html=True)
    
    # 2 Cards Top
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="stCard">
            <div style="color: #a3aed0; font-size: 0.8rem; letter-spacing: 1px; font-weight: 600;">BASELINE</div>
            <div style="color: #2b3674; font-size: 1.5rem; font-weight: 700;">{current_run}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="hero-card" style="background: linear-gradient(135deg, #868CFF 0%, #4318FF 100%);">
            <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; letter-spacing: 1px; font-weight: 600;">CANDIDATE</div>
            <div style="color: white; font-size: 1.5rem; font-weight: 700;">{comparison_run}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Fetch Both
    m1 = get_run_details(current_run, "metrics")
    m2 = get_run_details(comparison_run, "metrics")
    
    if m1 and m2:
        p1 = m1.get("performance_metrics", {})
        p2 = m2.get("performance_metrics", {})
        
        # Decision Summary Logic
        s1, s2 = p1.get('stability_ratio', 1.0), p2.get('stability_ratio', 1.0)
        t1, t2 = p1.get('max_temperature', 0.0), p2.get('max_temperature', 0.0)
        
        is_stable_improvement = s2 < s1 and s2 < 1.0
        is_temp_improvement = t2 < t1
        
        decision_text = "Candidate shows improvements."
        decision_color = "#05cd99"
        
        if is_stable_improvement:
             decision_text = f"Candidate is more stable (Stability -{(s1-s2):.2f})."
        elif not is_stable_improvement and s2 > 1.0:
             decision_text = "Candidate is UNSTABLE. Do not proceed."
             decision_color = "#EE5D50"
             
        # Decision Card
        st.markdown(f"""
        <div class="content-card" style="border-left: 5px solid {decision_color};">
            <div style="font-weight: 700; color: #2b3674; margin-bottom:0.5rem;">DECISION SUMMARY</div>
            <div style="font-size: 1.1rem; color: #2b3674;">{decision_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3>Performance Deltas</h3>", unsafe_allow_html=True)
        with st.container():
            # Using st.metric here as it's cleaner for simple deltas, 
            # but wrapping in a content card container if possible? 
            # Streamlit metrics are hard to style. Let's use custom HTML again for consistency.
            
            c1, c2, c3 = st.columns(3)
            
            # Helper
            def diff_card(label, v1, v2, suffix=""):
                delta = v2 - v1
                # Logic: Is positive delta good or bad? 
                # Stability: Lower is better. Delta < 0 is Green.
                # Temp: Context dependent, but let's assume Lower is better (Green) usually for peaks.
                
                is_good = False
                if label == "Stability":
                    is_good = delta < 0
                else: 
                     # For temps, maybe we tolerate increase? Let's treat reduction as Green for now.
                     is_good = delta <= 0
                
                color = "#05cd99" if is_good else "#EE5D50"
                
                return f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{v2:.4f}{suffix}</div>
                    <div style="color: {color}; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem;">
                        {'+' if delta > 0 else ''}{delta:.4f} vs baseline
                    </div>
                </div>
                """
            
            with c1:
                st.markdown(diff_card("Max Temp", p1.get('max_temperature', 0), p2.get('max_temperature', 0), " (Norm)"), unsafe_allow_html=True)
            with c2:
                st.markdown(diff_card("Mean Temp", p1.get('mean_temperature', 0), p2.get('mean_temperature', 0), " (Norm)"), unsafe_allow_html=True)
            with c3:
                st.markdown(diff_card("Stability", p1.get('stability_ratio', 1), p2.get('stability_ratio', 1)), unsafe_allow_html=True)

else:
    st.markdown("<div style='text-align:center; padding: 4rem; color: #a3aed0;'>Please select runs from the sidebar.</div>", unsafe_allow_html=True)
