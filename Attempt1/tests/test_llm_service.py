import unittest
from unittest.mock import patch, MagicMock
import os
import torch
from services.llm_service import LLMService
from models.email_model import Email

class TestLLMService(unittest.TestCase):
    """Test cases for the LLMService class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Mock the model initialization to avoid loading actual models
        with patch('services.llm_service.AutoTokenizer'), \
             patch('services.llm_service.AutoModelForCausalLM'):
            self.llm_service = LLMService()
        
        # Create a sample email for testing
        self.sample_email = Email()
        self.sample_email.subject = "Meeting Tomorrow"
        self.sample_email.sender = "colleague@example.com"
        self.sample_email.body_text = """
        Hi Team,
        
        Let's have a meeting tomorrow at 2 PM to discuss the project progress.
        Please bring your status updates and any blockers you're facing.
        
        Best regards,
        John
        """
    
    @patch('services.llm_service.LLMChain')
    def test_analyze_email(self, mock_llm_chain):
        """Test analyzing email content"""
        # Mock LLMChain
        mock_chain = MagicMock()
        mock_llm_chain.return_value = mock_chain
        mock_chain.run.return_value = "Key points:\n1. Meeting scheduled tomorrow\n2. Time: 2 PM\n3. Topic: Project progress"
        
        # Call the method
        result = self.llm_service.analyze_email(self.sample_email)
        
        # Assertions
        mock_llm_chain.assert_called_once()
        mock_chain.run.assert_called_once_with(email_content=self.sample_email.body_text)
        self.assertEqual(result, "Key points:\n1. Meeting scheduled tomorrow\n2. Time: 2 PM\n3. Topic: Project progress")
    
    @patch('services.llm_service.LLMChain')
    def test_generate_reply(self, mock_llm_chain):
        """Test generating a reply to an email"""
        # Mock LLMChain
        mock_chain = MagicMock()
        mock_llm_chain.return_value = mock_chain
        mock_chain.run.return_value = "Hi John,\n\nThank you for the invitation. I'll be there with my status update.\n\nBest regards,\nMe"
        
        # Call the method
        result = self.llm_service.generate_reply(self.sample_email)
        
        # Assertions
        mock_llm_chain.assert_called_once()
        mock_chain.run.assert_called_once_with(email_content=self.sample_email.body_text)
        self.assertEqual(result, "Hi John,\n\nThank you for the invitation. I'll be there with my status update.\n\nBest regards,\nMe")
    
    @patch('services.llm_service.LLMChain')
    def test_summarize_email(self, mock_llm_chain):
        """Test summarizing an email"""
        # Mock LLMChain
        mock_chain = MagicMock()
        mock_llm_chain.return_value = mock_chain
        mock_chain.run.return_value = "Team meeting scheduled for tomorrow at 2 PM to discuss project progress."
        
        # Call the method
        result = self.llm_service.summarize_email(self.sample_email)
        
        # Assertions
        mock_llm_chain.assert_called_once()
        mock_chain.run.assert_called_once_with(email_content=self.sample_email.body_text)
        self.assertEqual(result, "Team meeting scheduled for tomorrow at 2 PM to discuss project progress.")
    
    @patch('services.llm_service.LLMChain')
    def test_extract_action_items(self, mock_llm_chain):
        """Test extracting action items from an email"""
        # Mock LLMChain
        mock_chain = MagicMock()
        mock_llm_chain.return_value = mock_chain
        mock_chain.run.return_value = "Action items:\n1. Attend meeting tomorrow at 2 PM\n2. Prepare status update\n3. Identify blockers"
        
        # Call the method
        result = self.llm_service.extract_action_items(self.sample_email)
        
        # Assertions
        mock_llm_chain.assert_called_once()
        mock_chain.run.assert_called_once_with(email_content=self.sample_email.body_text)
        self.assertEqual(result, "Action items:\n1. Attend meeting tomorrow at 2 PM\n2. Prepare status update\n3. Identify blockers")
    
    @patch('services.llm_service.LLMChain')
    def test_detect_intent(self, mock_llm_chain):
        """Test detecting the intent of an email"""
        # Mock LLMChain
        mock_chain = MagicMock()
        mock_llm_chain.return_value = mock_chain
        mock_chain.run.return_value = "Intent: Meeting invitation"
        
        # Call the method
        result = self.llm_service.detect_intent(self.sample_email)
        
        # Assertions
        mock_llm_chain.assert_called_once()
        mock_chain.run.assert_called_once_with(email_content=self.sample_email.body_text)
        self.assertEqual(result, "Intent: Meeting invitation")
    
    def test_create_pipeline(self):
        """Test creating the pipeline function"""
        # Call the method
        pipeline_func = self.llm_service.create_pipeline()
        
        # Check that it's a callable
        self.assertTrue(callable(pipeline_func))

if __name__ == '__main__':
    unittest.main()
