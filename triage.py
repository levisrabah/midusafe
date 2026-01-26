import os
from google import genai
from dotenv import load_dotenv
# 1. Load environment variables from a .env file
load_dotenv()

# 2. Initialize the client EXPLICITLY for Gemini Developer API (AI Studio)
# vertexai=False tells the SDK to use your AI Studio API key, not a Google Cloud account.
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    vertexai=False 
)

def analyze_report(text):
    prompt = f"""
    You are Midusafe AI, an emergency response triage system specializing in East Africa. 
    Analyze this report: '{text}'
    
    Focus on geographical context within East Africa (Kenya, Uganda, Tanzania, Rwanda, Burundi, South Sudan, Somalia, Ethiopia).
    
    Return ONLY a JSON object with:
    - 'urgency': (1-10, where 10 is most critical)
    - 'type': (flood, drought, landslide, storm, erosion, heatwave, disease_outbreak, or other)
    - 'summary': (one short sentence specific to East African context)
    - 'location_lat': (accurate latitude for the East African location, decimal)
    - 'location_lng': (accurate longitude for the East African location, decimal)
    - 'confidence': (0.0 to 1.0 confidence score in your analysis)
    
    Consider regional infrastructure, climate patterns, and local geography in your assessment.
    """
    
    try:
        # 3. Generate content using the Gemini model
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
#Test the function
if __name__ == "__main__":
    test_report = "Help! There is massive flooding on Main St and the water is rising fast!"
    print("--- Midusafe Triage Result ---")
    print(analyze_report(test_report))