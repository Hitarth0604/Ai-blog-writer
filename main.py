from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
import json

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
        f"**IMPORTANT:** Do NOT include ```json code fences or any other formatting around the JSON.\n"
        f"Respond ONLY with raw JSON.\n\n"
        f"Topic: {data.topic}\n"
        f"Tone: {data.tone}\n"
        f"Audience: {data.audience}\n\n"
        f"JSON format:\n"
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

    # Clean: remove any leading/trailing code fences
    if raw_output.startswith("```json"):
        raw_output = raw_output.replace("```json", "").strip()
    if raw_output.endswith("```"):
        raw_output = raw_output[:-3].strip()
    if raw_output.startswith("```"):
        raw_output = raw_output[3:].strip()

    # Now parse
    try:
        blog = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print("\n=== JSON DECODE ERROR ===\n", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON from model. Raw output:\n{raw_output}"
        )

    return blog