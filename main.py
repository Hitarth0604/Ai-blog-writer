from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
import json
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

class BlogRequest(BaseModel):
    topic: str
    tone: str
    audience: str

@app.post("/generate")
async def generate_blog(data: BlogRequest):
    prompt = (
        f"You are a helpful assistant that ALWAYS responds ONLY with valid JSON (no markdown wrapping, no commentary).\n\n"
        f"Write a complete, high-quality SEO blog post with:\n"
        f"- A compelling title\n"
        f"- A meta description (max 160 characters)\n"
        f"- 5 comma-separated SEO tags\n"
        f"- A body with at least 500 words\n"
        f"- The body must use Markdown with multiple sections and headings.\n\n"
        f"**IMPORTANT:** All strings must be properly JSON-escaped (e.g., newlines as \\n, quotes as \\\").\n\n"
        f"Topic: {data.topic}\n"
        f"Tone: {data.tone}\n"
        f"Audience: {data.audience}\n\n"
        f"Respond ONLY with JSON in this format:\n"
        f'{{\n'
        f'  "title": "string",\n'
        f'  "meta_description": "string",\n'
        f'  "tags": "tag1, tag2, tag3, tag4, tag5",\n'
        f'  "body": "markdown content here"\n'
        f'}}'
    )

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You generate structured JSON blog posts without any commentary or formatting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    raw_output = completion.choices[0].message.content.strip()

    print("\n=== RAW MODEL OUTPUT ===\n", raw_output)

    # Pre-clean output: escape unescaped newlines and quotes
    cleaned_output = raw_output.replace("\r", "\\r").replace("\n", "\\n")
    # Also escape unescaped quotes after colons (common)
    cleaned_output = re.sub(r'(?<=:\s)"(.*?)"(,?)', lambda m: ':"' + m.group(1).replace('"', '\\"') + '"' + m.group(2), cleaned_output)

    try:
        blog = json.loads(cleaned_output)
    except json.JSONDecodeError as e:
        print("\n=== JSON DECODE ERROR ===\n", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON from model. Raw output:\n{raw_output}"
        )

    return blog
