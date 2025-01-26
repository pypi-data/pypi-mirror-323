from typing import Optional
from vaklm import vaklm
from vaklm import VAKLMException

class DeepseekReasonExtractor:
    def __init__(self, 
                 endpoint: str = "https://api.deepseek.com",
                 model_name: str = "deepseek-reasoner",
                 api_key: str = None,
                 system_prompt: str = "You are an expert reasoning extractor"):
        """Initialize the Deepseek Reason Extractor
        
        Args:
            endpoint: Vaklm API endpoint
            model_name: Name of the model to use
            api_key: API key for authentication
            system_prompt: System prompt for the model
        """
        self.endpoint = endpoint
        self.model_name = model_name
        self.api_key = api_key
        self.system_prompt = system_prompt

    def extract_reasoning(self, prompt: str, temperature: float = 0.7) -> str:
        """Extract reasoning content using Vaklm
        
        Args:
            prompt: The input prompt for reasoning
            temperature: Sampling temperature for generation
            
        Returns:
            The generated reasoning content as a string
        """
        try:
            response = vaklm(
                endpoint=self.endpoint,
                model_name=self.model_name,
                user_prompt=prompt,
                system_prompt=self.system_prompt,
                api_key=self.api_key,
                temperature=temperature,
                max_tokens=1
            )
            return response
        except VAKLMException as e:
            raise RuntimeError(f"Failed to extract reasoning: {str(e)}")
