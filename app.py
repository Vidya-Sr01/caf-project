import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime

# ------------------------
# PAGE CONFIGURATION
# ------------------------
st.set_page_config(
    page_title="CAF Dashboard",
    page_icon="📚",
    layout="wide"
)

# ------------------------
# DATA FILE
# ------------------------
DATA_FILE = "caf_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

contexts = load_data()

# ------------------------
# SIDEBAR
# ------------------------
st.sidebar.title("📚 CAF Menu")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Context", "View Contexts", "Statistics"]
)

# ------------------------
# DASHBOARD
# ------------------------
if menu == "Dashboard":

    st.title("📚 Context Assembly Framework")

    total_contexts = len(contexts)

    categories = set()
    for c in contexts:
        categories.add(c["category"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Contexts", total_contexts)

    with col2:
        st.metric("Categories", len(categories))

    with col3:
        st.metric(
            "Current Date",
            datetime.now().strftime("%d-%m-%Y")
        )

    st.divider()

    st.subheader("Recent Contexts")

    if contexts:

        df = pd.DataFrame(contexts)

        st.dataframe(
            df[
                [
                    "title",
                    "category",
                    "timestamp"
                ]
            ],
            use_container_width=True
        )

    else:
        st.info("No contexts available.")

# ------------------------
# ADD CONTEXT
# ------------------------
elif menu == "Add Context":

    st.title("➕ Add Context")

    title = st.text_input("Context Title")

    category = st.selectbox(
        "Category",
        [
            "Requirement",
            "Design",
            "Development",
            "Testing",
            "Documentation"
        ]
    )

    description = st.text_area("Description")

    if st.button("Save Context"):

        if title and description:

            new_context = {
                "id": str(uuid.uuid4()),
                "title": title,
                "category": category,
                "description": description,
                "timestamp": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            contexts.append(new_context)

            save_data(contexts)

            st.success("Context Added Successfully")

        else:
            st.warning(
                "Please enter title and description."
            )

# ------------------------
# VIEW CONTEXTS
# ------------------------
elif menu == "View Contexts":

    st.title("📋 View Contexts")

    search = st.text_input(
        "Search Context"
    )

    filtered = []

    for c in contexts:

        if search.lower() in c["title"].lower():
            filtered.append(c)

    if search == "":
        filtered = contexts

    if filtered:

        for item in filtered:

            with st.expander(
                f"{item['title']} ({item['category']})"
            ):

                st.write(
                    f"**Description:** {item['description']}"
                )

                st.write(
                    f"**Created:** {item['timestamp']}"
                )

    else:
        st.warning(
            "No matching contexts found."
        )

# ------------------------
# STATISTICS
# ------------------------
elif menu == "Statistics":

    st.title("📊 Statistics")

    if contexts:

        df = pd.DataFrame(contexts)

        category_counts = (
            df["category"]
            .value_counts()
        )

        st.bar_chart(category_counts)

        st.subheader(
            "Category Distribution"
        )

        st.dataframe(
            category_counts,
            use_container_width=True
        )

    else:
        st.info(
            "Add contexts to view statistics."
        )
