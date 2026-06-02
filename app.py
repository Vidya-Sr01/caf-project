import streamlit as st
import json
import os
import uuid
from datetime import datetime
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="CAF | Context Assembly Framework",
    page_icon="⚡",
    layout="wide"
)

# -------------------------------------------------
# FILES
# -------------------------------------------------

DATA_FILE = "caf_history.json"

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

history = load_history()

# -------------------------------------------------
# STYLING
# -------------------------------------------------

st.markdown("""
<style>
.main-title{
    font-size:38px;
    font-weight:bold;
}
.section-card{
    padding:20px;
    border-radius:12px;
    background:#f5f5f5;
    margin-bottom:10px;
}
.metric-card{
    padding:15px;
    border-radius:10px;
    background:#fafafa;
    border:1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("⚡ CAF v1.0")

page = st.sidebar.radio(
    "Navigation",
    [
        "New Instruction",
        "History & Feedback",
        "Dashboard"
    ]
)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

if page == "Dashboard":

    st.markdown(
        '<p class="main-title">CAF Dashboard</p>',
        unsafe_allow_html=True
    )

    total_records = len(history)

    total_feedback = len(
        [x for x in history if x.get("feedback")]
    )

    avg_rating = 0

    ratings = [
        x["rating"]
        for x in history
        if x.get("rating", 0) > 0
    ]

    if ratings:
        avg_rating = round(
            sum(ratings) / len(ratings),
            2
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Instructions",
            total_records
        )

    with c2:
        st.metric(
            "Feedback Entries",
            total_feedback
        )

    with c3:
        st.metric(
            "Average Rating",
            avg_rating
        )

    st.divider()

    if history:

        df = pd.DataFrame(history)

        st.subheader("Recent Records")

        cols = [
            "title",
            "target_audience",
            "repository",
            "created_at"
        ]

        available = [
            c for c in cols if c in df.columns
        ]

        st.dataframe(
            df[available],
            use_container_width=True
        )

    else:
        st.info("No records found.")

# -------------------------------------------------
# NEW INSTRUCTION
# -------------------------------------------------

elif page == "New Instruction":

    st.markdown(
        '<p class="main-title">New Instruction</p>',
        unsafe_allow_html=True
    )

    title = st.text_input(
        "Instruction Title"
    )

    target_audience = st.selectbox(
        "Target Audience",
        [
            "Students",
            "Researchers",
            "Developers",
            "Business Users",
            "General Public"
        ]
    )

    repository = st.text_input(
        "Repository"
    )

    context = st.text_area(
        "Context / Requirements",
        height=180
    )

    if st.button(
        "Generate Instruction",
        use_container_width=True
    ):

        if title and context:

            generated_content = f"""
Instruction Title:
{title}

Target Audience:
{target_audience}

Repository:
{repository}

Generated Guidance:

Based on the provided context,
the system recommends developing
content tailored for
{target_audience}.

Context Summary:
{context}

Recommended Actions:
1. Analyze requirements.
2. Organize information.
3. Generate structured output.
4. Validate and review results.
5. Collect feedback.
"""

            record = {
                "id": str(uuid.uuid4()),
                "title": title,
                "target_audience": target_audience,
                "repository": repository,
                "context": context,
                "generated_content": generated_content,
                "created_at":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                "rating": 0,
                "feedback": ""
            }

            history.append(record)

            save_history(history)

            st.success(
                "Instruction Generated"
            )

            st.text_area(
                "Generated Output",
                generated_content,
                height=300
            )

        else:
            st.warning(
                "Please enter title and context."
            )

# -------------------------------------------------
# HISTORY & FEEDBACK
# -------------------------------------------------

elif page == "History & Feedback":

    st.markdown(
        '<p class="main-title">History & Feedback</p>',
        unsafe_allow_html=True
    )

    if not history:

        st.info(
            "No generated instructions found."
        )

    else:

        for index, item in enumerate(history):

            with st.expander(
                item["title"]
            ):

                st.write(
                    f"**Target Audience:** "
                    f"{item['target_audience']}"
                )

                st.write(
                    f"**Repository:** "
                    f"{item['repository']}"
                )

                st.write(
                    item["generated_content"]
                )

                rating = st.slider(
                    f"Rating {index}",
                    1,
                    5,
                    value=max(
                        1,
                        item.get("rating", 1)
                    )
                )

                feedback = st.text_area(
                    f"Feedback {index}",
                    value=item.get(
                        "feedback",
                        ""
                    )
                )

                if st.button(
                    f"Save Feedback {index}"
                ):

                    history[index][
                        "rating"
                    ] = rating

                    history[index][
                        "feedback"
                    ] = feedback

                    save_history(history)

                    st.success(
                        "Feedback Saved"
                    )
