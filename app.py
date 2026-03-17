# app.py

import streamlit as st
import streamlit.components.v1 as components
from anthropic import Anthropic
from rag_system import ConsultingRAG
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
try:
    # Try Streamlit secrets first (for cloud deployment)
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    anthropic = Anthropic(api_key=api_key)
    st.sidebar.success("✓ Using Streamlit Secrets")
except Exception as e:
    # Fall back to .env file (for local development)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        anthropic = Anthropic(api_key=api_key)
        st.sidebar.info("Using .env file")
    else:
        st.error(f"""
        **API Key Not Found!**
        
        Please configure your Anthropic API key in Streamlit Cloud:
        1. Click '⋮' menu → Settings
        2. Click 'Secrets' tab
        3. Add: ANTHROPIC_API_KEY = "your-key-here"
        4. Save and reboot
        
        Error details: {str(e)}
        """)
        st.stop()

# Initialize RAG system
@st.cache_resource
def load_rag_system():
    """Load RAG system once and cache it"""
    rag = ConsultingRAG()
    # Try to load existing database, otherwise build new one
    try:
        rag.load_existing_db()
        print("✓ Loaded existing knowledge base")
    except:
        rag.build_knowledge_base()
    return rag

rag = load_rag_system()

# Page configuration
st.set_page_config(
    page_title="AI Consultant",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .output-section {
        background-color: #f9fafb;
        padding: 2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">AI Consultant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Strategy & Operations Analysis powered by AI</p>', unsafe_allow_html=True)

# About section
with st.expander("ℹ️ About This Tool"):
    st.write("""
    This AI consultant uses proven consulting frameworks to analyze business challenges and provide 
    actionable recommendations. It combines:
    
    - **Gap Analysis** - Identify current vs desired state
    - **RACI Matrix** - Clarify roles and responsibilities  
    - **M&A Integration** - Post-merger best practices
    - **Process Improvement** - Optimize workflows and operations
    
    The tool searches a knowledge base of consulting frameworks and generates customized strategy briefs.
    """)

# Sidebar - Sample Scenarios
st.sidebar.header("📋 Sample Scenarios")
st.sidebar.write("Click to load a pre-filled example:")

sample_scenarios = {
    "Post-M&A Tech Integration": {
        "engagement_type": "M&A Integration",
        "industry": "Technology / SaaS",
        "challenge": "Two companies recently merged. Need to integrate different tech stacks (one on AWS, one on Google Cloud), combine engineering teams, and show synergies to investors within 90 days.",
        "constraints": "Limited budget for migration, key engineers considering leaving, customers worried about service disruption"
    },
    "Scaling Operations 3x": {
        "engagement_type": "Operational Transformation",
        "industry": "E-commerce",
        "challenge": "Company growing 300% year-over-year but operations team can't keep up. Current processes are manual and breaking down. Need to scale without proportional headcount increase.",
        "constraints": "Can't afford expensive enterprise software, need solutions in 6 months, team resistant to change"
    },
    "Building Strategic PMO": {
        "engagement_type": "Organizational Design",
        "industry": "Financial Services",
        "challenge": "Multiple strategic initiatives happening simultaneously with no coordination. Projects are delayed, resources over-allocated, unclear priorities. Need to establish Project Management Office.",
        "constraints": "Decentralized organization, no existing PMO expertise, executives skeptical of process overhead"
    }
}

for scenario_name, scenario_data in sample_scenarios.items():
    if st.sidebar.button(scenario_name):
        st.session_state.engagement_type = scenario_data["engagement_type"]
        st.session_state.industry = scenario_data["industry"]
        st.session_state.challenge = scenario_data["challenge"]
        st.session_state.constraints = scenario_data["constraints"]

# Main input form
st.subheader("🎯 Define Your Challenge")

col1, col2 = st.columns(2)

with col1:
    engagement_type = st.selectbox(
        "Engagement Type",
        [
            "Strategy & Execution",
            "Process Improvement", 
            "Operational Transformation",
            "Organizational Design",
            "M&A Integration"
        ],
        index=0 if "engagement_type" not in st.session_state else 
              ["Strategy & Execution", "Process Improvement", "Operational Transformation", 
               "Organizational Design", "M&A Integration"].index(st.session_state.engagement_type)
    )

with col2:
    industry = st.text_input(
        "Industry",
        value=st.session_state.get("industry", ""),
        placeholder="e.g., Technology, Healthcare, Finance"
    )

challenge = st.text_area(
    "Describe the Challenge",
    value=st.session_state.get("challenge", ""),
    placeholder="What problem are you trying to solve? Be specific about the current situation and desired outcomes.",
    height=150
)

constraints = st.text_input(
    "Key Constraints (Optional)",
    value=st.session_state.get("constraints", ""),
    placeholder="e.g., Budget limits, timeline, resource constraints"
)

# Generate button
if st.button("🚀 Generate Strategy Brief", type="primary"):
    if not challenge:
        st.error("Please describe the challenge before generating a brief.")
    else:
        with st.spinner("🔍 Analyzing challenge and retrieving relevant frameworks..."):
            # Build query for RAG
            query = f"{engagement_type}: {industry} - {challenge}"
            
            # Get relevant frameworks from knowledge base
            relevant_frameworks = rag.get_relevant_frameworks(query, k=3)
            
            # Build prompt for Claude
            system_prompt = """You are a senior Strategy & Operations consultant. 

Your task is to analyze business challenges and provide actionable recommendations using proven consulting frameworks.

Key principles:
- Data-driven and realistic
- Break complex problems into actionable steps
- Balance technical and business perspectives
- Provide specific metrics and timelines
- Professional but clear communication

Output a comprehensive strategy brief with these sections:
1. EXECUTIVE SUMMARY (3-4 key bullets)
2. CURRENT STATE ASSESSMENT
3. GAP ANALYSIS
4. PRIORITIZED RECOMMENDATIONS (with effort/impact scores)
5. IMPLEMENTATION ROADMAP (phased timeline)
6. SUCCESS METRICS
7. RISK REGISTER

Use concrete examples and specific numbers where possible."""

            user_prompt = f"""
RELEVANT CONSULTING FRAMEWORKS:
{relevant_frameworks}

CLIENT CHALLENGE:
Engagement Type: {engagement_type}
Industry: {industry}
Challenge: {challenge}
Constraints: {constraints if constraints else "None specified"}

Using the frameworks above, generate a comprehensive strategy brief for this challenge.
"""

        with st.spinner("🤖 Generating strategy brief with AI..."):
            # Call Anthropic API
            response = anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                ]
            )
            
            # Extract response
            strategy_brief = response.content[0].text
            
            # Display output
            st.markdown('<div class="output-section">', unsafe_allow_html=True)
            st.markdown("## 📄 Strategy Brief")
            st.markdown(strategy_brief)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Signal to Francium parent
            import json as _json
            _signal_data = _json.dumps({
                "type": "francium_signal",
                "toolId": "ai-consultant",
                "event": "brief_generated",
                "data": {
                    "engagement_type": engagement_type,
                    "industry": industry,
                    "challenge_preview": challenge[:200] if challenge else "",
                    "has_constraints": bool(constraints),
                }
            })
            components.html(f"<script>window.top.postMessage({_signal_data}, '*');</script>", height=0)
            
            # Download button
            st.download_button(
                label="⬇️ Download as Text",
                data=strategy_brief.encode('utf-8'),
                file_name=f"strategy_brief_{industry.replace(' ', '_').lower()}.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
    Built with Streamlit • Powered by Claude AI • Knowledge Base: 4 Consulting Frameworks
</div>
""", unsafe_allow_html=True)