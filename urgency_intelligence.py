import re
from typing import Dict, List, Tuple

class UrgencyIntelligence:
    """
    Intelligent urgency scoring system for disaster reports.
    Uses keyword analysis, disaster type classification, and contextual factors
    to determine realistic urgency scores instead of defaulting to 5/10.
    """
    
    def __init__(self):
        # Critical urgency keywords (9-10/10)
        self.critical_keywords = [
            # Life-threatening situations
            'trapped', 'stuck', 'buried', 'collapsed', 'collapse', 'crushed',
            'drowning', 'suffocating', 'cannot breathe', 'dying', 'killed',
            'casualties', 'fatalities', 'multiple deaths', 'mass casualties',
            
            # Immediate danger
            'explosion', 'exploded', 'blast', 'toxic', 'poison', 'chemical',
            'gas leak', 'radiation', 'contaminated', 'hazardous',
            
            # Infrastructure failure
            'building collapsed', 'bridge collapsed', 'dam failure', 'broken dam',
            'structural failure', 'evacuation radius', 'immediate evacuation',
            
            # Scale indicators
            'hundreds', 'thousands', 'entire village', 'whole town', 'city-wide',
            'widespread', 'catastrophic', 'devastating', 'unprecedented'
        ]
        
        # High urgency keywords (7-8/10)
        self.high_keywords = [
            # Serious injuries
            'injured', 'hurt', 'bleeding', 'broken', 'fractured', 'wounded',
            'hospital', 'medical emergency', 'ambulance', 'rescue needed',
            
            # Dangerous situations
            'fire', 'burning', 'flames', 'smoke', 'flooding', 'flood',
            'flash flood', 'rising water', 'overflow', 'submerged',
            
            # Infrastructure damage
            'destroyed', 'damaged', 'washed away', 'roads closed', 'bridge out',
            'power outage', 'electricity', 'communication down',
            
            # Weather emergencies
            'hurricane', 'cyclone', 'tornado', 'severe storm', 'extreme',
            'emergency declared', 'state of emergency'
        ]
        
        # Medium urgency keywords (5-6/10)
        self.medium_keywords = [
            # Disruptions
            'stranded', 'stuck', 'isolated', 'cut off', 'blocked',
            'delayed', 'disrupted', 'suspended', 'closed',
            
            # Environmental issues
            'heavy rain', 'strong winds', 'erosion', 'landslide', 'mudslide',
            'drought', 'water shortage', 'food shortage', 'crop damage',
            
            # Public health
            'outbreak', 'disease', 'contamination', 'pollution', 'health risk',
            
            # Scale indicators
            'dozens', 'many', 'several', 'numerous', 'significant'
        ]
        
        # Low urgency keywords (3-4/10)
        self.low_keywords = [
            # Minor issues
            'minor', 'small', 'localized', 'limited', 'partial',
            'monitoring', 'watching', 'observing', 'assessing',
            
            # Preparations
            'preparing', 'getting ready', 'warning', 'advisory', 'alert',
            'precaution', 'preventive', 'planning'
        ]
        
        # Disaster type urgency mapping
        self.disaster_urgency_map = {
            'structural_collapse': 10,
            'industrial_accident': 9,
            'industrial_fire': 9,
            'gas_leak': 8,
            'flash_flood': 8,
            'landslide': 8,
            'earthquake': 9,
            'volcanic_activity': 8,
            'wildfire': 8,
            'flood': 7,
            'storm': 7,
            'heatwave': 6,
            'drought': 5,
            'disease_outbreak': 6,
            'locust_invasion': 6,
            'coastal_erosion': 5,
            'other': 4
        }
        
        # Location urgency modifiers (urban areas get higher scores)
        self.high_population_locations = [
            'nairobi', 'mombasa', 'kisumu', 'nakuru', 'eldoret',
            'thika', 'kitui', 'garissa', 'kakuma', 'dadaab',
            'lagos', 'accra', 'abidjan', 'dakar', 'johannesburg',
            'cape town', 'durban', 'addis ababa', 'kampala', 'kigali',
            'dar es salaam', 'harare', 'lusaka', 'maputo', 'antananarivo'
        ]
        
        # African languages urgency boosters (emergency words)
        self.emergency_words = {
            'swahili': ['dharura', 'haraka', 'msaada', 'hatari', 'kimbilio'],
            'sheng': ['kazana', 'noma', 'mbaya', 'msiba', 'tatizo'],
            'dholuo': ['mar chike', 'dhiang\'o', 'mos', 'timmer', 'wacho'],
            'kikuyu': ['urimi', 'muthiru', 'mena', 'thiinĩ', 'mũgambo'],
            'kalenjin': ['kony', 'teng', 'chemasir', 'konyit', 'tongit'],
            'hausa': ['gaggãwa', 'gaggãri', 'tashi', 'gaggãra', 'bala'],
            'yoruba': ['pànipàní', 'ìpaniláyà', 'wàhálà', 'bànjẹ', 'sákità'],
            'igbo': ['ịsị', 'ọjọọ', 'nsogbu', 'gbagọrọagbagọrọ', 'mba'],
            'amharic': ['አደጋ', 'ወሰኒ', 'ስጋ', 'ሞት', 'እሳት'],
            'arabic': ['طوارئ', 'خطر', 'مساعدة', 'كارثة', 'موت'],
            'french': ['urgence', 'danger', 'aide', 'catastrophe', 'mort'],
            'portuguese': ['emergência', 'perigo', 'ajuda', 'catástrofe', 'morte']
        }
    
    def calculate_urgency_score(self, text: str, disaster_type: str = None, location: str = None) -> int:
        """
        Calculate urgency score based on text analysis, disaster type, and location.
        Returns score from 1-10.
        """
        text_lower = text.lower()
        base_score = 5  # Start with medium urgency
        
        # 1. Keyword analysis
        keyword_score = self._analyze_keywords(text_lower)
        
        # 2. Disaster type scoring
        disaster_score = self._get_disaster_score(disaster_type)
        
        # 3. Location modifier
        location_modifier = self._get_location_modifier(location)
        
        # 4. African language emergency words
        language_boost = self._detect_emergency_words(text_lower)
        
        # 5. Contextual factors
        context_modifier = self._analyze_context(text_lower)
        
        # Calculate final score with weighted components
        final_score = (
            base_score * 0.2 +           # Base score (20%)
            keyword_score * 0.4 +         # Keywords (40%)
            disaster_score * 0.2 +       # Disaster type (20%)
            location_modifier * 0.1 +     # Location (10%)
            language_boost * 0.05 +      # Language emergency words (5%)
            context_modifier * 0.05       # Context (5%)
        )
        
        # Ensure score is within bounds
        final_score = max(1, min(10, int(round(final_score))))
        
        return final_score
    
    def _analyze_keywords(self, text: str) -> float:
        """Analyze text for urgency keywords."""
        critical_count = sum(1 for keyword in self.critical_keywords if keyword in text)
        high_count = sum(1 for keyword in self.high_keywords if keyword in text)
        medium_count = sum(1 for keyword in self.medium_keywords if keyword in text)
        low_count = sum(1 for keyword in self.low_keywords if keyword in text)
        
        # Weight the counts
        weighted_score = (
            critical_count * 10 +
            high_count * 8 +
            medium_count * 6 +
            low_count * 4
        )
        
        # Normalize to 1-10 scale
        if weighted_score > 0:
            return min(10, max(1, weighted_score / max(1, critical_count + high_count + medium_count + low_count)))
        return 5  # Default to medium if no keywords found
    
    def _get_disaster_score(self, disaster_type: str) -> float:
        """Get base score for disaster type."""
        if not disaster_type:
            return 5  # Default medium
        
        return self.disaster_urgency_map.get(disaster_type.lower(), 5)
    
    def _get_location_modifier(self, location: str) -> float:
        """Get urgency modifier based on location population density."""
        if not location:
            return 0  # No modifier
        
        location_lower = location.lower()
        
        # Check for high population areas
        for high_pop_loc in self.high_population_locations:
            if high_pop_loc in location_lower:
                return 1  # Boost by 1 point
        
        # Check for urban indicators
        urban_indicators = ['city', 'town', 'urban', 'cbd', 'central', 'downtown']
        if any(indicator in location_lower for indicator in urban_indicators):
            return 0.5
        
        return 0  # No modifier
    
    def _detect_emergency_words(self, text: str) -> float:
        """Detect emergency words in African languages."""
        boost = 0
        
        for language, emergency_words in self.emergency_words.items():
            for word in emergency_words:
                if word in text:
                    boost += 0.5  # Add 0.5 for each emergency word found
        
        return min(2, boost)  # Cap at 2 points boost
    
    def _analyze_context(self, text: str) -> float:
        """Analyze contextual factors for urgency."""
        modifier = 0
        
        # Time sensitivity
        time_sensitive = ['immediately', 'urgent', 'now', 'asap', 'quickly', 'fast']
        if any(word in text for word in time_sensitive):
            modifier += 0.5
        
        # Scale indicators
        scale_indicators = ['multiple', 'many', 'widespread', 'extensive', 'massive']
        if any(word in text for word in scale_indicators):
            modifier += 0.5
        
        # Vulnerable populations
        vulnerable_groups = ['children', 'elderly', 'disabled', 'pregnant', 'patients']
        if any(word in text for word in vulnerable_groups):
            modifier += 0.5
        
        return min(2, modifier)  # Cap at 2 points
    
    def get_urgency_level(self, score: int) -> str:
        """Convert numeric score to descriptive level."""
        if score >= 9:
            return "CRITICAL"
        elif score >= 7:
            return "HIGH"
        elif score >= 5:
            return "MODERATE"
        elif score >= 3:
            return "LOW"
        else:
            return "MINIMAL"
    
    def get_urgency_color(self, score: int) -> str:
        """Get color code for urgency score."""
        if score >= 9:
            return "#DC2626"  # Red
        elif score >= 7:
            return "#EA580C"  # Orange
        elif score >= 5:
            return "#D97706"  # Amber
        elif score >= 3:
            return "#65A30D"  # Lime
        else:
            return "#059669"  # Green

# Global instance
urgency_intelligence = UrgencyIntelligence()

def calculate_urgency_score(text: str, disaster_type: str = None, location: str = None) -> int:
    """Convenience function to calculate urgency score."""
    return urgency_intelligence.calculate_urgency_score(text, disaster_type, location)
