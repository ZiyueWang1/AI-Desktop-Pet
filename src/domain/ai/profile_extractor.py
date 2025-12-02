"""
Profile Extractor
Use AI to extract user information from conversations
"""
from typing import Dict, List, Optional
import json
import re


class ProfileExtractor:
    """Use AI to extract user information from conversations"""
    
    def __init__(self, ai_provider):
        """
        Initialize profile extractor
        
        Args:
            ai_provider: AI provider instance (OpenAIProvider, ClaudeProvider, etc.)
        """
        self.ai_provider = ai_provider
    
    def extract_user_info(self, recent_messages: List[Dict]) -> Dict:
        """
        Analyze recent conversations and extract user information
        
        Args:
            recent_messages: Recent conversation history, format: [{"role": "user|assistant", "content": "..."}]
            
        Returns:
            Extracted user information dictionary, format:
            {
                "name": "user's name or null",
                "personality_traits": ["trait1", "trait2"],
                "preferences": {"category": "preference"},
                "goals": ["goal1", "goal2"],
                "important_dates": {"event": "date"},
                "facts": ["fact1", "fact2"]
            }
        """
        # Build analysis prompt
        conversation_text = self._format_messages(recent_messages)
        
        system_prompt = """You are a user profile analyst. Extract key information about the user from the conversation.

CRITICAL: You MUST return ONLY a valid JSON object, with no additional text, explanations, or markdown formatting. Do not include ```json or ``` markers.

Return ONLY this JSON structure (use null for missing fields):
{
  "name": "user's name or null",
  "personality_traits": ["trait1", "trait2"],
  "preferences": {"category": "preference"},
  "goals": ["goal1", "goal2"],
  "important_dates": {"event": "date"},
  "facts": ["fact1", "fact2"]
}

Important:
- Return ONLY the JSON object, nothing else
- Only extract information explicitly mentioned by the user
- Do not infer or assume information
- Use empty arrays [] and empty objects {} if no information found
- Use null for missing string fields
- Ensure valid JSON format (no trailing commas, proper quotes)
- For personality_traits, extract observable traits from the conversation
- For preferences, extract specific likes/dislikes mentioned
- For goals, extract stated goals or aspirations
- For important_dates, extract dates mentioned (birthday, deadlines, etc.)
- For facts, extract other notable information about the user"""

        user_prompt = f"""Analyze this conversation and extract user information:

{conversation_text}

Return ONLY the JSON object. Do not include any explanations, markdown formatting, or additional text. Just the JSON."""

        # Call AI
        try:
            response = self.ai_provider.generate_response(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt
            )
            
            # Parse JSON
            extracted_data = self._parse_json_response(response)
            return extracted_data
            
        except Exception as e:
            print(f"✗ Profile extraction failed: {e}")
            return self._get_empty_extraction()
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        Parse JSON response from AI
        
        Handle possible markdown code block markers and extra text
        """
        if not response or not response.strip():
            print(f"⚠ Warning: Empty AI response, using empty extraction")
            return self._get_empty_extraction()
        
        # Remove possible markdown code block markers
        response = response.strip()
        
        # Remove ```json or ``` markers
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Try direct parsing
        try:
            extracted_data = json.loads(response)
            return self._validate_extraction(extracted_data)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON portion
            # Use more precise regex to match complete JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                try:
                    extracted_data = json.loads(json_match.group())
                    return self._validate_extraction(extracted_data)
                except json.JSONDecodeError as e:
                    # Try more lenient matching
                    json_match2 = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match2:
                        try:
                            extracted_data = json.loads(json_match2.group())
                            return self._validate_extraction(extracted_data)
                        except json.JSONDecodeError:
                            pass
        
        # If all parsing fails, print debug info (only first 200 chars to avoid long logs)
        debug_response = response[:200] + "..." if len(response) > 200 else response
        print(f"⚠ Warning: Failed to parse JSON from AI response, using empty extraction")
        print(f"   Response preview: {debug_response}")
        return self._get_empty_extraction()
    
    def _validate_extraction(self, data: Dict) -> Dict:
        """Validate and normalize extracted data"""
        # Ensure all fields exist
        validated = {
            "name": data.get("name"),
            "personality_traits": data.get("personality_traits", []),
            "preferences": data.get("preferences", {}),
            "goals": data.get("goals", []),
            "important_dates": data.get("important_dates", {}),
            "facts": data.get("facts", [])
        }
        
        # Ensure types are correct
        if validated["name"] and not isinstance(validated["name"], str):
            validated["name"] = None
        
        if not isinstance(validated["personality_traits"], list):
            validated["personality_traits"] = []
        
        if not isinstance(validated["preferences"], dict):
            validated["preferences"] = {}
        
        if not isinstance(validated["goals"], list):
            validated["goals"] = []
        
        if not isinstance(validated["important_dates"], dict):
            validated["important_dates"] = {}
        
        if not isinstance(validated["facts"], list):
            validated["facts"] = []
        
        return validated
    
    def _get_empty_extraction(self) -> Dict:
        """Return empty extraction result"""
        return {
            "name": None,
            "personality_traits": [],
            "preferences": {},
            "goals": [],
            "important_dates": {},
            "facts": []
        }
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages as text"""
        formatted = []
        for msg in messages:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        return "\n\n".join(formatted)

