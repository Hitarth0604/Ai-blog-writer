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
        f"You are a helpful assistant that always responds ONLY with valid JSON without markdown formatting or extra commentary.\n\n"
        f"Generate a blog post in this exact JSON format:\n\n"
        f'{{\n'
        f'  "title": "string",\n'
        f'  "meta_description": "string",\n'
        f'  "tags": "tag1, tag2, tag3",\n'
        f'  "body": "string"\n'
        f'}}\n\n'
        f"Topic: {data.topic}\n"
        f"Tone: {data.tone}\n"
        f"Audience: {data.audience}\n\n"
        f"Respond ONLY with JSON."
    )

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You generate structured JSON blog posts without any commentary or formatting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw_output = completion.choices[0].message.content.strip()

    print("\n=== RAW MODEL OUTPUT ===\n", raw_output)

    try:
        blog = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print("\n=== JSON DECODE ERROR ===\n", str(e))
        raise HTTPException(status_code=500, detail=f"Invalid JSON from model. Raw output: {raw_output}")

    return blog
