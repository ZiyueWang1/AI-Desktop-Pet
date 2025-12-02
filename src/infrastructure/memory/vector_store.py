"""
ChromaDB Vector Store
Long-term memory vector storage manager
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import os


class VectorMemoryStore:
    """ChromaDB vector storage manager"""
    
    def __init__(self, persist_directory: str = "./data/chromadb", openai_api_key: Optional[str] = None):
        """
        Initialize ChromaDB client
        
        Args:
            persist_directory: Data persistence directory
            openai_api_key: OpenAI API key (deprecated, now using free local model)
        """
        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Use free local SentenceTransformer model
        # Advantages: completely free, no account needed, data local, good privacy
        try:
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # Free high-quality local model
            )
            print("✓ Using SentenceTransformer embeddings (all-MiniLM-L6-v2) - 100% free and local")
            print("  First run will download the model (~80MB), then works offline")
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize SentenceTransformer embeddings: {e}")
            print("  Falling back to default embedding function")
            try:
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            except Exception:
                # If default function is also unavailable, use None (ChromaDB will use default)
                self.embedding_function = None
        
        # Create or get collection
        try:
            self.collection = self.client.get_or_create_collection(
                name="conversation_memory",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            print(f"✓ ChromaDB collection initialized: {self.collection.count()} conversations stored")
        except Exception as e:
            print(f"✗ Failed to initialize ChromaDB collection: {e}")
            raise
    
    def add_conversation(
        self, 
        user_message: str, 
        ai_response: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save conversation to vector database
        
        Args:
            user_message: User message
            ai_response: AI response
            metadata: Additional metadata
            
        Returns:
            Conversation ID
        """
        try:
            # Generate unique ID
            conversation_id = f"conv_{datetime.now().timestamp()}_{hash(user_message + ai_response) % 10000}"
            
            # Combine user message and AI response as document
            document = f"User: {user_message}\nAssistant: {ai_response}"
            
            # Prepare metadata
            meta = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message[:500],  # Limit length
                "ai_response": ai_response[:500],     # Limit length
                **(metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                documents=[document],
                metadatas=[meta],
                ids=[conversation_id]
            )
            
            return conversation_id
        except Exception as e:
            print(f"✗ Failed to add conversation to vector store: {e}")
            return ""
    
    def search_relevant_conversations(
        self, 
        query: str, 
        n_results: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant historical conversations based on query
        
        Args:
            query: Query text (usually user's latest message)
            n_results: Number of results to return
            
        Returns:
            List of relevant conversations, format: [{
                "user_message": "...",
                "ai_response": "...",
                "timestamp": "...",
                "relevance_score": 0.0-1.0
            }]
        """
        try:
            if self.collection.count() == 0:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            # Format return results
            conversations = []
            if results.get('metadatas') and len(results['metadatas']) > 0:
                metadatas = results['metadatas'][0]
                distances = results.get('distances', [[]])[0] if results.get('distances') else [0.0] * len(metadatas)
                
                for i, metadata in enumerate(metadatas):
                    distance = distances[i] if i < len(distances) else 0.0
                    conversations.append({
                        "user_message": metadata.get("user_message", ""),
                        "ai_response": metadata.get("ai_response", ""),
                        "timestamp": metadata.get("timestamp", ""),
                        "relevance_score": max(0.0, 1.0 - distance)  # Convert cosine distance to similarity
                    })
            
            return conversations
        except Exception as e:
            print(f"✗ Failed to search conversations: {e}")
            return []
    
    def get_conversation_count(self) -> int:
        """Get total number of stored conversations"""
        try:
            return self.collection.count()
        except Exception:
            return 0
    
    def clear_all(self):
        """Clear all conversations (for testing)"""
        try:
            self.client.delete_collection(name="conversation_memory")
            self.collection = self.client.get_or_create_collection(
                name="conversation_memory",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ Cleared all conversations from vector store")
        except Exception as e:
            print(f"✗ Failed to clear conversations: {e}")

