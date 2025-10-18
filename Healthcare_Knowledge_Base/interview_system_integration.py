
# Integration with complete interview system
def enhance_interview_with_materials(interview_system):
    """Enhance interview system with downloaded materials"""
    
    materials_path = Path("Healthcare_Knowledge_Base")
    
    # Add materials search to AI consensus
    def search_relevant_materials(question, candidate_response):
        """Search for relevant materials based on question and response"""
        
        query = f"{question.question} {candidate_response.response_text}"
        
        # Determine band and specialty from question metadata
        band = question.band
        specialty = question.category
        
        # Search materials
        results = materials_downloader.search_materials(
            query=query,
            band=band,
            specialty=specialty,
            top_k=3
        )
        
        return results
    
    # Enhance feedback with evidence-based recommendations
    interview_system.ai_consensus.search_materials = search_relevant_materials
    
    print("✅ Interview system enhanced with materials database")

# Usage in your interview system:
# enhance_interview_with_materials(your_interview_system)
