"""
Load testing script - Using Locust
Simulates concurrent users to test AI Desktop Pet performance

Usage:
1. Local testing:
   - Ensure backend service is running at http://localhost:8080
   - Run: locust -f tests/load/locustfile.py --host=http://localhost:8080

2. Kubernetes testing:
   - From outside cluster: Use NodePort or port-forward
   - From inside cluster: Use Service name http://desktop-pet-service:8080
   - Run: locust -f tests/load/locustfile.py --host=http://desktop-pet-service:8080

3. Ensure Mock AI Provider is used (USE_MOCK_AI=true) to avoid consuming API tokens
"""

from locust import HttpUser, task, between
import json
import random
import os


class DesktopPetUser(HttpUser):
    """Simulates desktop pet user"""
    
    wait_time = between(1, 3)  # User operation interval 1-3 seconds
    
    def on_start(self):
        """Initialize when user starts"""
        # Support reading host from environment variable for Kubernetes environment
        host = os.getenv('LOCUST_HOST')
        if host:
            self.host = host
        self.user_id = f"test_user_{random.randint(1000, 9999)}"
        self.conversation_id = None
    
    @task(3)
    def send_message(self):
        """Send message (weight 3, more frequent)"""
        messages = [
            "Hello, how are you?",
            "What's the weather like?",
            "Tell me a joke",
            "How can you help me?",
            "What do you remember about me?",
            "你好",
            "今天天气怎么样？",
            "我有点累",
            "给我讲个笑话",
            "What's your favorite color?",
            "Can you help me with my work?",
            "I'm feeling stressed today",
        ]
        
        payload = {
            "user_id": self.user_id,
            "message": random.choice(messages)
        }
        
        with self.client.post(
            "/api/v1/chat",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get("conversation_id")
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def get_conversation(self):
        """Get conversation history (weight 1)"""
        self.client.get(f"/api/v1/conversation/{self.user_id}")
    
    @task(1)
    def get_profile(self):
        """Get user profile (weight 1)"""
        self.client.get(f"/api/v1/profile/{self.user_id}")
    
    @task(1)
    def health_check(self):
        """Health check (weight 1)"""
        self.client.get("/health")

