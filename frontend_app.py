import streamlit as st
import requests
from io import BytesIO
from output_utils import blog_to_docx

# --- Config ---
API_URL = "https://ai-blog-writer-ibfk.onrender.com/generate"
st.set_page_config(page_title="AI First Draft", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    html, body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f6f7f9;
        color: #1a1a1a;
    }

    .block-container {
        padding: 2rem 3rem;
        max-width: 1000px;
        margin: auto;
    }

    h1, h2, h3 {
        color: #333;
        font-weight: 600;
    }

    .stTextInput > div > div > input {
        font-size: 16px;
        padding: 10px;
        border-radius: 6px;
    }

    .stButton button {
        background-color: #3b82f6;
        color: white;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        border: none;
        margin-top: 1rem;
    }

    .stDownloadButton > button {
        background-color: #10b981 !important;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5rem 1rem;
        margin-top: 1rem;
    }

    .stMarkdown p {
        font-size: 16px;
        line-height: 1.6;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("✍️ AI First Draft")
st.caption("A clean, modern blog generator powered by AI")

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ Settings")

    preset_topic = st.selectbox("Preset Topics", [
        "", "Top AI Tools in 2025", "Morning Routine for Designers",
        "Marketing Hacks for Startups", "Mental Health for Remote Workers"
    ])

    tone = st.selectbox("Tone", [
        "Informative", "Friendly", "Motivational", "Professional", "Casual"
    ])

    audience = st.text_input("Target Audience", "General")

    tone_examples = {
        "Informative": "Factual, structured, clear.",
        "Friendly": "Warm, conversational, approachable.",
        "Motivational": "Energetic, inspiring, action-driven.",
        "Professional": "Corporate, serious, to-the-point.",
        "Casual": "Chill, relaxed, everyday tone."
    }

    st.caption(f"💬 Tone preview: *{tone_examples[tone]}*")



# --- Input Area ---
st.subheader("🔤 Blog Topic")
topic = st.text_input("What should the blog be about?", value=preset_topic)

submitted = st.button("🚀 Generate Blog")

# --- Blog Output ---
if submitted:
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("🧠 Crafting your blog..."):
            try:
                res = requests.post(API_URL, json={
                    "topic": topic,
                    "tone": tone,
                    "audience": audience
                })



                if res.status_code == 200:
                    try:
                        blog = res.json()
                    except Exception as json_err:
                        st.error("❌ Failed to parse JSON response.")
                        raise json_err

                    st.success("✅ Blog generated!")

                    # Display the blog content
                    st.markdown(f"### 📝 {blog['title']}")
                    st.markdown(f"**Meta Description:** {blog['meta_description']}")
                    st.markdown("**Tags:** " + ", ".join(blog['tags'].split(",")))
                    st.markdown("---")

                    # Render the blog body
                    st.markdown(blog["body"], unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown(f"📏 Word Count: {len(blog['body'].split())} words")
                    st.markdown(f"🏷️ Tags: {len(blog['tags'].split(','))} tags")

                    # Download button
                    try:
                        doc = blog_to_docx(
                            blog['title'],
                            blog['meta_description'],
                            blog['tags'],
                            blog['body']
                        )
                        buffer = BytesIO()
                        doc.save(buffer)
                        st.download_button(
                            "📄 Download as .docx",
                            buffer.getvalue(),
                            file_name=f"{blog['title'][:50]}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    except Exception as doc_err:
                        st.warning("Download feature temporarily unavailable.")

                else:
                    st.error(f"❌ Error: {res.status_code}")

            except requests.exceptions.RequestException as req_err:
                st.error("❌ Network error: Could not connect to the blog generation service.")
                
                # Show fallback content
                st.info("📝 Here's a sample blog while we fix the connection:")
                
                fallback_blog = {
                    "title": "5 Tips to Boost Productivity While Working Remotely",
                    "meta_description": "Remote workers, here's how to stay sharp and focused from home.",
                    "tags": "remote work, focus, productivity, home office, habits",
                    "body": """
# 5 Tips to Boost Productivity While Working Remotely

Working from home can be empowering — but it comes with unique challenges and distractions that can impact your productivity.

## 1. Create a Dedicated Workspace

Having a specific area for work helps your brain switch into "work mode" and maintains boundaries between personal and professional life.

## 2. Establish a Morning Routine

Start your day with intention. Whether it's exercise, meditation, or simply making your bed, having a routine sets a positive tone.

## 3. Use the Pomodoro Technique

Work in focused 25-minute intervals with 5-minute breaks. This helps maintain concentration and prevents burnout.

## 4. Minimize Distractions

Turn off non-essential notifications, use website blockers, and communicate your work hours to family members.

## 5. Take Regular Breaks

Step away from your screen regularly. Go for a walk, stretch, or grab some fresh air to recharge your mind.

## Conclusion

Remote work success comes down to creating structure, maintaining boundaries, and being intentional about your habits. Implement these tips gradually to build a sustainable routine that works for you.
                    """
                }
                
                st.markdown(f"### 📝 {fallback_blog['title']}")
                st.markdown(f"**Meta Description:** {fallback_blog['meta_description']}")
                st.markdown("**Tags:** " + ", ".join(fallback_blog['tags'].split(",")))
                st.markdown("---")
                st.markdown(fallback_blog["body"], unsafe_allow_html=True)

            except Exception as e:
                st.error("❌ Something went wrong! Please try again.")