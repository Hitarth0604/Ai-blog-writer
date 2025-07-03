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
        f"Generate a blog post in JSON format with these keys:\n"
        f"title\nmeta_description\ntags\nbody\n\n"
        f"Topic: {data.topic}\n"
        f"Tone: {data.tone}\n"
        f"Audience: {data.audience}\n\n"
        f"Example JSON format:\n"
        f"{{\n"
        f'  "title": "...",\n'
        f'  "meta_description": "...",\n'
        f'  "tags": "tag1, tag2, tag3",\n'
        f'  "body": "markdown content here"\n'
        f"}}"
    )

    completion = client.chat.completions.create(
        model="llama2-70b-4096",   # ✅ Use this stable model
        messages=[
            {"role": "system", "content": "You generate structured JSON blog posts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    raw_output = completion.choices[0].message.content.strip()

    print("\n=== RAW MODEL OUTPUT ===\n", raw_output)

    try:
        blog = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print("\n=== JSON DECODE ERROR ===\n", str(e))
        raise HTTPException(status_code=500, detail=f"Invalid JSON from model: {raw_output}")

    return blog
