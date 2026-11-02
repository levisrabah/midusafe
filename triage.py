import os
from dotenv import load_dotenv
from urgency_intelligence import calculate_urgency_score
# 1. Load environment variables from a .env file
load_dotenv()

# 2. Import the Gemini SDK only if installed (requirements-legacy.txt).
# Without it, analyze_report() returns a degraded fallback instead of crashing.
try:
    from google import genai
except ImportError:
    genai = None

# Initialize the client EXPLICITLY for Gemini Developer API (AI Studio)
# vertexai=False tells the SDK to use your AI Studio API key, not a Google Cloud account.
client = None
if genai is not None:
    try:
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            vertexai=False
        )
    except Exception as e:
        print(f"Gemini client init failed, legacy triage degraded: {e}")
        client = None

TRIAGE_AVAILABLE = client is not None


def _degraded_response(text, note):
    """Valid fallback payload when Gemini is unavailable (missing SDK/key)."""
    intelligent_urgency = calculate_urgency_score(text)
    return f"""{{
        "original_text": "{text}",
        "detected_language": "en",
        "english_summary": "Legacy triage degraded: {note}",
        "urgency_score": {intelligent_urgency},
        "suggested_actions": "Manual review required for this report",
        "cultural_context": "Legacy Gemini path unavailable",
        "disaster_type": "other",
        "location_lat": 0.0,
        "location_lng": 0.0,
        "confidence": 0.1,
        "degraded": true,
        "error": "{note}"
    }}"""

def analyze_report(text):
    if not TRIAGE_AVAILABLE:
        return _degraded_response(
            text, "Gemini SDK not installed (pip install -r requirements-legacy.txt)")
    prompt = f"""
    You are a Pan-African Crisis Dispatcher specializing in multilingual disaster triage across the entire African continent.
    You must support ALL languages including Sheng, Swahili, Dholuo, Amharic, French, Portuguese, Arabic, Hausa, Yoruba, Igbo, Zulu, Xhosa, Afrikaans, Somali, Amharic, Tigrinya, Oromo, Wolof, and any other African language or dialect.
    
    Analyze this report: '{text}'
    
    CRITICAL REQUIREMENTS:
    1. Universal Language Detection: Auto-detect ANY language (including code-switching where people mix multiple languages)
    2. Dialect Identification: Label specific dialects (e.g., 'Sheng', 'Dholuo', 'Amharic', 'Hausa', 'Yoruba', 'Zulu', 'Portuguese', 'French')
    3. Code-Switching Handling: Handle mixed-language sentences (e.g., "Moto umekuwa serious, watu wanarun tao")
    4. English Translation: Always provide professional English translation for the Command Center
    5. Cultural Context: Extract cultural terms and geographical references specific to each region
    6. Geospatial Intelligence: Use African place names for precise location mapping across all countries
    
    Return ONLY a JSON object with:
    - 'original_text': (the exact input text received)
    - 'detected_language': (auto-detected language code - en, sw, sh, luo, am, fr, pt, ar, ha, yo, ig, zu, xh, af, so, ti, om, wo, or 'native:[dialect_name]')
    - 'english_summary': (professional English translation for dashboard)
    - 'urgency_score': (1-10 based on immediate threat to life, where 10 is most critical)
    - 'suggested_actions': (AI-generated next steps, e.g., "Dispatch Red Cross to Kisumu Sector 4")
    - 'cultural_context': (brief explanation of local terms and their significance)
    - 'disaster_type': (flood, fire, structural_collapse, drought, industrial_accident, gas_leak, landslide, storm, erosion, heatwave, disease_outbreak, locust_invasion, volcanic_activity, coastal_erosion, or other)
    - 'location_lat': (accurate latitude for the African location, decimal)
    - 'location_lng': (accurate longitude for the African location, decimal)
    - 'confidence': (0.0 to 1.0 confidence score in your analysis)
    
    Consider African infrastructure, local geography, cultural significance, and regional emergency patterns across all 54 African nations.
    """
    
    try:
        # 3. Generate content using the Gemini model with timeout
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("AI call timed out")
        
        # Set 5 second timeout for AI call
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt
            )
        finally:
            signal.alarm(0)  # Cancel alarm
        
        # Validate response before returning
        if not response.text or response.text.strip() == "":
            raise ValueError("Empty response from AI model")
            
        return response.text
    except TimeoutError:
        # Return quick fallback response with intelligent urgency
        intelligent_urgency = calculate_urgency_score(text)
        return f"""{{
            "original_text": "{text}",
            "detected_language": "en",
            "english_summary": "Emergency report received - AI processing delayed",
            "urgency_score": {intelligent_urgency},
            "suggested_actions": "Manual review required",
            "cultural_context": "AI processing timeout",
            "disaster_type": "other",
            "location_lat": 0.0,
            "location_lng": 0.0,
            "confidence": 0.1,
            "timeout": true
        }}"""
    except Exception as e:
        # Return structured error response with intelligent urgency
        intelligent_urgency = calculate_urgency_score(text)
        error_response = f"""{{
            "original_text": "{text}",
            "detected_language": "en",
            "english_summary": "AI processing temporarily unavailable - using fallback analysis",
            "urgency_score": {intelligent_urgency},
            "suggested_actions": "Manual review required for this report",
            "cultural_context": "Unable to process due to technical issues",
            "disaster_type": "other",
            "location_lat": 0.0,
            "location_lng": 0.0,
            "confidence": 0.1,
            "error": "{str(e)}"
        }}"""
        return error_response
#Test the function
if __name__ == "__main__":
    test_report = "Help! There is massive flooding on Main St and the water is rising fast!"
    print("--- Midusafe Triage Result ---")
    print(analyze_report(test_report))