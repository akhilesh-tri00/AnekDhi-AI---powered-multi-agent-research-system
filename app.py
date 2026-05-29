import streamlit as st
import time
from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain,
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AnekDhi AI - Research Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# CUSTOM CSS (NEON THEME & ANIMATIONS)
# ---------------------------------------------------

st.markdown(
    """
    <style>
    /* Dark Neon Background */
    .stApp {
        background-color: #05050f;
    }
    
    /* AnekDhi AI Glowing Title */
    .glowing-title {
        text-align: center;
        font-size: 4.5rem;
        font-weight: 900;
        color: #ffffff;
        margin-top: -30px;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 
            0 0 10px #00f3ff, 
            0 0 20px #00f3ff, 
            0 0 40px #00f3ff, 
            0 0 80px #00f3ff;
    }
    .glowing-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #e0e0e0;
        margin-bottom: 30px;
        letter-spacing: 2px;
        text-shadow: 0 0 5px #ff00ff;
    }

    /* Neon Button */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: transparent;
        color: #00f3ff !important;
        border: 2px solid #00f3ff;
        padding: 12px;
        font-weight: bold;
        box-shadow: 0 0 10px #00f3ff, inset 0 0 10px #00f3ff;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #00f3ff;
        color: #000000 !important;
        box-shadow: 0 0 20px #00f3ff, inset 0 0 20px #00f3ff;
    }

    /* Step Indicators Styles */
    .step-box {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        transition: all 0.4s ease;
    }
    .step-pending {
        background-color: #111122;
        border: 2px solid #333;
        color: #666;
    }
    .step-running {
        background-color: rgba(0, 243, 255, 0.1);
        border: 2px solid #00f3ff;
        color: #00f3ff;
        text-shadow: 0 0 5px #00f3ff;
        box-shadow: 0 0 15px #00f3ff, inset 0 0 10px rgba(0,243,255,0.2);
        animation: pulse-neon 1.5s infinite;
    }
    .step-completed {
        background-color: rgba(0, 255, 136, 0.1);
        border: 2px solid #00ff88;
        color: #00ff88;
        text-shadow: 0 0 5px #00ff88;
        box-shadow: 0 0 10px #00ff88;
    }

    /* Keyframes for Running Phase Animation */
    @keyframes pulse-neon {
        0% { box-shadow: 0 0 5px #00f3ff, inset 0 0 5px rgba(0,243,255,0.2); }
        50% { box-shadow: 0 0 25px #00f3ff, inset 0 0 15px rgba(0,243,255,0.5); }
        100% { box-shadow: 0 0 5px #00f3ff, inset 0 0 5px rgba(0,243,255,0.2); }
    }

    /* Container Borders */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-color: #ff00ff !important;
        box-shadow: 0 0 10px rgba(255,0,255,0.2);
        background-color: #0a0a1a;
    }
    
    /* Text colors */
    h1, h2, h3, p, span, div {
        color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# ANEKDHI AI MAIN HEADER
# ---------------------------------------------------
st.markdown('<h1 class="glowing-title">AnekDhi AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="glowing-subtitle">Powered Multi-Agent Research Engine</p>', unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:
    st.markdown("<h2 style='color: #00f3ff; text-shadow: 0 0 5px #00f3ff;'>🔬 AnekDhi Console</h2>", unsafe_allow_html=True)
    st.caption("v2.4.0-neon-active")

    st.divider()

    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Impact of AI on Healthcare",
    )

    run_button = st.button("Generate Research")

    st.divider()

    st.markdown("### Agent Settings")

    deep_scraping = st.checkbox("Enable Deep Scraping", value=True)
    include_citations = st.checkbox("Include Citations", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "AnekDhi AI orchestrates multiple autonomous agents "
        "to generate high-quality research reports."
    )

# ---------------------------------------------------
# DEFAULT SCREEN
# ---------------------------------------------------

if not run_button:
    st.info("Enter a topic in the sidebar and click 'Generate Research' to awaken AnekDhi AI.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Pipeline Status")
        st.write("Awaiting commands...")
    with col2:
        st.markdown("### Current Report")
        st.write("---")

# ---------------------------------------------------
# PIPELINE EXECUTION
# ---------------------------------------------------
else:
    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    state = {}

    st.markdown(f"<h3 style='color: #ff00ff;'>Current Session: {topic}</h3>", unsafe_allow_html=True)
    
    # ---------------------------------------------------
    # DYNAMIC STEPS VISUALIZATION FUNCTION
    # ---------------------------------------------------
    step_placeholders = st.columns(4)
    
    def update_steps(active_index):
        steps = ["Search", "Reading", "Writing", "Critique"]
        for i, col in enumerate(step_placeholders):
            if i < active_index:
                status_class = "step-completed"
                icon = "✅"
            elif i == active_index:
                status_class = "step-running"
                icon = "⚡"
            else:
                status_class = "step-pending"
                icon = "🔒"
            
            html = f"""
            <div class="step-box {status_class}">
                <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 5px;">STEP {i+1}</div>
                <div style="font-size: 1.2rem;">{icon} {steps[i]}</div>
            </div>
            """
            with col:
                st.empty() # Clear previous
                st.markdown(html, unsafe_allow_html=True)

    # Initialize steps (Step 1 running)
    update_steps(0)

    st.divider()

    # ---------------------------------------------------
    # TWO-COLUMN LAYOUT
    # ---------------------------------------------------
    log_col, report_col = st.columns([1, 2])

    with log_col:
        st.markdown("<h2 style='color: #00f3ff;'>Agent Activity Log</h2>", unsafe_allow_html=True)
        try:
            # ================== STEP 1 ==================
            update_steps(0)
            with st.status("⚡ Step 1: Search Agent is working...", expanded=True) as status:
                search_agent = build_search_agent()
                search_result = search_agent.invoke({
                    "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
                })
                state["search_results"] = search_result["messages"][-1].content
                st.success("Web intelligence collected")
                st.code(state["search_results"][:500] + "...", language="markdown")
                status.update(label="Search Completed", state="complete")

            # ================== STEP 2 ==================
            update_steps(1)
            with st.status("⚡ Step 2: Reader Agent is scraping resources...", expanded=True) as status:
                reader_agent = build_reader_agent()
                reader_result = reader_agent.invoke({
                    "messages": [("user", f"Based on the search results below about '{topic}', select the most relevant source and extract detailed insights.\n\nSEARCH RESULTS:\n{state['search_results'][:1000]}")]
                })
                state["scraped_content"] = reader_result["messages"][-1].content
                st.success("Deep content extracted")
                st.code(state["scraped_content"][:500] + "...", language="markdown")
                status.update(label="Reading Completed", state="complete")

            # ================== STEP 3 ==================
            update_steps(2)
            with st.status("⚡ Step 3: Writer Agent is drafting report...", expanded=True) as status:
                research_combined = f"SEARCH RESULTS:\n{state['search_results']}\n\nSCRAPED CONTENT:\n{state['scraped_content']}"
                state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
                st.success("Research report generated")
                status.update(label="Writing Completed", state="complete")

            # ================== STEP 4 ==================
            update_steps(3)
            with st.status("⚡ Step 4: Critic Agent is reviewing...", expanded=True) as status:
                state["feedback"] = critic_chain.invoke({"report": state["report"]})
                st.success("Review completed")
                status.update(label="Critique Completed", state="complete")

            # All Steps Done
            update_steps(4)

        except Exception as e:
            st.error(f"Pipeline Error: {str(e)}")

    with report_col:
        st.markdown("<h2 style='color: #00ff88;'>Generated Research Report</h2>", unsafe_allow_html=True)
        if "report" in state:
            with st.container(border=True):
                st.markdown(state["report"])
        st.divider()
        if "feedback" in state:
            st.markdown("<h2 style='color: #ff00ff;'>Critic Agent Feedback</h2>", unsafe_allow_html=True)
            with st.expander("View Detailed Assessment", expanded=True):
                st.markdown(state["feedback"])

    if "report" in state:
        st.markdown("""
            <div style="text-align: center; padding: 20px; border: 2px solid #00ff88; border-radius: 10px; background-color: rgba(0,255,136,0.1); margin-top: 20px;">
                <h3 style="color: #00ff88; margin:0;">🎉 AnekDhi AI Pipeline Finished Successfully!</h3>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()