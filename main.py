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

def clean_json_string(json_str):
    """Clean the JSON string to remove invalid control characters"""
    # Remove any leading/trailing whitespace and code fences
    json_str = json_str.strip()
    
    if json_str.startswith("```json"):
        json_str = json_str.replace("```json", "").strip()
    if json_str.endswith("```"):
        json_str = json_str[:-3].strip()
    if json_str.startswith("```"):
        json_str = json_str[3:].strip()
    
    # Replace invalid control characters (except for \n, \r, \t which are valid in JSON strings)
    # This regex keeps valid JSON escape sequences but removes invalid control chars
    json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', json_str)
    
    return json_str

def extract_json_from_text(text):
    """Extract JSON from text that might contain other content"""
    # Try to find JSON block between curly braces
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return text[start_idx:end_idx + 1]
    return text

@app.post("/generate")
async def generate_blog(data: BlogRequest):
    prompt = (
        f"You are a helpful assistant that generates blog content.\n"
        f"Generate a complete, high-quality SEO blog post and format your response as valid JSON.\n\n"
        f"Requirements:\n"
        f"- Write a compelling title\n"
        f"- Create a meta description (max 160 characters)\n"
        f"- Provide 5 comma-separated SEO tags\n"
        f"- Write a body with at least 500 words using Markdown formatting\n"
        f"- Use proper headings (## for main sections)\n\n"
        f"Topic: {data.topic}\n"
        f"Tone: {data.tone}\n"
        f"Audience: {data.audience}\n\n"
        f"Respond with ONLY valid JSON in this exact format:\n"
        f'{{\n'
        f'  "title": "Your blog title here",\n'
        f'  "meta_description": "Your meta description here",\n'
        f'  "tags": "tag1, tag2, tag3, tag4, tag5",\n'
        f'  "body": "Your markdown content here with proper escaping"\n'
        f'}}\n\n'
        f"Important: Ensure all quotes and special characters in the JSON are properly escaped."
    )

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a professional blog writer that responds with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=2000  # Increased token limit
        )

        raw_output = completion.choices[0].message.content.strip()
        print("\n=== RAW MODEL OUTPUT ===\n", raw_output)

        # Clean and extract JSON
        cleaned_output = clean_json_string(raw_output)
        json_content = extract_json_from_text(cleaned_output)
        
        print("\n=== CLEANED JSON ===\n", json_content)

        # Parse JSON
        try:
            blog = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"\n=== JSON DECODE ERROR ===\n{str(e)}")
            print(f"=== PROBLEMATIC JSON ===\n{json_content}")
            
            # Fallback: Create a manual blog response
            blog = {
                "title": f"Guide to {data.topic}",
                "meta_description": f"Discover essential insights about {data.topic} in this comprehensive guide.",
                "tags": f"{data.topic.lower()}, guide, tips, advice, {data.audience.lower()}",
                "body": f"# {data.topic}\n\nThis comprehensive guide covers everything you need to know about {data.topic}.\n\n## Introduction\n\nIn today's world, understanding {data.topic} is crucial for {data.audience}.\n\n## Key Points\n\n- Important aspect 1\n- Important aspect 2\n- Important aspect 3\n\n## Conclusion\n\nWe hope this guide helps you with {data.topic}."
            }
            
            print("\n=== USING FALLBACK CONTENT ===")

        # Validate the required fields
        required_fields = ["title", "meta_description", "tags", "body"]
        for field in required_fields:
            if field not in blog:
                blog[field] = f"Default {field}"

        return blog

    except Exception as e:
        print(f"\n=== GENERAL ERROR ===\n{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating blog: {str(e)}"
        )

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "AI Blog Writer API is running"}

# Test endpoint
@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}