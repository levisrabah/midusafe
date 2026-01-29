from enum import Enum
from typing import Dict, List, Tuple
import math

class DisasterSeverity(Enum):
    """Enhanced disaster severity classification with African context."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    MINIMAL = "MINIMAL"

class DisasterCategory(Enum):
    """African disaster categories with local relevance."""
    CLIMATE = "CLIMATE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    HEALTH = "HEALTH"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    SOCIAL = "SOCIAL"
    ECONOMIC = "ECONOMIC"

class DisasterSeverityClassifier:
    """
    Unique disaster severity classification system for African contexts.
    Combines multiple factors for comprehensive severity assessment.
    """
    
    def __init__(self):
        # Disaster type to category mapping
        self.disaster_categories = {
            'flood': DisasterCategory.CLIMATE,
            'flash_flood': DisasterCategory.CLIMATE,
            'drought': DisasterCategory.CLIMATE,
            'heatwave': DisasterCategory.CLIMATE,
            'storm': DisasterCategory.CLIMATE,
            'cyclone': DisasterCategory.CLIMATE,
            'hurricane': DisasterCategory.CLIMATE,
            'tornado': DisasterCategory.CLIMATE,
            
            'structural_collapse': DisasterCategory.INFRASTRUCTURE,
            'industrial_accident': DisasterCategory.INFRASTRUCTURE,
            'industrial_fire': DisasterCategory.INFRASTRUCTURE,
            'gas_leak': DisasterCategory.INFRASTRUCTURE,
            'bridge_collapse': DisasterCategory.INFRASTRUCTURE,
            'dam_failure': DisasterCategory.INFRASTRUCTURE,
            
            'disease_outbreak': DisasterCategory.HEALTH,
            'medical': DisasterCategory.HEALTH,
            'epidemic': DisasterCategory.HEALTH,
            'pandemic': DisasterCategory.HEALTH,
            
            'landslide': DisasterCategory.ENVIRONMENTAL,
            'volcanic_activity': DisasterCategory.ENVIRONMENTAL,
            'earthquake': DisasterCategory.ENVIRONMENTAL,
            'wildfire': DisasterCategory.ENVIRONMENTAL,
            'coastal_erosion': DisasterCategory.ENVIRONMENTAL,
            
            'locust_invasion': DisasterCategory.SOCIAL,
            'food_shortage': DisasterCategory.SOCIAL,
            'civil_unrest': DisasterCategory.SOCIAL,
            'displacement': DisasterCategory.SOCIAL,
            
            'economic_crisis': DisasterCategory.ECONOMIC,
            'market_crash': DisasterCategory.ECONOMIC,
            'supply_chain_disruption': DisasterCategory.ECONOMIC
        }
        
        # Base severity scores for disaster types
        self.base_severity_scores = {
            'structural_collapse': 9.5,
            'industrial_accident': 9.0,
            'industrial_fire': 8.5,
            'dam_failure': 9.0,
            'gas_leak': 8.0,
            'flash_flood': 8.0,
            'landslide': 8.0,
            'earthquake': 9.0,
            'volcanic_activity': 8.0,
            'cyclone': 8.5,
            'wildfire': 8.0,
            'flood': 7.0,
            'storm': 7.0,
            'disease_outbreak': 7.0,
            'heatwave': 6.0,
            'drought': 5.5,
            'locust_invasion': 6.0,
            'coastal_erosion': 5.0,
            'other': 4.0
        }
        
        # African vulnerability factors by region
        self.regional_vulnerability = {
            'east_africa': {
                'flood': 1.3,  # High vulnerability to floods
                'drought': 1.4,  # Very high vulnerability to drought
                'locust_invasion': 1.5,
                'landslide': 1.2
            },
            'west_africa': {
                'flood': 1.2,
                'drought': 1.3,
                'disease_outbreak': 1.2,
                'coastal_erosion': 1.4
            },
            'southern_africa': {
                'drought': 1.5,
                'heatwave': 1.3,
                'wildfire': 1.2,
                'flood': 1.1
            },
            'north_africa': {
                'heatwave': 1.4,
                'drought': 1.3,
                'sandstorm': 1.5,
                'flood': 1.2
            },
            'central_africa': {
                'disease_outbreak': 1.3,
                'landslide': 1.2,
                'flood': 1.3,
                'volcanic_activity': 1.4
            }
        }
        
        # Infrastructure impact multipliers
        self.infrastructure_multipliers = {
            'severe': 1.5,
            'moderate': 1.2,
            'low': 1.0,
            'minimal': 0.8
        }
        
        # Population impact multipliers
        self.population_multipliers = {
            'high': 1.4,
            'medium': 1.2,
            'low': 1.0,
            'minimal': 0.9
        }
        
        # Seasonal adjustments (for climate disasters)
        self.seasonal_factors = {
            'rainy_season': {
                'flood': 1.3,
                'landslide': 1.2,
                'disease_outbreak': 1.1
            },
            'dry_season': {
                'drought': 1.4,
                'wildfire': 1.3,
                'heatwave': 1.2
            },
            'normal': {
                'flood': 1.0,
                'drought': 1.0,
                'wildfire': 1.0
            }
        }
    
    def classify_disaster_severity(self, 
                                 disaster_type: str,
                                 location: str = None,
                                 infrastructure_impact: str = 'moderate',
                                 affected_population: str = 'medium',
                                 season: str = 'normal',
                                 confidence: float = 0.8) -> Dict:
        """
        Comprehensive disaster severity classification.
        
        Args:
            disaster_type: Type of disaster
            location: Geographic location
            infrastructure_impact: Level of infrastructure damage
            affected_population: Population affected level
            season: Current season
            confidence: AI confidence score
        
        Returns:
            Dictionary with severity classification and metadata
        """
        # Get base severity score
        base_score = self.base_severity_scores.get(disaster_type, 4.0)
        
        # Get disaster category
        category = self.disaster_categories.get(disaster_type, DisasterCategory.SOCIAL)
        
        # Apply regional vulnerability
        regional_multiplier = self._get_regional_multiplier(disaster_type, location)
        
        # Apply infrastructure impact multiplier
        infra_multiplier = self.infrastructure_multipliers.get(infrastructure_impact, 1.0)
        
        # Apply population impact multiplier
        pop_multiplier = self.population_multipliers.get(affected_population, 1.0)
        
        # Apply seasonal factors for climate disasters
        seasonal_multiplier = self._get_seasonal_multiplier(disaster_type, season)
        
        # Calculate final severity score
        final_score = base_score * regional_multiplier * infra_multiplier * pop_multiplier * seasonal_multiplier
        
        # Apply confidence adjustment
        confidence_adjustment = 0.8 + (confidence * 0.2)  # Range: 0.8 to 1.0
        final_score *= confidence_adjustment
        
        # Ensure score is within bounds
        final_score = max(1.0, min(10.0, final_score))
        
        # Determine severity level
        severity_level = self._get_severity_level(final_score)
        
        # Calculate response priority (1-10, higher = more urgent)
        response_priority = self._calculate_response_priority(final_score, category, affected_population)
        
        # Generate severity description
        description = self._generate_severity_description(severity_level, disaster_type, category)
        
        return {
            'severity_score': round(final_score, 1),
            'severity_level': severity_level.value,
            'disaster_category': category.value,
            'response_priority': round(response_priority, 1),
            'description': description,
            'base_score': base_score,
            'regional_multiplier': regional_multiplier,
            'infrastructure_multiplier': infra_multiplier,
            'population_multiplier': pop_multiplier,
            'seasonal_multiplier': seasonal_multiplier,
            'confidence_adjustment': confidence_adjustment,
            'regional_risk_factors': self._get_regional_risk_factors(location, disaster_type),
            'recommended_actions': self._get_recommended_actions(severity_level, category),
            'estimated_duration': self._estimate_disaster_duration(disaster_type, severity_level),
            'cascade_risks': self._assess_cascade_risks(disaster_type, location, severity_level)
        }
    
    def _get_regional_multiplier(self, disaster_type: str, location: str) -> float:
        """Get regional vulnerability multiplier."""
        if not location:
            return 1.0
        
        location_lower = location.lower()
        
        # Determine region
        if any(country in location_lower for country in ['kenya', 'tanzania', 'uganda', 'rwanda', 'burundi', 'south sudan', 'ethiopia', 'somalia']):
            region = 'east_africa'
        elif any(country in location_lower for country in ['nigeria', 'ghana', 'senegal', 'mali', 'burkina faso', 'niger', 'benin', 'togo', 'cote d\'ivoire']):
            region = 'west_africa'
        elif any(country in location_lower for country in ['south africa', 'zimbabwe', 'botswana', 'namibia', 'zambia', 'mozambique', 'lesotho', 'eswatini']):
            region = 'southern_africa'
        elif any(country in location_lower for country in ['egypt', 'libya', 'tunisia', 'algeria', 'morocco', 'sudan']):
            region = 'north_africa'
        elif any(country in location_lower for country in ['drc', 'congo', 'central african republic', 'cameroon', 'gabon', 'chad', 'angola']):
            region = 'central_africa'
        else:
            return 1.0
        
        regional_factors = self.regional_vulnerability.get(region, {})
        return regional_factors.get(disaster_type, 1.0)
    
    def _get_seasonal_multiplier(self, disaster_type: str, season: str) -> float:
        """Get seasonal adjustment multiplier."""
        if disaster_type not in ['flood', 'drought', 'wildfire', 'heatwave', 'landslide', 'disease_outbreak']:
            return 1.0
        
        seasonal_factors = self.seasonal_factors.get(season, self.seasonal_factors['normal'])
        return seasonal_factors.get(disaster_type, 1.0)
    
    def _get_severity_level(self, score: float) -> DisasterSeverity:
        """Convert numeric score to severity level."""
        if score >= 9.0:
            return DisasterSeverity.CRITICAL
        elif score >= 7.0:
            return DisasterSeverity.HIGH
        elif score >= 5.0:
            return DisasterSeverity.MODERATE
        elif score >= 3.0:
            return DisasterSeverity.LOW
        else:
            return DisasterSeverity.MINIMAL
    
    def _calculate_response_priority(self, severity_score: float, category: DisasterCategory, population: str) -> float:
        """Calculate emergency response priority."""
        base_priority = severity_score
        
        # Category adjustments
        category_adjustments = {
            DisasterCategory.INFRASTRUCTURE: 1.2,
            DisasterCategory.HEALTH: 1.3,
            DisasterCategory.CLIMATE: 1.1,
            DisasterCategory.ENVIRONMENTAL: 1.0,
            DisasterCategory.SOCIAL: 1.1,
            DisasterCategory.ECONOMIC: 0.9
        }
        
        category_multiplier = category_adjustments.get(category, 1.0)
        pop_multiplier = self.population_multipliers.get(population, 1.0)
        
        priority = base_priority * category_multiplier * pop_multiplier
        return max(1.0, min(10.0, priority))
    
    def _generate_severity_description(self, severity: DisasterSeverity, disaster_type: str, category: DisasterCategory) -> str:
        """Generate human-readable severity description."""
        descriptions = {
            DisasterSeverity.CRITICAL: f"CRITICAL: {disaster_type.replace('_', ' ').title()} requires immediate emergency response. Mass casualties and widespread infrastructure damage expected.",
            DisasterSeverity.HIGH: f"HIGH: {disaster_type.replace('_', ' ').title()} poses significant threat to life and property. Rapid response essential.",
            DisasterSeverity.MODERATE: f"MODERATE: {disaster_type.replace('_', ' ').title()} requires coordinated response. Monitor for escalation.",
            DisasterSeverity.LOW: f"LOW: {disaster_type.replace('_', ' ').title()} presents limited threat. Local response adequate.",
            DisasterSeverity.MINIMAL: f"MINIMAL: {disaster_type.replace('_', ' ').title()} requires monitoring. Minimal impact expected."
        }
        
        return descriptions.get(severity, f"Severity level: {severity.value}")
    
    def _get_regional_risk_factors(self, location: str, disaster_type: str) -> List[str]:
        """Get region-specific risk factors."""
        if not location:
            return []
        
        location_lower = location.lower()
        risk_factors = []
        
        # East Africa specific risks
        if any(country in location_lower for country in ['kenya', 'tanzania', 'uganda']):
            if disaster_type == 'flood':
                risk_factors.extend(["Poor drainage systems", "Informal settlements in flood-prone areas", "Limited early warning systems"])
            elif disaster_type == 'drought':
                risk_factors.extend(["Rain-fed agriculture dependency", "Limited water storage", "High livestock dependency"])
        
        # West Africa specific risks
        elif any(country in location_lower for country in ['nigeria', 'ghana']):
            if disaster_type == 'flood':
                risk_factors.extend(["Coastal vulnerability", "Urban flooding", "Inadequate drainage"])
            elif disaster_type == 'disease_outbreak':
                risk_factors.extend(["High population density", "Limited healthcare access", "Tropical disease prevalence"])
        
        return risk_factors
    
    def _get_recommended_actions(self, severity: DisasterSeverity, category: DisasterCategory) -> List[str]:
        """Get recommended response actions."""
        actions = {
            DisasterSeverity.CRITICAL: [
                "Immediate evacuation of affected areas",
                "Deploy emergency medical teams",
                "Activate national disaster response",
                "International assistance request",
                "Establish emergency operations center"
            ],
            DisasterSeverity.HIGH: [
                "Rapid assessment teams deployment",
                "Emergency shelter preparation",
                "Medical response coordination",
                "Public emergency alerts",
                "Resource mobilization"
            ],
            DisasterSeverity.MODERATE: [
                "Local emergency services activation",
                "Community evacuation if needed",
                "Medical support readiness",
                "Damage assessment",
                "Public information updates"
            ],
            DisasterSeverity.LOW: [
                "Monitor situation closely",
                "Local response coordination",
                "Community awareness",
                "Basic medical support",
                "Resource preparation"
            ],
            DisasterSeverity.MINIMAL: [
                "Situation monitoring",
                "Community notification",
                "Standby resources",
                "Information collection",
                "Preventive measures"
            ]
        }
        
        return actions.get(severity, ["Monitor situation"])
    
    def _estimate_disaster_duration(self, disaster_type: str, severity: DisasterSeverity) -> str:
        """Estimate disaster duration based on type and severity."""
        duration_estimates = {
            'flood': {
                DisasterSeverity.CRITICAL: "2-4 weeks",
                DisasterSeverity.HIGH: "1-2 weeks",
                DisasterSeverity.MODERATE: "3-7 days",
                DisasterSeverity.LOW: "1-3 days",
                DisasterSeverity.MINIMAL: "Hours to 1 day"
            },
            'drought': {
                DisasterSeverity.CRITICAL: "6-12 months",
                DisasterSeverity.HIGH: "3-6 months",
                DisasterSeverity.MODERATE: "1-3 months",
                DisasterSeverity.LOW: "2-4 weeks",
                DisasterSeverity.MINIMAL: "1-2 weeks"
            },
            'earthquake': {
                DisasterSeverity.CRITICAL: "Weeks to months",
                DisasterSeverity.HIGH: "1-3 weeks",
                DisasterSeverity.MODERATE: "3-7 days",
                DisasterSeverity.LOW: "1-3 days",
                DisasterSeverity.MINIMAL: "Hours to 1 day"
            }
        }
        
        return duration_estimates.get(disaster_type, {}).get(severity, "Variable")
    
    def _assess_cascade_risks(self, disaster_type: str, location: str, severity: DisasterSeverity) -> List[str]:
        """Assess potential cascade risks."""
        cascade_risks = {
            'flood': ["Disease outbreak", "Infrastructure damage", "Food shortage", "Displacement"],
            'drought': ["Food insecurity", "Water scarcity", "Livestock loss", "Migration"],
            'earthquake': ["Aftershocks", "Infrastructure collapse", "Tsunami (coastal)", "Landslides"],
            'industrial_accident': ["Chemical contamination", "Health impacts", "Evacuation", "Economic disruption"],
            'disease_outbreak': ["Healthcare system overload", "Economic disruption", "Travel restrictions", "Social unrest"]
        }
        
        return cascade_risks.get(disaster_type, ["Monitor for secondary effects"])

# Global instance
disaster_classifier = DisasterSeverityClassifier()

def classify_disaster_severity(disaster_type: str, location: str = None, 
                             infrastructure_impact: str = 'moderate',
                             affected_population: str = 'medium',
                             season: str = 'normal',
                             confidence: float = 0.8) -> Dict:
    """Convenience function for disaster severity classification."""
    return disaster_classifier.classify_disaster_severity(
        disaster_type, location, infrastructure_impact, 
        affected_population, season, confidence
    )
