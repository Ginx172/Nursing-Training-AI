import numpy as np
from typing import Dict, List
from datetime import datetime

class ClinicalPerformanceAnalyzer:
    def __init__(self, mistral_model, knowledge_manager):
        self.mistral = mistral_model
        self.knowledge_manager = knowledge_manager
        self.clinical_scenarios = []
        self.performance_metrics = {
            'clinical_judgment': 0,
            'patient_safety': 0,
            'communication': 0,
            'documentation': 0,
            'time_management': 0
        }
        self.current_scenario = None

    def load_clinical_scenarios(self):
        """Load clinical scenarios from knowledge base"""
        scenarios = self.knowledge_manager.get_relevant_chunks(
            "clinical scenarios and patient care", "training_clinic_merged"
        )
        self.clinical_scenarios = self._process_scenarios(scenarios)
        return len(self.clinical_scenarios)

    def _process_scenarios(self, scenarios):
        """Process and categorize clinical scenarios"""
        processed_scenarios = []
        for scenario in scenarios:
            # Extract key elements
            elements = self.mistral.generate_response(
                f"Analyze this clinical scenario: {scenario}. "
                f"Extract: 1. Patient condition, 2. Required actions, 3. Potential risks."
            )
            
            # Generate assessment criteria
            criteria = self.mistral.generate_response(
                f"Generate assessment criteria for this scenario: {scenario}. "
                f"Include: 1. Clinical judgment, 2. Patient safety, 3. Communication."
            )
            
            processed_scenarios.append({
                'scenario': scenario,
                'elements': elements,
                'criteria': criteria,
                'assessment': {}
            })
        
        return processed_scenarios

    def start_scenario(self, scenario_index: int):
        """Start a specific clinical scenario"""
        if scenario_index >= len(self.clinical_scenarios):
            return "Invalid scenario index"
        
        self.current_scenario = self.clinical_scenarios[scenario_index]
        return self.current_scenario['scenario']

    def analyze_response(self, user_response: str):
        """Analyze user's response to clinical scenario"""
        # Get context from scenario
        context = self.current_scenario['scenario']
        
        # Generate assessment
        assessment = self.mistral.generate_response(
            f"Assess this response to clinical scenario: {context}\n"
            f"Response: {user_response}\n"
            f"Criteria: {self.current_scenario['criteria']}\n"
            f"Analyze: 1. Clinical judgment, 2. Patient safety, 3. Communication."
        )
        
        # Calculate scores
        scores = self._calculate_scores(assessment)
        
        # Update metrics
        self._update_metrics(scores)
        
        return {
            'assessment': assessment,
            'scores': scores,
            'recommendations': self._generate_recommendations(assessment)
        }

    def _calculate_scores(self, assessment: str):
        """Calculate performance scores based on assessment"""
        # Extract scores for each metric
        scores = {}
        for metric in self.performance_metrics.keys():
            score = self.mistral.generate_response(
                f"Score this aspect of the assessment: {assessment}\n"
                f"Aspect: {metric}\n"
                f"Provide score (1-5) and justification."
            )
            scores[metric] = float(score.split()[0])  # Extract numeric score
        
        return scores

    def _update_metrics(self, scores: Dict[str, float]):
        """Update overall performance metrics"""
        for metric, score in scores.items():
            current_score = self.performance_metrics[metric]
            self.performance_metrics[metric] = (current_score + score) / 2  # Simple average

    def _generate_recommendations(self, assessment: str):
        """Generate personalized recommendations"""
        recommendations = self.mistral.generate_response(
            f"Based on this assessment: {assessment}, "
            f"generate specific recommendations for improvement in clinical practice."
        )
        
        return recommendations

    def generate_performance_report(self):
        """Generate comprehensive clinical performance report"""
        report = {
            'overall_performance': np.mean(list(self.performance_metrics.values())),
            'metrics': self.performance_metrics.copy(),
            'strengths': self._identify_strengths(),
            'areas_for_improvement': self._identify_weaknesses(),
            'recommendations': self._generate_overall_recommendations()
        }
        
        return report

    def _identify_strengths(self):
        """Identify areas of strength"""
        strengths = []
        for metric, score in self.performance_metrics.items():
            if score >= 4.0:  # Consider score >= 4 as strength
                strengths.append({
                    'metric': metric,
                    'score': score,
                    'evaluation': self.mistral.generate_response(
                        f"Evaluate why this is a strength: {metric} score {score}"
                    )
                })
        return strengths

    def _identify_weaknesses(self):
        """Identify areas needing improvement"""
        weaknesses = []
        for metric, score in self.performance_metrics.items():
            if score <= 3.0:  # Consider score <= 3 as weakness
                weaknesses.append({
                    'metric': metric,
                    'score': score,
                    'evaluation': self.mistral.generate_response(
                        f"Analyze why this needs improvement: {metric} score {score}"
                    )
                })
        return weaknesses

    def _generate_overall_recommendations(self):
        """Generate comprehensive recommendations"""
        recommendations = self.mistral.generate_response(
            f"Based on these metrics: {self.performance_metrics}, "
            f"generate a comprehensive plan for improving clinical performance."
        )
        
        return recommendations