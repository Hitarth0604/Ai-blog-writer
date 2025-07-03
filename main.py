from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BlogRequest(BaseModel):
    topic: str
    tone: str
    audience: str

@app.post("/generate")
async def generate_blog(data: BlogRequest):
    # Here you can call your Groq/generative model instead of this dummy content.
    title = f"Revolutionize Your Workflow: {data.topic}"
    meta_description = (
        f"Discover how {data.topic} can transform your workflow with a {data.tone.lower()} approach."
    )
    tags = "ai, productivity, workflow, 2025"
    body = (
        f"# {data.topic}\n\n"
        f"Welcome to the future of {data.topic.lower()}! "
        f"This {data.tone.lower()} guide is tailored for {data.audience}.\n\n"
        "## Section 1: Overview\n"
        "Learn about the most important trends and tools.\n\n"
        "## Section 2: Implementation\n"
        "Tips on applying these insights to your workflow.\n\n"
        "## Conclusion\n"
        "Stay ahead by embracing innovation today."
    )

    return {
        "title": title,
        "meta_description": meta_description,
        "tags": tags,
        "body": body
    }
