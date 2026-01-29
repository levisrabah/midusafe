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
    You are a Universal Emergency Response AI specializing in multilingual disaster triage for Kenya and East Africa.
    You must support ALL languages including English, Swahili, Sheng, Dholuo, Kalenjin, Gikuyu, Luhya, Somali, French, Arabic, and any other language.
    
    Analyze this report: '{text}'
    
    CRITICAL REQUIREMENTS:
    1. Universal Language Detection: Auto-detect ANY language (including code-switching where people mix multiple languages)
    2. Dialect Identification: If it's a Kenyan dialect, label it specifically (e.g., 'Native: Kalenjin', 'Native: Gikuyu')
    3. Code-Switching Handling: Handle mixed-language sentences (e.g., "Moto imekuwa serious, watu wanarun tao")
    4. English Translation: Always provide English translation for the Command Center
    5. Cultural Context: Extract cultural terms like 'Boma', 'Shamba', 'Stage', 'Mtaa', 'Madhuka', 'Gichagi', 'Chunk'
    6. Geospatial Intelligence: Use Kenyan place names for precise location mapping
    
    Return ONLY a JSON object with:
    - 'detected_language': (auto-detected language code - en, sw, sh, luo, kal, kik, luh, som, fr, ar, or 'native:[dialect_name]')
    - 'detected_language_label': (full language name - 'English', 'Swahili', 'Sheng', 'Dholuo', 'Native: Kalenjin', 'Native: Gikuyu', etc.)
    - 'original_text': (the exact input text received)
    - 'translated_summary': (English translation for dashboard)
    - 'cultural_context': (brief explanation of local terms and their significance)
    - 'urgency': (1-10, where 10 is most critical)
    - 'type': (flood, fire, structural_collapse, drought, industrial_accident, gas_leak, landslide, storm, erosion, heatwave, disease_outbreak, or other)
    - 'summary': (one short sentence incorporating cultural context)
    - 'location_lat': (accurate latitude for the Kenyan location, decimal)
    - 'location_lng': (accurate longitude for the Kenyan location, decimal)
    - 'confidence': (0.0 to 1.0 confidence score in your analysis)
    
    Consider Kenyan infrastructure, local geography, cultural significance, and regional emergency patterns.
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