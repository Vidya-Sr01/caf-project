import streamlit as st
import json
import os
import uuid
import time
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CAF | Context Assembly",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# --- CSS ---
st.markdown("""
<style>
    :root {
        --gh-bg: var(--background-color);
        --gh-text: var(--text-color);
        --gh-sidebar-bg: var(--secondary-background-color);
        --gh-card-bg: var(--background-color);
        --gh-input-bg: var(--secondary-background-color);
        --gh-border: rgba(128, 128, 128, 0.2);
        --gh-btn-primary-bg: #2da44e;
        --gh-btn-primary-hover: #2c974b;
        --gh-btn-primary-text: #ffffff;
        --gh-btn-bg: var(--secondary-background-color);
        --gh-btn-text: var(--text-color);
        --gh-btn-border: rgba(128, 128, 128, 0.2);
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        color: var(--gh-text) !important;
        background-color: var(--gh-bg) !important;
    }
    
    h1 {
        font-weight: 600;
        font-size: 2rem;
        border-bottom: 1px solid var(--gh-border);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        color: var(--gh-text) !important;
    }
    h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: var(--gh-text) !important;
    }

    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: var(--gh-card-bg);
        border: 1px solid var(--gh-border);
        border-radius: 6px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px;
        background-color: var(--gh-input-bg) !important;
        color: var(--gh-text) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #0969da !important;
        box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.3);
    }
    
    label[data-testid="stWidgetLabel"] p {
        color: var(--gh-text) !important;
        font-weight: 600;
    }

    .stButton button[kind="primary"] {
        background-color: var(--gh-btn-primary-bg) !important;
        color: var(--gh-btn-primary-text) !important;
        border: 1px solid rgba(27,31,36,0.15) !important;
        font-weight: 600;
    }
    .stButton button[kind="primary"]:hover {
        background-color: var(--gh-btn-primary-hover) !important;
        filter: brightness(1.05);
    }

    .stButton button {
        background-color: var(--gh-btn-bg) !important;
        color: var(--gh-btn-text) !important;
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
    }
    .stButton button:hover {
        border-color: var(--gh-text) !important;
        opacity: 0.8;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--gh-sidebar-bg) !important;
        border-right: 1px solid var(--gh-border);
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: var(--gh-text) !important;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: var(--gh-text) !important;
        background-color: transparent !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: var(--gh-text) !important;
    }

    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: var(--gh-text) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        opacity: 0.7;
        color: var(--gh-text) !important;
    }
    
    .streamlit-expanderHeader {
        color: var(--gh-text) !important;
        background-color: transparent !important;
        border: 1px solid var(--gh-border);
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
STORAGE_FILE = "caf_storage.json"

QUESTIONS = [
    {"id": "objective", "label": "Task Objective", "help": "Describe the primary task objective clearly.", "type": "text_area", "required": True},
    {"id": "audience", "label": "Target Audience", "help": "Who is this instruction for? (e.g., Junior Dev, Customer)", "type": "text_input", "required": True},
    {"id": "tone", "label": "Tone & Style", "options": ["Professional", "Direct", "Casual", "Urgent", "Technical"], "type": "select", "required": True},
    {"id": "constraints", "label": "Constraints", "help": "List any restrictions (one per line).", "type": "text_area", "required": False},
    {"id": "output_format", "label": "Output Format", "help": "How should the final result look?", "type": "text_input", "required": True},
    {"id": "risk_level", "label": "Risk Level", "options": ["Low", "Medium", "High"], "type": "select", "required": True}
]

TEMPLATE = """## Instruction Objective
{objective}

**Target Audience:** {audience}  
**Tone:** {tone}  
**Risk Level:** {risk_level}

### Constraints
{constraints}

### Expected Output
{output_format}"""

# --- STORAGE ---

def init_storage():
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w") as f:
            json.dump({"instructions": {}}, f)

def load_data():
    if not os.path.exists(STORAGE_FILE):
        init_storage()
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"instructions": {}}

def save_data(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_instruction(instruction_id, context, assembled_text):
    data = load_data()
    timestamp = datetime.now().isoformat()
    
    if instruction_id not in data["instructions"]:
        data["instructions"][instruction_id] = {
            "id": instruction_id,
            "created_at": timestamp,
            "versions": []
        }
    
    version_num = len(data["instructions"][instruction_id]["versions"]) + 1
    new_version = {
        "version": version_num,
        "timestamp": timestamp,
        "context": context,
        "assembled_instruction": assembled_text,
        "manual_edits": False,
        "feedback": None
    }
    
    data["instructions"][instruction_id]["versions"].append(new_version)
    save_data(data)
    return version_num

def add_feedback(instruction_id, version_index, rating, tags):
    data = load_data()
    if instruction_id in data["instructions"]:
        try:
            target_version = data["instructions"][instruction_id]["versions"][version_index]
            target_version["feedback"] = {
                "rating": rating,
                "tags": tags,
                "timestamp": datetime.now().isoformat()
            }
            save_data(data)
            return True
        except IndexError:
            return False
    return False

# --- LOGIC ---

def assemble_instruction(context):
    safe_context = {k["id"]: context.get(k["id"], "") for k in QUESTIONS}
    return TEMPLATE.format(**safe_context)

# --- UI ---

def sidebar_nav():
    with st.sidebar:
        st.markdown("### ⚡ CAF")
        st.caption("Context Assembly Framework v1.0")
        st.markdown("---")
        
        nav = st.radio("Repository", ["New Instruction", "History & Feedback"])
        
        st.markdown("---")
        if st.button("Reset Form", use_container_width=True):
            st.session_state.current_context = None
            st.session_state.generated_text = None
            st.rerun()
            
        return nav

def get_rating_color(rating):
    if rating == 1: return "#cf222e", "Poor"
    if rating == 2: return "#bc4c00", "Fair"
    if rating == 3: return "#bf8700", "Average"
    if rating == 4: return "#4ac26b", "Good"
    if rating == 5: return "#2da44e", "Excellent"
    return "#6e7681", "Not Rated"

def render_star_rating(key_suffix):
    st.write("**Rate Quality**")
    rating = st.feedback("stars", key=f"rating_{key_suffix}")
    display_rating = (rating + 1) if rating is not None else 0
    
    if display_rating > 0:
        color, label = get_rating_color(display_rating)
        st.markdown(
            f"""
            <div style="background-color: {color}15; border: 1px solid {color}; color: {color}; 
            display: inline-block; padding: 2px 10px; border-radius: 2em; font-weight: 600; font-size: 0.85rem; margin-top: 5px;">
            {label} ({display_rating}/5)
            </div>
            """, 
            unsafe_allow_html=True
        )
    return display_rating

def page_new_instruction():
    st.title("Create Instruction")
    st.markdown("_Define context parameters to assemble a new artifact._")
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.subheader("1. Context Definitions")
            st.markdown("Fill out the issue parameters below.")
            
            with st.form("caf_input_form"):
                form_data = {}
                for q in QUESTIONS:
                    if q["type"] == "text_area":
                        form_data[q["id"]] = st.text_area(q["label"], height=100, help=q.get("help"))
                    elif q["type"] == "select":
                        form_data[q["id"]] = st.selectbox(q["label"], q["options"])
                    else:
                        form_data[q["id"]] = st.text_input(q["label"], help=q.get("help"))
                
                submitted = st.form_submit_button("Generate Instruction", use_container_width=True)
                
                if submitted:
                    missing = [q["label"] for q in QUESTIONS if q.get("required") and not form_data[q["id"]]]
                    if missing:
                        st.error(f"Missing fields: {', '.join(missing)}")
                    else:
                        status = st.status("Processing...", expanded=True)
                        status.write("Parsing input parameters...")
                        time.sleep(0.3)
                        status.write("Assembling template...")
                        time.sleep(0.3)
                        status.update(label="Ready", state="complete", expanded=False)
                        
                        st.session_state.current_context = form_data
                        st.session_state.generated_text = assemble_instruction(form_data)
                        st.session_state.editing_text = st.session_state.generated_text
                        st.rerun()

    with col2:
        if "current_context" in st.session_state and st.session_state.current_context:
            with st.container(border=True):
                st.subheader("2. Artifact Preview")
                st.info("Review the assembled output below. You can make manual edits before committing.")
                
                final_text = st.text_area(
                    "Instruction Artifact", 
                    value=st.session_state.editing_text, 
                    height=400,
                    label_visibility="collapsed"
                )
                
                st.session_state.editing_text = final_text
                
                if st.button("Commit to History", type="primary", use_container_width=True):
                    inst_id = str(uuid.uuid4())[:8]
                    is_edited = final_text != st.session_state.generated_text
                    
                    save_instruction(inst_id, st.session_state.current_context, final_text)
                    
                    if is_edited:
                        data = load_data()
                        data["instructions"][inst_id]["versions"][-1]["manual_edits"] = True
                        save_data(data)
                    
                    st.toast(f"Committed artifact {inst_id}", icon="✅")
                    st.session_state.current_context = None
                    st.session_state.generated_text = None
                    st.rerun()
            
            with st.expander("View JSON Context"):
                st.json(st.session_state.current_context)
                
        else:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="text-align: center; opacity: 0.6; padding: 40px; color: var(--gh-text);">
                        <h3>No changes yet</h3>
                        <p>Complete the form to generate a preview.</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

def page_history():
    st.title("History")
    data = load_data()
    instructions = data.get("instructions", {})
    
    if instructions:
        total_docs = len(instructions)
        total_versions = sum(len(i['versions']) for i in instructions.values())
        
        all_ratings = []
        for i in instructions.values():
            for v in i['versions']:
                if v.get('feedback') and v['feedback'].get('rating'):
                    all_ratings.append(v['feedback']['rating'])
        
        avg_rating = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else 0.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Artifacts", total_docs)
        m2.metric("Total Versions", total_versions)
        m3.metric("Avg Score", f"{avg_rating}")
        st.markdown("---")

    if not instructions:
        st.warning("No history found.")
        return

    col_search, col_filter = st.columns([3, 1])
    with col_search:
        selected_id = st.selectbox("Select Artifact", list(instructions.keys()), format_func=lambda x: f"{x} (Created: {instructions[x]['created_at'][:10]})")

    if selected_id:
        inst_data = instructions[selected_id]
        versions = inst_data["versions"]
        
        tabs = st.tabs([f"v{v['version']}" for v in versions])
        
        for idx, tab in enumerate(tabs):
            with tab:
                version = versions[idx]
                c1, c2 = st.columns([2, 1], gap="large")
                
                with c1:
                    with st.container(border=True):
                        st.caption(f"Committed on {version['timestamp']}")
                        if version['manual_edits']:
                            st.warning("Contains manual edits")
                        st.markdown(version['assembled_instruction'])
                
                with c2:
                    with st.container(border=True):
                        st.subheader("Feedback")
                        existing_feedback = version.get("feedback")
                        
                        if existing_feedback:
                            rating = existing_feedback['rating']
                            color, label = get_rating_color(rating)
                            st.markdown(f"""
                                <div style="font-size: 1.5rem; color: {color}; margin-bottom: 5px;">
                                    {'★' * rating}{'☆' * (5-rating)}
                                </div>
                                <div style="color: {color}; font-weight: 600;">
                                    {label}
                                </div>
                            """, unsafe_allow_html=True)
                            if existing_feedback['tags']:
                                st.write("**Tags:**")
                                for t in existing_feedback['tags']:
                                    st.markdown(f"`{t}`")
                        else:
                            st.info("Rate this version")
                            user_rating = render_star_rating(f"{selected_id}_{version['version']}")
                            tags = st.multiselect("Issues", ["Verbose", "Unclear", "Incomplete", "Incorrect Tone", "Perfect"], key=f"tags_{selected_id}_{version['version']}")
                            if st.button("Submit Feedback", key=f"btn_{selected_id}_{version['version']}"):
                                if user_rating > 0:
                                    add_feedback(selected_id, idx, user_rating, tags)
                                    st.toast("Feedback saved", icon="💾")
                                    st.rerun()
                                else:
                                    st.error("Select a rating")

# --- MAIN APP ---
def main():
    init_storage()
    page = sidebar_nav()
    if page == "New Instruction":
        page_new_instruction()
    elif page == "History & Feedback":
        page_history()

if __name__ == "__main__":
    main()

 
