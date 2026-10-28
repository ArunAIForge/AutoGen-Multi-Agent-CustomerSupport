import re
from typing import Tuple, Optional

def validate_support_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validates user query constraints and catches empty or spam inputs."""
    if not query or not query.strip():
        return False, "Query cannot be empty. Please enter your support question."
        
    cleaned = query.strip()
    
    if len(cleaned) < 3:
        return False, "Your query is too short. Please provide more details regarding your issue."
        
    if len(cleaned) > 2000:
        return False, "Your query exceeds the 2000 character limit. Please shorten your inquiry."
        
    if re.search(r'(.)\1{15,}', cleaned):
        return False, "Your query contains repetitive characters. Please enter a valid question."
        
    return True, None