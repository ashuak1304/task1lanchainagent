from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from langchain import PromptTemplate, LLMChain
from langchain.llms import HuggingFacePipeline

class LLMService:
    def __init__(self):
        # Initialize the model and tokenizer
        model_name = "gpt2"  # You can change this to a more advanced model if needed
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, from_tf=True)

        
        # Create a HuggingFacePipeline
        self.pipeline = HuggingFacePipeline(pipeline=self.create_pipeline())
        
    def create_pipeline(self):
        def model_func(prompt):
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            with torch.no_grad():
                output = self.model.generate(input_ids, max_length=150)
            return self.tokenizer.decode(output[0], skip_special_tokens=True)
        return model_func

    def analyze_email(self, email):
        """Analyze email content and extract key information"""
        template = """
        Analyze the following email and extract key information:
        Email: {email_content}
        Key points:
        1.
        2.
        3.
        """
        prompt = PromptTemplate(template=template, input_variables=["email_content"])
        llm_chain = LLMChain(prompt=prompt, llm=self.pipeline)
        return llm_chain.run(email_content=email.body_text)

    def generate_reply(self, email):
        """Generate a reply to the given email"""
        template = """
        Generate a polite and professional reply to the following email:
        Email: {email_content}
        Reply:
        """
        prompt = PromptTemplate(template=template, input_variables=["email_content"])
        llm_chain = LLMChain(prompt=prompt, llm=self.pipeline)
        return llm_chain.run(email_content=email.body_text)

    def summarize_email(self, email):
        """Summarize the content of an email"""
        template = """
        Summarize the following email in a concise manner:
        Email: {email_content}
        Summary:
        """
        prompt = PromptTemplate(template=template, input_variables=["email_content"])
        llm_chain = LLMChain(prompt=prompt, llm=self.pipeline)
        return llm_chain.run(email_content=email.body_text)

    def extract_action_items(self, email):
        """Extract action items from an email"""
        template = """
        Extract action items from the following email:
        Email: {email_content}
        Action items:
        1.
        2.
        3.
        """
        prompt = PromptTemplate(template=template, input_variables=["email_content"])
        llm_chain = LLMChain(prompt=prompt, llm=self.pipeline)
        return llm_chain.run(email_content=email.body_text)

    def detect_intent(self, email):
        """Detect the intent of an email"""
        template = """
        Determine the primary intent of the following email:
        Email: {email_content}
        Intent:
        """
        prompt = PromptTemplate(template=template, input_variables=["email_content"])
        llm_chain = LLMChain(prompt=prompt, llm=self.pipeline)
        return llm_chain.run(email_content=email.body_text)
