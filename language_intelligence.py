import re
from typing import Dict, List, Optional

class LanguageIntelligence:
    """
    Enhanced language detection for African languages with code-switching support.
    """
    
    def __init__(self):
        # African language patterns
        self.language_patterns = {
            'swahili': [r'\b(na|wa|ya|la|kwa|za|mo|ku|li|vi|mi|ji|ma|pa|tu|hu|mu|bi|ki|ri|si|ti|ni|ngu|thi|cha|dhi|nya|mba|nga|ra|ka|ta|sa|ha|ja|me|ke|go|po|so|lo|vo|zo)\b'],
            'sheng': [r'\b(kazini|noma|mbaya|sasa|poa|fresh|mambo|vibe|story|ndo|bas|bro|sis|dude|chali|demu|mamii|buda|mzee|jamaa|kaka|dada|mchizi)\b'],
            'dholuo': [r'\b(pi|ni|gi|mi|di|ki|bi|ti|ri|li|wi|yi|fi|vi|si|hi|ji|chi|shi|zhi|ghi|dhi|thi|nyi|ngi|mbi|ndi|ngi|nji|nyi)\b'],
            'kikuyu': [r'\b(mũ|wa|gĩ|kĩ|thĩ|ĩrĩ|ũrĩ|mĩrĩ|thiĩ|ĩcio|ũcio|mũcio|gĩcio|kĩcio|thĩcio|ĩrĩcio|ũrĩcio|mĩrĩcio|thiĩcio)\b'],
            'kalenjin': [r'\b(ki|ka|ke|ko|ku|kem|keme|kemei|kony|konyi|teng|tengi|chem|chemi|sir|siri)\b'],
            'amharic': [r'[\u1200-\u137F]+'],  # Ethiopic script
            'hausa': [r'\b(wa|ta|na|da|ga|ma|sa|ra|ka|la|ba|fa|ya|ha|ja|za|ca|sha|dha|gha|kha|tsa)\b'],
            'yoruba': [r'\b(ní|kí|kò|jẹ́|jẹ|kí|kò|ní|kí|kò|jẹ́|jẹ|kí|kò|ní)\b'],
            'igbo': [r'\b(ka|na|na-eme|bụ|ịbụ|mà|bụrụ|dị|ọ́bụ́la|nke|na|gbasara|n\'ịhụ|n\'anya|bụ|ụzọ|bịa|nwere|ike|ịga|n\'ihu|bụ|otu|n\'ime|nke|a)\b'],
            'arabic': [r'[\u0600-\u06FF]+'],  # Arabic script
            'french': [r'\b(le|la|les|de|du|des|à|au|aux|un|une|des|et|est|dans|pour|sur|avec|par|sous|vers|chez|entre|pendant|depuis|jusqu|selon|malgré|sans|parmi|contre|pendant|depuis|vers|chez|entre|pendant|depuis|jusqu|selon|malgré|sans|parmi|contre)\b'],
            'portuguese': [r'\b(o|a|os|as|de|do|da|dos|das|em|no|na|nos|nas|por|pelo|pela|pelos|pelas|com|sem|para|pela|pelo|pelos|pelas|como|quando|onde|porque|porquê|porquê|porquê)\b']
        }
        
        # Emergency words by language
        self.emergency_words = {
            'swahili': ['dharura', 'haraka', 'msaada', 'hatari', 'kimbilio', 'tatizo', 'ajiri', 'okoa'],
            'sheng': ['kazana', 'noma', 'mbaya', 'msiba', 'tatizo', 'kazini', 'emergency', 'help'],
            'dholuo': ['mar chike', 'dhiang\'o', 'mos', 'timmer', 'wacho', 'kony', 'teng', 'ok'],
            'kikuyu': ['urimi', 'muthiru', 'mena', 'thiinĩ', 'mũgambo', 'ũhoro', 'ũrĩmĩ'],
            'kalenjin': ['kony', 'teng', 'chemasir', 'konyit', 'tongit', 'emis', 'chemasir'],
            'hausa': ['gaggãwa', 'gaggãri', 'tashi', 'gaggãra', 'bala', 'agaji', 'ceto'],
            'yoruba': ['pànipàní', 'ìpaniláyà', 'wàhálà', 'bànjẹ', 'sákità', 'ìdínà', 'èébú'],
            'igbo': ['ịsị', 'ọjọọ', 'nsogbu', 'gbagọrọagbagọrọ', 'mba', 'nnapụta', 'ọkụkọ'],
            'amharic': ['አደጋ', 'ወሰኒ', 'ስጋ', 'ሞት', 'እሳት', 'ስራ', 'ህመም', 'እርዳታ'],
            'arabic': ['طوارئ', 'خطر', 'مساعدة', 'كارثة', 'موت', 'إسعاف', 'نجدة', 'حريق'],
            'french': ['urgence', 'danger', 'aide', 'catastrophe', 'mort', 'secours', 'incendie', 'accident'],
            'portuguese': ['emergência', 'perigo', 'ajuda', 'catástrofe', 'morte', 'socorro', 'incêndio', 'acidente']
        }
        
        # Code-switching patterns (mixed languages)
        self.code_switching_patterns = [
            r'\b\w+(?:\s+\w+){0,2}\s+(?:na|wa|kwa|la|za|mo|ku|li|vi|mi|ji|ma|pa|tu|hu|mu|bi|ki|ri|si|ti|ni|ngu|thi|cha|dhi|nya|mba|nga|ra|ka|ta|sa|ha|ja|me|ke|go|po|so|lo|vo|zo)\b',
            r'\b(?:kazini|noma|mbaya|sasa|poa|fresh|mambo|vibe|story|ndo|bas|bro|sis|dude|chali|demu|mamii|buda|mzee|jamaa|kaka|dada|mchizi)\s+\w+\b',
            r'\b\w+\s+(?:pi|ni|gi|mi|di|ki|bi|ti|ri|li|wi|yi|fi|vi|si|hi|ji|chi|shi|zhi|ghi|dhi|thi|nyi|ngi|mbi|ndi|ngi|nji|nyi)\b'
        ]
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect language with confidence scores and code-switching detection.
        """
        text_lower = text.lower()
        detected_languages = {}
        
        # Check each language pattern
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                detected_languages[language] = score
        
        # Check for code-switching
        code_switching_score = 0
        for pattern in self.code_switching_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            code_switching_score += len(matches)
        
        # Determine primary language
        if detected_languages:
            primary_language = max(detected_languages, key=detected_languages.get)
            confidence = min(1.0, detected_languages[primary_language] / 10.0)
        else:
            primary_language = 'english'
            confidence = 0.5
        
        # Detect emergency words
        emergency_detected = False
        emergency_language = None
        
        for language, words in self.emergency_words.items():
            for word in words:
                if word in text_lower:
                    emergency_detected = True
                    emergency_language = language
                    break
            if emergency_detected:
                break
        
        return {
            'primary_language': primary_language,
            'confidence': confidence,
            'all_detected': detected_languages,
            'code_switching': code_switching_score > 0,
            'code_switching_score': code_switching_score,
            'emergency_detected': emergency_detected,
            'emergency_language': emergency_language,
            'language_code': self._get_language_code(primary_language)
        }
    
    def _get_language_code(self, language: str) -> str:
        """Convert language name to ISO code."""
        language_codes = {
            'english': 'en',
            'swahili': 'sw',
            'sheng': 'sh',
            'dholuo': 'luo',
            'kikuyu': 'ki',
            'kalenjin': 'kl',
            'amharic': 'am',
            'hausa': 'ha',
            'yoruba': 'yo',
            'igbo': 'ig',
            'arabic': 'ar',
            'french': 'fr',
            'portuguese': 'pt'
        }
        return language_codes.get(language, 'en')
    
    def get_language_display_name(self, language_code: str) -> str:
        """Get display name for language code."""
        display_names = {
            'en': 'English',
            'sw': 'Swahili',
            'sh': 'Sheng',
            'luo': 'Dholuo',
            'ki': 'Kikuyu',
            'kl': 'Kalenjin',
            'am': 'Amharic',
            'ha': 'Hausa',
            'yo': 'Yoruba',
            'ig': 'Igbo',
            'ar': 'Arabic',
            'fr': 'French',
            'pt': 'Portuguese'
        }
        return display_names.get(language_code, 'English')
    
    def get_language_flag(self, language_code: str) -> str:
        """Get flag emoji for language."""
        flags = {
            'en': '🇬🇧',
            'sw': '🇰🇪',
            'sh': '🇰🇪',
            'luo': '🇰🇪',
            'ki': '🇰🇪',
            'kl': '🇰🇪',
            'am': '🇪🇹',
            'ha': '🇳🇬',
            'yo': '🇳🇬',
            'ig': '🇳🇬',
            'ar': '🇸🇦',
            'fr': '🇫🇷',
            'pt': '🇵🇹'
        }
        return flags.get(language_code, '🇬🇧')

# Global instance
language_intelligence = LanguageIntelligence()

def detect_language_enhanced(text: str) -> Dict[str, any]:
    """Convenience function for enhanced language detection."""
    return language_intelligence.detect_language(text)
