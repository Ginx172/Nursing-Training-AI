class FeedbackAnalyzer:
    def __init__(self, mistral_model):
        self.mistral = mistral_model
        self.error_categories = {
            'SITUATION': ['context', 'background', 'setting'],
            'TASK': ['objective', 'goal', 'challenge'],
            'ACTION': ['steps', 'process', 'implementation'],
            'RESULT': ['outcome', 'impact', 'measurement']
        }
        self.common_strengths = {
            'CLARITY': ['clear', 'concise', 'well-structured'],
            'EVIDENCE': ['examples', 'specifics', 'details'],
            'IMPACT': ['results', 'outcomes', 'benefits']
        }

    def analyze_response(self, response, question):
        """Analyze STAR response and categorize strengths/weaknesses"""
        analysis = self.mistral.generate_response(
            f"Analyze this STAR response for question: {question}\n"
            f"Response: {response}\n"
            f"Identify strengths and weaknesses in each STAR component.\n"
            f"Format: {{'strengths': ['point1', 'point2'], 'weaknesses': ['point1', 'point2']}}"
        )
        return self._process_analysis(analysis)

    def _process_analysis(self, analysis):
        """Process and categorize the analysis results"""
        strengths = []
        weaknesses = []
        
        # Categorize strengths
        for category, keywords in self.common_strengths.items():
            for keyword in keywords:
                if keyword in analysis.lower():
                    strengths.append(f"{category}: {keyword}")
        
        # Categorize weaknesses
        for category, keywords in self.error_categories.items():
            for keyword in keywords:
                if keyword in analysis.lower():
                    weaknesses.append(f"{category}: {keyword}")
        
        return {
            'strengths': list(set(strengths)),
            'weaknesses': list(set(weaknesses)),
            'recommendations': self._generate_recommendations(weaknesses)
        }

    def _generate_recommendations(self, weaknesses):
        """Generate personalized recommendations based on weaknesses"""
        recommendations = []
        
        for weakness in weaknesses:
            category = weakness.split(':')[0]
            recommendation = self.mistral.generate_response(
                f"Provide a specific recommendation for improving {category} in STAR responses."
            )
            recommendations.append(recommendation)
        
        return recommendations

    def generate_improvement_plan(self, all_feedback):
        """Generate a comprehensive improvement plan"""
        common_weaknesses = {}
        strengths_count = {}
        
        # Count occurrences of each weakness and strength
        for feedback in all_feedback:
            for weakness in feedback['weaknesses']:
                common_weaknesses[weakness] = common_weaknesses.get(weakness, 0) + 1
            for strength in feedback['strengths']:
                strengths_count[strength] = strengths_count.get(strength, 0) + 1
        
        # Sort by frequency
        sorted_weaknesses = sorted(common_weaknesses.items(), key=lambda x: x[1], reverse=True)
        sorted_strengths = sorted(strengths_count.items(), key=lambda x: x[1], reverse=True)
        
        # Generate improvement plan
        improvement_plan = self.mistral.generate_response(
            f"Based on these weaknesses: {sorted_weaknesses} and strengths: {sorted_strengths}, "
            f"generate a personalized improvement plan for STAR responses. "
            f"Include specific practice exercises and resources."
        )
        
        return {
            'most_common_weaknesses': sorted_weaknesses[:3],
            'strongest_areas': sorted_strengths[:3],
            'improvement_plan': improvement_plan
        }