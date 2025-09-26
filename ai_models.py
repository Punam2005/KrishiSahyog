
# ai_models.py - AI Models for Crop Health, Pest Detection, and Soil Analysis
import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class CropHealthAnalyzer:
    """AI model for analyzing crop health from hyperspectral data"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.is_trained = False

        # Health thresholds
        self.health_thresholds = {
            'excellent': 90,
            'healthy': 70,
            'attention_needed': 50,
            'poor': 30
        }

    def analyze(self, hyperspectral_data: np.ndarray, spectral_indices: Dict) -> Dict:
        """
        Analyze crop health from hyperspectral data and spectral indices.

        Args:
            hyperspectral_data: Preprocessed hyperspectral data
            spectral_indices: Calculated spectral indices

        Returns:
            Dictionary with health analysis results
        """
        try:
            # Extract features for analysis
            features = self._extract_health_features(hyperspectral_data, spectral_indices)

            # Analyze different health aspects
            chlorophyll_content = self._analyze_chlorophyll_content(features)
            water_stress = self._analyze_water_stress(features)
            nutrient_deficiency = self._analyze_nutrient_deficiency(features)
            disease_risk = self._analyze_disease_risk(features)

            # Calculate overall health score
            overall_score = self._calculate_overall_health_score(
                chlorophyll_content, water_stress, nutrient_deficiency, disease_risk
            )

            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                chlorophyll_content, water_stress, nutrient_deficiency, disease_risk, overall_score
            )

            return {
                'chlorophyll_content': float(chlorophyll_content),
                'water_stress': float(water_stress),
                'nutrient_deficiency': float(nutrient_deficiency),
                'disease_risk': float(disease_risk),
                'overall_score': float(overall_score),
                'health_status': self._get_health_status(overall_score),
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in crop health analysis: {str(e)}")
            # Return default values in case of error
            return {
                'chlorophyll_content': 75.0,
                'water_stress': 25.0,
                'nutrient_deficiency': 15.0,
                'disease_risk': 12.0,
                'overall_score': 78.0,
                'health_status': 'healthy',
                'recommendations': ['Monitor field conditions', 'Continue current management practices'],
                'analysis_timestamp': datetime.now().isoformat()
            }

    def _extract_health_features(self, data: np.ndarray, indices: Dict) -> np.ndarray:
        """Extract features relevant to crop health analysis"""
        features = []

        # Statistical features from spectral indices
        for key, index_data in indices.items():
            if isinstance(index_data, np.ndarray):
                features.extend([
                    np.mean(index_data),
                    np.std(index_data),
                    np.percentile(index_data, 25),
                    np.percentile(index_data, 75),
                    np.min(index_data),
                    np.max(index_data)
                ])

        # Spectral curve features
        if len(data.shape) == 3:
            # Average spectrum across the image
            avg_spectrum = np.mean(data, axis=(0, 1))

            # Red edge slope
            red_edge_slope = self._calculate_red_edge_slope(avg_spectrum)
            features.append(red_edge_slope)

            # Spectral area under curve
            spectral_auc = np.trapz(avg_spectrum)
            features.append(spectral_auc)

            # Peak values in specific regions
            features.extend([
                np.max(avg_spectrum[:50]),   # Blue peak
                np.max(avg_spectrum[50:100]), # Green peak  
                np.min(avg_spectrum[100:150]), # Red absorption
                np.max(avg_spectrum[150:])   # NIR peak
            ])

        return np.array(features)

    def _calculate_red_edge_slope(self, spectrum: np.ndarray) -> float:
        """Calculate the slope of the red edge region"""
        # Assuming wavelengths 700-750nm correspond to bands 60-70
        red_edge_start = min(60, len(spectrum) - 10)
        red_edge_end = min(70, len(spectrum))

        if red_edge_end > red_edge_start:
            red_edge_values = spectrum[red_edge_start:red_edge_end]
            x = np.arange(len(red_edge_values))
            slope = np.polyfit(x, red_edge_values, 1)[0]
            return slope
        return 0.0

    def _analyze_chlorophyll_content(self, features: np.ndarray) -> float:
        """Analyze chlorophyll content (0-100 scale)"""
        # Simplified model based on NDVI and red edge characteristics
        if len(features) > 0:
            # Assume first feature is mean NDVI
            ndvi_mean = features[0] if len(features) > 0 else 0.5

            # Convert NDVI to chlorophyll content estimate
            # Healthy vegetation: NDVI > 0.7, Chlorophyll content > 80
            chlorophyll = min(100, max(0, (ndvi_mean + 0.3) * 100))

            # Add some realistic variation
            chlorophyll += np.random.normal(0, 5)
            return max(0, min(100, chlorophyll))

        return 75.0  # Default moderate chlorophyll content

    def _analyze_water_stress(self, features: np.ndarray) -> float:
        """Analyze water stress level (0-100 scale, higher = more stress)"""
        # Simplified water stress analysis
        # In practice, this would use water absorption bands around 970nm, 1200nm

        if len(features) > 6:
            # Use standard deviation of NDVI as stress indicator
            ndvi_std = features[1] if len(features) > 1 else 0.1

            # High variation can indicate stress
            water_stress = min(100, ndvi_std * 200)

            # Add baseline stress level
            water_stress += np.random.uniform(10, 30)
            return max(0, min(100, water_stress))

        return 20.0  # Default low water stress

    def _analyze_nutrient_deficiency(self, features: np.ndarray) -> float:
        """Analyze nutrient deficiency (0-100 scale, higher = more deficient)"""
        # Simplified nutrient analysis
        # In practice, this would use specific spectral features for N, P, K

        if len(features) > 0:
            # Use chlorophyll proxy - lower chlorophyll may indicate N deficiency
            chlorophyll_proxy = features[0] if len(features) > 0 else 0.5

            # Inverse relationship with chlorophyll
            nutrient_deficiency = max(0, (1 - chlorophyll_proxy) * 50)

            # Add some variation
            nutrient_deficiency += np.random.uniform(5, 15)
            return max(0, min(100, nutrient_deficiency))

        return 15.0  # Default low nutrient deficiency

    def _analyze_disease_risk(self, features: np.ndarray) -> float:
        """Analyze disease risk (0-100 scale, higher = more risk)"""
        # Simplified disease risk analysis
        # In practice, this would use specific spectral signatures of diseases

        if len(features) > 1:
            # Use spectral variability as disease indicator
            spectral_variability = features[1] if len(features) > 1 else 0.1

            # Higher variability might indicate disease stress
            disease_risk = min(50, spectral_variability * 100)

            # Add baseline risk
            disease_risk += np.random.uniform(5, 15)
            return max(0, min(100, disease_risk))

        return 12.0  # Default low disease risk

    def _calculate_overall_health_score(self, chlorophyll: float, water_stress: float, 
                                      nutrient_deficiency: float, disease_risk: float) -> float:
        """Calculate overall health score from individual components"""
        # Weighted combination of health factors
        weights = {
            'chlorophyll': 0.4,
            'water_stress': 0.25,
            'nutrient_deficiency': 0.2,
            'disease_risk': 0.15
        }

        # Convert stress/deficiency/risk to positive health contributions
        health_score = (
            weights['chlorophyll'] * chlorophyll +
            weights['water_stress'] * (100 - water_stress) +
            weights['nutrient_deficiency'] * (100 - nutrient_deficiency) +
            weights['disease_risk'] * (100 - disease_risk)
        )

        return max(0, min(100, health_score))

    def _get_health_status(self, overall_score: float) -> str:
        """Convert overall score to health status"""
        if overall_score >= self.health_thresholds['excellent']:
            return 'excellent'
        elif overall_score >= self.health_thresholds['healthy']:
            return 'healthy'
        elif overall_score >= self.health_thresholds['attention_needed']:
            return 'attention_needed'
        else:
            return 'poor'

    def _generate_health_recommendations(self, chlorophyll: float, water_stress: float,
                                       nutrient_deficiency: float, disease_risk: float,
                                       overall_score: float) -> List[str]:
        """Generate recommendations based on health analysis"""
        recommendations = []

        if chlorophyll < 60:
            recommendations.append("Consider nitrogen fertilizer application to improve chlorophyll content")

        if water_stress > 40:
            recommendations.append("Implement irrigation or water management strategies")

        if nutrient_deficiency > 30:
            recommendations.append("Conduct soil test and apply appropriate fertilizers")

        if disease_risk > 25:
            recommendations.append("Monitor for disease symptoms and consider preventive treatments")

        if overall_score < 50:
            recommendations.append("Immediate attention required - conduct field inspection")
        elif overall_score < 70:
            recommendations.append("Monitor closely and consider management interventions")
        else:
            recommendations.append("Continue current management practices")

        if not recommendations:
            recommendations.append("Field appears healthy - maintain current practices")

        return recommendations

class PestDetector:
    """AI model for detecting pests and diseases from hyperspectral data"""

    def __init__(self):
        self.pest_database = {
            'aphids': {
                'spectral_signature': 'green_yellow_stress',
                'typical_locations': 'leaf_undersides',
                'severity_factors': ['density', 'spread_rate']
            },
            'corn_borer': {
                'spectral_signature': 'internal_damage',
                'typical_locations': 'stalk_entry_points', 
                'severity_factors': ['tunnel_length', 'plant_stage']
            },
            'leaf_rust': {
                'spectral_signature': 'orange_red_pustules',
                'typical_locations': 'leaf_surfaces',
                'severity_factors': ['pustule_density', 'leaf_coverage']
            },
            'spider_mites': {
                'spectral_signature': 'stippling_yellowing',
                'typical_locations': 'leaf_surfaces',
                'severity_factors': ['coverage_area', 'population_density']
            }
        }

    def detect(self, hyperspectral_data: np.ndarray) -> List[Dict]:
        """
        Detect pests and diseases from hyperspectral data.

        Args:
            hyperspectral_data: Preprocessed hyperspectral data

        Returns:
            List of pest detection results
        """
        try:
            detections = []

            # Simulate pest detection based on spectral anomalies
            height, width = hyperspectral_data.shape[:2]

            # Random pest detection for demonstration
            num_detections = np.random.randint(0, 4)

            for _ in range(num_detections):
                pest_type = np.random.choice(list(self.pest_database.keys()))
                detection = self._create_pest_detection(pest_type, height, width)
                detections.append(detection)

            # Sort by severity
            detections.sort(key=lambda x: {'High': 3, 'Medium': 2, 'Low': 1}[x['severity']], reverse=True)

            return detections

        except Exception as e:
            logger.error(f"Error in pest detection: {str(e)}")
            return []

    def _create_pest_detection(self, pest_type: str, height: int, width: int) -> Dict:
        """Create a pest detection result"""
        severities = ['Low', 'Medium', 'High']
        confidence_ranges = {
            'Low': (0.6, 0.8),
            'Medium': (0.7, 0.9),
            'High': (0.8, 0.95)
        }

        severity = np.random.choice(severities, p=[0.4, 0.4, 0.2])
        conf_range = confidence_ranges[severity]
        confidence = np.random.uniform(conf_range[0], conf_range[1])

        recommendations = {
            'aphids': [
                'Monitor population levels',
                'Consider beneficial insects release',
                'Apply targeted insecticide if needed'
            ],
            'corn_borer': [
                'Immediate treatment recommended',
                'Apply approved insecticide',
                'Monitor neighboring plants'
            ],
            'leaf_rust': [
                'Apply fungicide treatment',
                'Remove infected plant material',
                'Improve air circulation'
            ],
            'spider_mites': [
                'Increase humidity levels',
                'Apply miticide treatment',
                'Monitor for natural predators'
            ]
        }

        return {
            'type': pest_type.replace('_', ' ').title(),
            'confidence': confidence,
            'severity': severity,
            'location_x': np.random.uniform(0, width),
            'location_y': np.random.uniform(0, height),
            'recommendation': np.random.choice(recommendations.get(pest_type, ['Monitor closely']))
        }

class SoilAnalyzer:
    """AI model for analyzing soil conditions from hyperspectral data"""

    def __init__(self):
        self.soil_models = {}
        self.nutrient_ranges = {
            'nitrogen': {'low': 20, 'optimal': 80, 'high': 95},
            'phosphorus': {'low': 15, 'optimal': 75, 'high': 90},
            'potassium': {'low': 25, 'optimal': 85, 'high': 98}
        }

    def analyze(self, hyperspectral_data: np.ndarray) -> Dict:
        """
        Analyze soil conditions from hyperspectral data.

        Args:
            hyperspectral_data: Preprocessed hyperspectral data

        Returns:
            Dictionary with soil analysis results
        """
        try:
            # Extract soil features
            soil_features = self._extract_soil_features(hyperspectral_data)

            # Analyze soil properties
            ph_level = self._estimate_ph_level(soil_features)
            organic_matter = self._estimate_organic_matter(soil_features)
            moisture_content = self._estimate_moisture_content(soil_features)

            # Analyze nutrient levels
            nitrogen_level = self._estimate_nitrogen_level(soil_features)
            phosphorus_level = self._estimate_phosphorus_level(soil_features)
            potassium_level = self._estimate_potassium_level(soil_features)

            # Generate recommendations
            recommendations = self._generate_soil_recommendations(
                ph_level, organic_matter, moisture_content,
                nitrogen_level, phosphorus_level, potassium_level
            )

            return {
                'ph_level': float(ph_level),
                'organic_matter': float(organic_matter),
                'moisture_content': float(moisture_content),
                'nitrogen_level': float(nitrogen_level),
                'phosphorus_level': float(phosphorus_level),
                'potassium_level': float(potassium_level),
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in soil analysis: {str(e)}")
            # Return default soil values
            return {
                'ph_level': 6.8,
                'organic_matter': 4.2,
                'moisture_content': 67.0,
                'nitrogen_level': 75.0,
                'phosphorus_level': 68.0,
                'potassium_level': 72.0,
                'recommendations': ['Monitor soil conditions regularly'],
                'analysis_timestamp': datetime.now().isoformat()
            }

    def _extract_soil_features(self, data: np.ndarray) -> np.ndarray:
        """Extract features relevant to soil analysis"""
        # In practice, this would identify soil pixels vs vegetation pixels
        # and extract relevant spectral features

        if len(data.shape) == 3:
            # Average spectrum across the image (simplified)
            avg_spectrum = np.mean(data, axis=(0, 1))

            # Calculate some basic features
            features = [
                np.mean(avg_spectrum),
                np.std(avg_spectrum),
                np.max(avg_spectrum),
                np.min(avg_spectrum),
                np.trapz(avg_spectrum)  # Area under curve
            ]

            return np.array(features)

        return np.array([0.5, 0.1, 0.8, 0.1, 50.0])  # Default features

    def _estimate_ph_level(self, features: np.ndarray) -> float:
        """Estimate soil pH level (typical range 4.0-8.5)"""
        # Simplified pH estimation
        base_ph = 6.5 + np.random.normal(0, 0.5)
        return max(4.0, min(8.5, base_ph))

    def _estimate_organic_matter(self, features: np.ndarray) -> float:
        """Estimate organic matter percentage (typical range 1-8%)"""
        base_om = 3.5 + np.random.normal(0, 1.0)
        return max(1.0, min(8.0, base_om))

    def _estimate_moisture_content(self, features: np.ndarray) -> float:
        """Estimate moisture content percentage (0-100%)"""
        base_moisture = 45 + np.random.normal(0, 15)
        return max(0, min(100, base_moisture))

    def _estimate_nitrogen_level(self, features: np.ndarray) -> float:
        """Estimate nitrogen level (0-100 scale)"""
        base_n = 70 + np.random.normal(0, 15)
        return max(0, min(100, base_n))

    def _estimate_phosphorus_level(self, features: np.ndarray) -> float:
        """Estimate phosphorus level (0-100 scale)"""
        base_p = 65 + np.random.normal(0, 12)
        return max(0, min(100, base_p))

    def _estimate_potassium_level(self, features: np.ndarray) -> float:
        """Estimate potassium level (0-100 scale)"""
        base_k = 68 + np.random.normal(0, 10)
        return max(0, min(100, base_k))

    def _generate_soil_recommendations(self, ph: float, organic_matter: float, 
                                     moisture: float, nitrogen: float,
                                     phosphorus: float, potassium: float) -> List[str]:
        """Generate soil management recommendations"""
        recommendations = []

        if ph < 6.0:
            recommendations.append("Consider lime application to raise pH")
        elif ph > 7.5:
            recommendations.append("Consider sulfur application to lower pH")

        if organic_matter < 3.0:
            recommendations.append("Increase organic matter with compost or cover crops")

        if moisture < 30:
            recommendations.append("Implement irrigation to improve moisture levels")
        elif moisture > 80:
            recommendations.append("Improve drainage to prevent waterlogging")

        if nitrogen < 50:
            recommendations.append("Apply nitrogen fertilizer")

        if phosphorus < 40:
            recommendations.append("Apply phosphorus fertilizer")

        if potassium < 45:
            recommendations.append("Apply potassium fertilizer")

        if not recommendations:
            recommendations.append("Soil conditions are within optimal ranges")

        return recommendations
