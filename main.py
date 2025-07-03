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

def clean_and_extract_json(text):
    """Extract and clean JSON from AI response"""
    # Remove code fences
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()
    
    # Find JSON object boundaries
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1:
        return None
    
    json_str = text[start:end+1]
    
    # Clean up common JSON issues
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)  # Remove control characters
    json_str = re.sub(r'(?<!\\)"(?![,}\]\s])', '\\"', json_str)  # Escape unescaped quotes
    
    return json_str

def generate_blog_content(topic, tone, audience):
    """Generate blog using AI with multiple retry attempts"""
    
    # Simplified prompt for better JSON generation
    prompt = f"""Generate a blog post about "{topic}" with a {tone.lower()} tone for {audience}.

Return ONLY valid JSON with this structure:
{{
  "title": "Blog title here",
  "meta_description": "Description under 160 characters",
  "tags": "tag1, tag2, tag3, tag4, tag5",
  "body": "# Title\\n\\nIntroduction paragraph...\\n\\n## Section 1\\n\\nContent...\\n\\n## Section 2\\n\\nContent...\\n\\n## Conclusion\\n\\nConclusion paragraph..."
}}

Make the body at least 500 words with proper markdown formatting."""

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a blog writer. Respond ONLY with valid JSON. Do not include any text outside the JSON object."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        raw_response = completion.choices[0].message.content.strip()
        print(f"Raw AI Response: {raw_response[:200]}...")
        
        # Extract and clean JSON
        json_str = clean_and_extract_json(raw_response)
        
        if not json_str:
            raise ValueError("No valid JSON found in response")
            
        # Parse JSON
        blog_data = json.loads(json_str)
        
        # Validate required fields
        required_fields = ["title", "meta_description", "tags", "body"]
        for field in required_fields:
            if field not in blog_data or not blog_data[field]:
                raise ValueError(f"Missing or empty field: {field}")
        
        return blog_data
        
    except Exception as e:
        print(f"AI generation failed: {str(e)}")
        raise e

def create_fallback_blog(topic, tone, audience):
    """Create a structured fallback blog when AI fails"""
    
    tone_intros = {
        "informative": "This comprehensive guide provides essential information about",
        "friendly": "Hey there! Let's dive into everything you need to know about",
        "motivational": "Ready to transform your approach to",
        "professional": "This detailed analysis examines the key aspects of",
        "casual": "So you want to know more about"
    }
    
    intro = tone_intros.get(tone.lower(), "Let's explore")
    
    # Create more detailed fallback content
    body_content = f"""# {topic}

{intro} {topic.lower()}.

## Understanding {topic}

{topic} has become increasingly important in today's world. Whether you're a beginner or looking to deepen your knowledge, this guide will provide valuable insights.

## Key Benefits

Here are the main advantages of focusing on {topic.lower()}:

- **Enhanced Performance**: Implementing best practices can significantly improve your results
- **Better Understanding**: Gaining deeper insights helps you make informed decisions  
- **Practical Application**: Real-world applications that you can implement immediately
- **Long-term Success**: Building a foundation for sustained growth and improvement

## Getting Started

To begin your journey with {topic.lower()}, consider these essential steps:

1. **Research and Planning**: Take time to understand the fundamentals
2. **Set Clear Goals**: Define what you want to achieve
3. **Start Small**: Begin with manageable steps and gradually expand
4. **Track Progress**: Monitor your development and adjust as needed

## Best Practices

Successful implementation of {topic.lower()} strategies requires attention to several key areas:

### Planning and Strategy
Develop a comprehensive approach that aligns with your objectives and timeline.

### Implementation
Focus on consistent execution while remaining flexible enough to adapt when necessary.

### Monitoring and Adjustment
Regular evaluation helps ensure you're on the right track and making progress.

## Common Challenges and Solutions

Many people face similar obstacles when dealing with {topic.lower()}. Here are some common challenges and how to overcome them:

- **Time Management**: Prioritize tasks and create realistic schedules
- **Resource Allocation**: Make the most of available resources while identifying areas for improvement
- **Consistency**: Develop sustainable habits that support long-term success

## Conclusion

{topic} represents an important area of focus for {audience.lower()}. By understanding the fundamentals, implementing best practices, and maintaining consistency, you can achieve meaningful results.

Remember that success in {topic.lower()} is a journey, not a destination. Stay committed to continuous learning and improvement, and you'll see progress over time."""

    return {
        "title": f"Complete Guide to {topic}: Everything You Need to Know",
        "meta_description": f"Discover essential strategies and insights about {topic}. A comprehensive guide for {audience.lower()} to achieve better results.",
        "tags": f"{topic.lower()}, guide, tips, strategies, {audience.lower()}",
        "body": body_content
    }

@app.post("/generate")
async def generate_blog(data: BlogRequest):
    try:
        # First try AI generation
        blog_data = generate_blog_content(data.topic, data.tone, data.audience)
        print("✅ AI generation successful")
        return blog_data
        
    except Exception as ai_error:
        print(f"❌ AI generation failed: {str(ai_error)}")
        
        # Fallback to template
        print("🔄 Using fallback content generation")
        blog_data = create_fallback_blog(data.topic, data.tone, data.audience)
        return blog_data

@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "AI Blog Writer API is running"}

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}