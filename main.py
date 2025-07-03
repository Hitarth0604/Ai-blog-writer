from fastapi import FastAPI
from pydantic import BaseModel
from groq import OpenAI
import os

# Initialize Groq client
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

class BlogRequest(BaseModel):
    topic: str
    tone: str
    audience: str

@app.post("/generate")
async def generate_blog(data: BlogRequest):
    # Build prompt to get structured output
    prompt = (
        f"You are a helpful AI blog writer.\n\n"
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

    # Call Groq API
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You generate structured JSON blog posts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # Extract model output
    raw_output = completion.choices[0].message.content.strip()

    # For debugging:
    print("\n=== RAW MODEL OUTPUT ===\n", raw_output)

    # Safely parse JSON
    import json
    blog = json.loads(raw_output)

    return blog
