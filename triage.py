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
    You are a Kenyan Emergency Expert specializing in multilingual disaster response. 
    You must support English, Swahili, Sheng, and Dholuo languages.
    
    Analyze this report: '{text}'
    
    REQUIREMENTS:
    1. Language Detection: Identify if the input is English, Swahili, Sheng, or Dholuo
    2. Cultural Context: Extract cultural terms like 'Boma', 'Shamba', 'Stage', 'Mtaa', 'Madhuka' and explain their significance
    3. Geospatial Intelligence: Use local place names to pinpoint exact locations in Kenya
    4. Translation: Provide English translation for dashboard display
    
    Return ONLY a JSON object with:
    - 'detected_language': (english, swahili, sheng, dholuo)
    - 'original_text': (the exact input text received)
    - 'translated_summary': (English translation for dashboard)
    - 'cultural_context': (brief explanation of local terms and their significance)
    - 'urgency': (1-10, where 10 is most critical)
    - 'type': (flood, fire, structural_collapse, drought, industrial_accident, gas_leak, or other)
    - 'summary': (one short sentence incorporating cultural context)
    - 'location_lat': (accurate latitude for the Kenyan location, decimal)
    - 'location_lng': (accurate longitude for the Kenyan location, decimal)
    - 'confidence': (0.0 to 1.0 confidence score in your analysis)
    
    Consider Kenyan infrastructure, local geography, and cultural significance in your assessment.
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