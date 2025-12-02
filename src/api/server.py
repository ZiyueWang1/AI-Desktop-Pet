"""
FastAPI Backend Server
API server for Kubernetes deployment and load testing
"""
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add project root directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.config_manager import ConfigManager
from src.infrastructure.memory.vector_store import VectorMemoryStore
from src.domain.profile.profile_manager import ProfileManager
from src.domain.ai.profile_extractor import ProfileExtractor
from src.domain.ai.providers.mock_provider import MockAIProvider
from src.domain.ai.providers.openai_provider import OpenAIProvider
from src.domain.ai.providers.claude_provider import ClaudeProvider
from src.domain.ai.providers.gemini_provider import GeminiProvider

app = FastAPI(
    title="AI Desktop Pet API",
    description="Backend API for AI Desktop Pet application",
    version="1.0.0"
)

# CORS configuration (allow cross-origin access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production should restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instance storage (independent instance for each user)
user_instances: Dict[str, Dict] = {}


# ==================== Request/Response Models ====================

class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_count: int


class HealthResponse(BaseModel):
    status: str
    version: str


# ==================== Utility Functions ====================

def get_user_instance(user_id: str) -> Dict:
    """Get or create user instance"""
    if user_id not in user_instances:
        # Create independent instance for each user
        # Use absolute paths, based on project root directory
        project_root = Path(__file__).parent.parent.parent
        user_data_dir = project_root / "data" / "users" / user_id
        global_data_dir = project_root / "data"
        
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if Mock mode is used
        use_mock = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'
        
        # Initialize ConfigManager, support fallback to global config
        config_manager = ConfigManager(base_dir=str(user_data_dir), fallback_dir=str(global_data_dir))
        
        # Initialize AI Provider
        if use_mock:
            response_delay = float(os.getenv('MOCK_RESPONSE_DELAY', '1.0'))
            cpu_intensive = os.getenv('MOCK_CPU_INTENSIVE', 'true').lower() == 'true'
            ai_provider = MockAIProvider(
                response_delay=response_delay,
                cpu_intensive=cpu_intensive
            )
        else:
            # Use real AI Provider
            provider_name = config_manager.get_ai_provider()
            api_key = config_manager.get_api_key(provider_name)
            model = config_manager.get_model(provider_name)
            
            if not api_key:
                # If no API key, use Mock
                ai_provider = MockAIProvider()
            elif provider_name == "openai":
                ai_provider = OpenAIProvider(api_key=api_key, model=model)
            elif provider_name == "claude":
                ai_provider = ClaudeProvider(api_key=api_key, model=model)
            elif provider_name == "gemini":
                ai_provider = GeminiProvider(api_key=api_key, model=model)
            else:
                ai_provider = MockAIProvider()
        
        instance = {
            'config_manager': config_manager,
            'vector_store': None,
            'profile_manager': None,
            'ai_provider': ai_provider,
            'profile_extractor': ProfileExtractor(ai_provider),
            'conversation_history': [],
        }
        
        # Initialize vector store
        try:
            instance['vector_store'] = VectorMemoryStore(
                persist_directory=str(user_data_dir / "chromadb")
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize vector store for user {user_id}: {e}")
        
        # Initialize user profile
        try:
            instance['profile_manager'] = ProfileManager(
                profile_file=user_data_dir / "user_profile.json"
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize profile manager for user {user_id}: {e}")
        
        user_instances[user_id] = instance
    
    return user_instances[user_id]


def build_system_prompt(instance: Dict, include_rag: bool = True) -> str:
    """
    Build system prompt (consistent with GUI version)
    
    System Prompt Structure:
    1. CRITICAL: Output Example & Performance (highest priority, placed first)
    2. Character Personality
    3. User Profile (from JSON)
    4. Relevant Past Conversations (RAG)
    5. Guidelines (if output_example doesn't exist, use default guidelines)
    """
    parts = []
    character_config = instance['config_manager'].load_character_config()
    
    # ===== 1. CRITICAL: Output Example & Performance (highest priority, placed first) =====
    # This is the most important part: strictly follow user-set performance to generate messages
    # Placed first to ensure AI sees and follows these requirements first
    has_output_example = False
    if character_config.get("output_example"):
        # Prioritize performance requirements in output_example, mark with CRITICAL
        parts.append(f"⚠️ CRITICAL - Output Example & Performance Requirements (MUST FOLLOW EXACTLY):\n{character_config['output_example']}")
        has_output_example = True
    
    # Notes usually contain important length and style requirements, should be included
    if character_config.get("notes"):
        # If output_example already exists, notes as supplement; otherwise notes as main guidance
        if has_output_example:
            # output_example already contains main requirements, notes as supplementary emphasis
            parts.append(f"⚠️ CRITICAL - Additional Notes (MUST FOLLOW):\n{character_config['notes']}")
        else:
            # When no output_example, notes as main guidance
            parts.append(f"⚠️ CRITICAL - Response Guidelines (MUST FOLLOW):\n{character_config['notes']}")
            has_output_example = True
    
    # ===== 2. Character Personality (full mode, no truncation) =====
    if character_config.get("personality"):
        personality = character_config['personality']
        parts.append(f"Personality: {personality}")
    
    # Other config items always added
    if character_config.get("backstory"):
        parts.append(f"Backstory: {character_config['backstory']}")
    if character_config.get("traits"):
        parts.append(f"Traits: {character_config['traits']}")
    if character_config.get("preferences"):
        parts.append(f"Preferences: {character_config['preferences']}")
    if character_config.get("worldview_background"):
        parts.append(f"Worldview Background: {character_config['worldview_background']}")
    if character_config.get("worldview_setting"):
        parts.append(f"Worldview Setting: {character_config['worldview_setting']}")
    
    # Fallback to simple personality if no detailed config
    if not any("Personality:" in p for p in parts):
        personality = instance['config_manager'].load_personality()
        if personality:
            parts.append(f"Personality: {personality}")
        else:
            parts.append("You are a friendly and supportive AI companion.")
    
    # ===== 3. User Profile =====
    if instance['profile_manager']:
        profile = instance['profile_manager'].get_profile()
        profile_summary = []
        
        if profile.name:
            profile_summary.append(f"User: {profile.name}")
        
        if profile.personality_traits:
            # Only take first 3 traits
            traits = ", ".join(profile.personality_traits[:3])
            profile_summary.append(f"Traits: {traits}")
        
        if profile.goals:
            # Show first 3 goals
            goals = ", ".join(profile.goals[:3])
            profile_summary.append(f"Goals: {goals}")
        
        if profile_summary:
            parts.append(" | ".join(profile_summary))
    
    # ===== 4. Relevant Past Conversations (RAG) - Load on demand, only include high relevance memories =====
    if include_rag and instance['vector_store'] and instance['conversation_history']:
        last_user_msg = ""
        for msg in reversed(instance['conversation_history']):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        
        if last_user_msg:
            try:
                relevant_convs = instance['vector_store'].search_relevant_conversations(
                    query=last_user_msg,
                    n_results=2  # Reduced from 3 to 2
                )
                
                # Only include high relevance memories (similarity > 0.7)
                high_relevance_convs = [
                    conv for conv in relevant_convs 
                    if conv.get('relevance_score', 0) > 0.7
                ]
                
                if high_relevance_convs:
                    memory_text = "Relevant memory:\n"
                    conv = high_relevance_convs[0]  # Only take the most relevant one
                    # Limit length of each memory
                    user_msg = conv.get('user_message', '')[:100]
                    ai_resp = conv.get('ai_response', '')[:100]
                    memory_text += f"U: {user_msg}...\nA: {ai_resp}..."
                    parts.append(memory_text)
            except Exception as e:
                print(f"⚠ Warning: Failed to search memories: {e}")
    
    # ===== 5. Guidelines (only use default guidelines if output_example and notes don't exist) =====
    if not has_output_example:
        # Get max_tokens to adjust response length instruction
        max_tokens = instance['config_manager'].get_max_tokens()
        
        # Calculate target sentence count based on max_tokens
        # Roughly: 50 tokens = 1 sentence, so adjust accordingly
        if max_tokens <= 100:
            target_sentences = "1-2"
            target_words = "30-50"
        elif max_tokens <= 200:
            target_sentences = "2-3"
            target_words = "50-80"
        else:
            target_sentences = "2-4"
            target_words = "80-120"
        
        parts.append(f"""Guidelines:
- Use the user profile information naturally in conversation
- Reference relevant past conversations when appropriate
- Stay consistent with your personality
- Be proactive and caring
- IMPORTANT: Keep responses concise ({target_sentences} sentences, {target_words} words). Express your complete thought in these few sentences - be brief but complete. Do not start a long response that gets cut off.""")
    
    return "\n\n".join(parts)


def get_relevant_history(history: List[Dict], current_message: str) -> list:
    """Intelligently select relevant history based on current message"""
    message_lower = current_message.lower()
    word_count = len(current_message.split())
    
    is_greeting = any(word in message_lower 
                     for word in ['hello', 'hi', '你好', '嗨', 'hey'])
    is_simple = word_count < 10
    is_question = '?' in current_message or '？' in current_message
    
    if is_greeting or (is_simple and not is_question):
        return history[-3:] if len(history) > 3 else history
    elif word_count < 30:
        return history[-8:] if len(history) > 8 else history
    else:
        return history[-15:] if len(history) > 15 else history


# ==================== API Endpoints ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user message
    
    Process:
    1. Get user instance
    2. Add to conversation history
    3. Build system prompt
    4. Get relevant history
    5. Call AI to generate response
    6. Save to vector database
    7. Update user profile
    """
    try:
        instance = get_user_instance(request.user_id)
        
        # Add to conversation history
        instance['conversation_history'].append({
            "role": "user",
            "content": request.message
        })
        
        # Build system prompt (always use full mode)
        system_prompt = build_system_prompt(instance, include_rag=True)
        
        # Get relevant history
        relevant_history = get_relevant_history(instance['conversation_history'], request.message)
        
        # Call AI to generate response
        max_tokens = instance['config_manager'].get_max_tokens()
        response = instance['ai_provider'].generate_response(
            messages=relevant_history,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        
        # Add to conversation history
        instance['conversation_history'].append({
            "role": "assistant",
            "content": response
        })
        
        # Save to vector database
        if instance['vector_store'] and len(instance['conversation_history']) >= 2:
            user_msg = instance['conversation_history'][-2]['content']
            try:
                instance['vector_store'].add_conversation(user_msg, response)
            except Exception as e:
                print(f"⚠ Warning: Failed to save to vector store: {e}")
        
        # Update user profile
        if instance['profile_manager']:
            instance['profile_manager'].increment_conversation_count()
            if instance['profile_manager'].should_update_profile():
                try:
                    recent_messages = instance['conversation_history'][-10:]
                    extracted_data = instance['profile_extractor'].extract_user_info(recent_messages)
                    instance['profile_manager'].update_profile_from_ai(extracted_data)
                except Exception as e:
                    print(f"⚠ Warning: Failed to update profile: {e}")
        
        # Limit history length
        if len(instance['conversation_history']) > 20:
            instance['conversation_history'] = instance['conversation_history'][-20:]
        
        return ChatResponse(
            response=response,
            conversation_id=request.user_id,
            message_count=len(instance['conversation_history'])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/conversation/{user_id}")
async def get_conversation(user_id: str):
    """Get conversation history"""
    instance = get_user_instance(user_id)
    return {
        "user_id": user_id,
        "history": instance['conversation_history']
    }


@app.get("/api/v1/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    instance = get_user_instance(user_id)
    if not instance['profile_manager']:
        return {
            "user_id": user_id,
            "profile": None
        }
    
    profile = instance['profile_manager'].get_profile()
    return {
        "user_id": user_id,
        "profile": {
            "name": profile.name,
            "traits": profile.personality_traits,
            "goals": profile.goals,
            "conversation_count": profile.conversation_count
        }
    }


# ==================== Start Server ====================

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 Starting API server on {host}:{port}")
    print(f"📝 API docs available at http://{host}:{port}/docs")
    
    if os.getenv('USE_MOCK_AI', 'false').lower() == 'true':
        print("✓ Using Mock AI Provider (no API tokens consumed)")
    
    uvicorn.run(app, host=host, port=port)

