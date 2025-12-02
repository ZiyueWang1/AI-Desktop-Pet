"""
User Profile Manager
Automatically extract and manage user personal information profiles
"""
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime


class UserProfile:
    """User profile data class - stores user's persistent information"""
    
    def __init__(self, data: Optional[Dict] = None):
        """
        Initialize user profile
        
        Information dimensions included:
        - name: User's name
        - personality_traits: Personality traits (e.g., optimistic, introverted, humorous)
        - preferences: Preferences (e.g., music taste, dietary habits)
        - goals: Goals and aspirations
        - important_dates: Important dates (birthday, anniversaries, etc.)
        - facts: Other important facts
        """
        # Basic information
        self.name: Optional[str] = None
        
        # Personality traits
        self.personality_traits: List[str] = []
        
        # Preferences (dictionary format, supports multiple dimensions)
        self.preferences: Dict[str, str] = {}
        
        # Goals list
        self.goals: List[str] = []
        
        # Important dates (dictionary format: event -> date)
        self.important_dates: Dict[str, str] = {}
        
        # Other facts
        self.facts: List[str] = []
        
        # Metadata
        self.conversation_count: int = 0
        self.last_updated: str = datetime.now().isoformat()
        self.created_at: str = datetime.now().isoformat()
        
        # If data is provided, update fields
        if data:
            self.__dict__.update(data)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format (for JSON serialization)"""
        return {
            "name": self.name,
            "personality_traits": self.personality_traits,
            "preferences": self.preferences,
            "goals": self.goals,
            "important_dates": self.important_dates,
            "facts": self.facts,
            "conversation_count": self.conversation_count,
            "last_updated": self.last_updated,
            "created_at": self.created_at
        }
    
    def to_prompt_text(self) -> str:
        """
        Convert to text format suitable for AI reading
        
        This text will be added to the System Prompt,
        allowing AI to understand the user's background information
        """
        parts = []
        
        # Name
        if self.name:
            parts.append(f"User's name: {self.name}")
        
        # Personality traits
        if self.personality_traits:
            traits = ", ".join(self.personality_traits)
            parts.append(f"User's personality traits: {traits}")
        
        # Preferences
        if self.preferences:
            prefs = []
            for category, value in self.preferences.items():
                prefs.append(f"{category}: {value}")
            parts.append(f"User's preferences:\n  - " + "\n  - ".join(prefs))
        
        # Goals
        if self.goals:
            parts.append(f"User's goals:\n  - " + "\n  - ".join(self.goals))
        
        # Important dates
        if self.important_dates:
            dates = []
            for event, date in self.important_dates.items():
                dates.append(f"{event}: {date}")
            parts.append(f"Important dates:\n  - " + "\n  - ".join(dates))
        
        # Other facts
        if self.facts:
            parts.append(f"Other important facts:\n  - " + "\n  - ".join(self.facts))
        
        if not parts:
            return ""
        
        return "\n\n".join(parts)
    
    def is_empty(self) -> bool:
        """Check if profile is empty"""
        return (
            not self.name 
            and not self.personality_traits 
            and not self.preferences 
            and not self.goals 
            and not self.important_dates 
            and not self.facts
        )


class ProfileManager:
    """User profile manager - handles profile loading, saving, and updating"""
    
    def __init__(self, profile_file: Path = None):
        """
        Initialize profile manager
        
        Args:
            profile_file: Profile file path, defaults to ./data/user_profile.json
        """
        if profile_file is None:
            # Get project root directory
            project_root = Path(__file__).parent.parent.parent.parent
            profile_file = project_root / "data" / "user_profile.json"
        
        self.profile_file = profile_file
        self.profile = self._load_profile()
        
        print(f"✓ Profile Manager initialized")
        if not self.profile.is_empty():
            print(f"  - User: {self.profile.name or 'Unknown'}")
            print(f"  - Conversations: {self.profile.conversation_count}")
            print(f"  - Last updated: {self.profile.last_updated}")
    
    def _load_profile(self) -> UserProfile:
        """Load user profile from file"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✓ Loaded existing user profile from {self.profile_file}")
                    return UserProfile(data)
            except Exception as e:
                print(f"✗ Failed to load profile: {e}")
                print("  Creating new profile...")
        
        return UserProfile()
    
    def save_profile(self) -> bool:
        """
        Save user profile to file
        
        Returns:
            Whether save was successful
        """
        try:
            # Ensure directory exists
            self.profile_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Update timestamp
            self.profile.last_updated = datetime.now().isoformat()
            
            # Save to JSON file
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.profile.to_dict(), 
                    f, 
                    indent=2, 
                    ensure_ascii=False
                )
            
            print(f"✓ Saved user profile to {self.profile_file}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to save profile: {e}")
            return False
    
    def get_profile(self) -> UserProfile:
        """Get current user profile"""
        return self.profile
    
    def update_profile_from_ai(self, ai_extracted_data: Dict):
        """
        Update profile using AI-extracted information
        
        How it works:
        1. AI analyzes conversation and returns structured data
        2. Incrementally update profile (deduplicate, merge)
        3. Save to file
        
        Args:
            ai_extracted_data: User information returned by AI analysis
            Format: {
                "name": "Alex",
                "personality_traits": ["creative", "curious"],
                "preferences": {"music": "indie rock"},
                "goals": ["learn Python"],
                "important_dates": {"birthday": "1995-03-15"},
                "facts": ["has a cat"]
            }
        """
        updated = False
        
        # Update name (only if currently empty)
        if "name" in ai_extracted_data and ai_extracted_data["name"]:
            if not self.profile.name:
                self.profile.name = ai_extracted_data["name"]
                updated = True
                print(f"  ✓ Updated name: {self.profile.name}")
        
        # Update personality traits (deduplicate and add)
        if "personality_traits" in ai_extracted_data:
            new_traits = ai_extracted_data["personality_traits"]
            for trait in new_traits:
                if trait and trait not in self.profile.personality_traits:
                    self.profile.personality_traits.append(trait)
                    updated = True
                    print(f"  ✓ Added personality trait: {trait}")
        
        # Update preferences (merge dictionary)
        if "preferences" in ai_extracted_data:
            new_prefs = ai_extracted_data["preferences"]
            for key, value in new_prefs.items():
                if key and value:
                    if key not in self.profile.preferences or self.profile.preferences[key] != value:
                        self.profile.preferences[key] = value
                        updated = True
                        print(f"  ✓ Updated preference: {key} = {value}")
        
        # Update goals (deduplicate and add)
        if "goals" in ai_extracted_data:
            new_goals = ai_extracted_data["goals"]
            for goal in new_goals:
                if goal and goal not in self.profile.goals:
                    self.profile.goals.append(goal)
                    updated = True
                    print(f"  ✓ Added goal: {goal}")
        
        # Update important dates (merge dictionary)
        if "important_dates" in ai_extracted_data:
            new_dates = ai_extracted_data["important_dates"]
            for event, date in new_dates.items():
                if event and date:
                    if event not in self.profile.important_dates or self.profile.important_dates[event] != date:
                        self.profile.important_dates[event] = date
                        updated = True
                        print(f"  ✓ Added important date: {event} = {date}")
        
        # Update facts (deduplicate and add)
        if "facts" in ai_extracted_data:
            new_facts = ai_extracted_data["facts"]
            for fact in new_facts:
                if fact and fact not in self.profile.facts:
                    self.profile.facts.append(fact)
                    updated = True
                    print(f"  ✓ Added fact: {fact}")
        
        # If there are updates, save to file
        if updated:
            self.save_profile()
            print(f"✓ User profile updated successfully")
        else:
            print(f"  No new information extracted")
    
    def increment_conversation_count(self):
        """Increment conversation count"""
        self.profile.conversation_count += 1
        # Don't save immediately, wait until next update to save together
    
    def should_update_profile(self) -> bool:
        """
        Determine if profile should be updated
        
        Optimized update strategy:
        - First 20 conversations: update every 5 (quickly build profile)
        - 20-50 conversations: update every 10 (medium frequency)
        - After 50: update every 15 (reduce frequency, less incremental information)
        
        Returns:
            Whether profile update should be triggered
        """
        count = self.profile.conversation_count
        
        if count <= 0:
            return False
        elif count <= 20:
            # Early stage: quickly build profile
            return count % 5 == 0
        elif count <= 50:
            # Mid stage: medium frequency
            return count % 10 == 0
        else:
            # Later stage: reduce frequency
            return count % 15 == 0
    
    def get_profile_summary(self) -> str:
        """Get profile summary (for debugging and display)"""
        if self.profile.is_empty():
            return "User profile is empty"
        
        summary_parts = []
        
        if self.profile.name:
            summary_parts.append(f"Name: {self.profile.name}")
        
        if self.profile.personality_traits:
            summary_parts.append(f"Traits: {', '.join(self.profile.personality_traits[:3])}")
        
        if self.profile.goals:
            summary_parts.append(f"Goals: {len(self.profile.goals)} items")
        
        if self.profile.preferences:
            summary_parts.append(f"Preferences: {len(self.profile.preferences)} items")
        
        summary_parts.append(f"Conversations: {self.profile.conversation_count}")
        
        return " | ".join(summary_parts)
    
    def reset_profile(self):
        """Reset profile (clear all data)"""
        self.profile = UserProfile()
        self.save_profile()
        print("✓ User profile has been reset")

