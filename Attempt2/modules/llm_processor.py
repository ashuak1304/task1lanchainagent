import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from transformers import BitsAndBytesConfig
from typing import Dict, Any, List, Optional
import uuid

from config import LLM_MODEL_ID, USE_4BIT_QUANTIZATION, MAX_NEW_TOKENS, TEMPERATURE

class LLMProcessor:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipe = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Transformer model."""
        print(f"Initializing LLM with model: {LLM_MODEL_ID}")
        
        # Configure quantization if enabled
        if USE_4BIT_QUANTIZATION and torch.cuda.is_available():
            print("Using 4-bit quantization")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            
            # Load model with quantization
            self.tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID)
            self.model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL_ID,
                device_map="auto",
                quantization_config=quantization_config,
                trust_remote_code=True
            )
        else:
            print("Using standard model loading (no quantization)")
            self.tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID)
            self.model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL_ID,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
        
        # Create pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True
        )
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using the model."""
        result = self.pipe(prompt)
        return result[0]['generated_text'].replace(prompt, "").strip()
    
    def classify_email(self, email_content: str) -> str:
        """Classify an email's intent and required action."""
        prompt = f"""
        Email: {email_content}
        
        Classify this email into one of the following categories:
        1. Meeting Request - Requires scheduling
        2. Question - Requires information
        3. Task - Requires an action
        4. FYI - Just informational
        
        Category and explanation:
        """
        
        return self.generate_text(prompt)
    
    def summarize_email(self, email_content: str) -> str:
        """Summarize an email's content."""
        prompt = f"""
        Email: {email_content}
        
        Provide a concise summary of this email in 1-2 sentences:
        """
        
        return self.generate_text(prompt)
    
    def generate_response(self, email_content: str, sender: str, context: Optional[str] = None) -> str:
        """Generate a response to an email."""
        context_section = f"Additional context: {context}" if context else "No additional context provided."
        
        prompt = f"""
        Email from {sender}: {email_content}
        
        {context_section}
        
        Draft a professional and concise response addressing their questions or requests:
        """
        
        return self.generate_text(prompt)
    
    def extract_meeting_details(self, email_content: str) -> Dict[str, Any]:
        """Extract meeting details from an email."""
        prompt = f"""
        Email: {email_content}
        
        Extract the following meeting details from this email:
        - Date (YYYY-MM-DD format)
        - Time (HH:MM format, specify timezone if mentioned)
        - Duration (in minutes)
        - Title or Subject
        - Participants (comma-separated list)
        - Location (physical or virtual)
        
        Format your response as:
        Date: [date]
        Time: [time]
        Duration: [duration]
        Title: [title]
        Participants: [participants]
        Location: [location]
        """
        
        result = self.generate_text(prompt)
        
        # Parse the result into a dictionary
        meeting_details = {}
        for line in result.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                meeting_details[key.strip()] = value.strip()
        
        return meeting_details
    
    def generate_search_query(self, email_content: str) -> str:
        """Generate a search query based on email content."""
        prompt = f"""
        Email: {email_content}
        
        Generate a concise search query to find information that would help respond to this email:
        """
        
        return self.generate_text(prompt)
