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
    You are Midusafe AI, an emergency response triage system. 
    Analyze this report: '{text}'
    
    Return ONLY a JSON object with:
    - 'urgency': (1-10)
    - 'type': (flood, fire, medical, or other)
    - 'summary': (one short sentence)
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