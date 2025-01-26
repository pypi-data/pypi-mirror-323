from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict
import numpy as np
import pandas as pd

class EmbeddingManager:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    
    def create_embeddings(self, df: pd.DataFrame) -> np.ndarray:
        """Create embeddings for all companies"""
        try:
            texts = []
            for _, row in df.iterrows():
                # Combine all available information for better matching
                text_parts = []
                
                # Add name if available
                if 'name' in row and pd.notna(row['name']):
                    text_parts.append(f"Company Name: {row['name']}")
                
                # Add description if available
                if 'description' in row and pd.notna(row['description']):
                    text_parts.append(f"Description: {row['description']}")
                
                # Add website if available
                if 'website' in row and pd.notna(row['website']):
                    text_parts.append(f"Website: {row['website']}")
                
                text = " | ".join(text_parts)
                texts.append(text)
            
            # print(f"Creating embeddings for {len(texts)} texts")
            embeddings = self.model.embed_documents(texts)
            return np.array(embeddings)
        
        except Exception as e:
            # print(f"Error creating embeddings: {e}")
            return np.array([])
    
    def get_similarities(self, query: str, company_embeddings: np.ndarray) -> np.ndarray:
        """Calculate similarities between query and companies"""
        try:
            query_embedding = self.model.embed_query(query)
            query_embedding = np.array(query_embedding)
            
            # Calculate cosine similarity
            similarities = np.dot(company_embeddings, query_embedding) / (
                np.linalg.norm(company_embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Handle NaN values if any
            similarities = np.nan_to_num(similarities, 0)
            
            return similarities
        except Exception as e:
            # print(f"Error calculating similarities: {e}")
            return np.array([])
        

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a single piece of text"""
        try:
            # Enhance query for better matching
            enhanced_query = f"Find AI companies related to: {text}"
            embedding = self.model.embed_query(enhanced_query)
            return np.array(embedding)
        except Exception as e:
            # print(f"Error embedding query: {e}")
            return np.array([])
    
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts"""
        try:
            embeddings = self.model.embed_documents(texts)
            return np.array(embeddings)
        except Exception as e:
            # print(f"Error embedding documents: {e}")
            return np.array([])

