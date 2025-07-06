import os
import openai
from typing import List
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class EmbeddingGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "text-embedding-ada-002")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using OpenAI API
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using OpenAI API
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise Exception(f"Error generating embeddings batch: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the current model
        """
        # OpenAI text-embedding-ada-002 has 1536 dimensions
        if self.model == "text-embedding-ada-002":
            return 1536
        else:
            # For other models, we'll need to generate a test embedding
            test_embedding = self.generate_embedding("test")
            return len(test_embedding) 