from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Dict, List
from datetime import datetime
import pandas as pd
import numpy as np
from .config import get_credentials
# import bcrypt

class DatabaseManager:
    def __init__(self):
        try:
            # Get credentials using existing config
            credentials = get_credentials()
            
            # Decode/decrypt the credentials here
            self.supabase_url = credentials.get("url")  
            self.supabase_key = credentials.get("key")
            
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Missing Supabase credentials")
                
            # Make sure the key is clean (no quotes or whitespace)
            self.supabase_key = self.supabase_key.strip().strip('"\'')
            
            # Initialize Supabase client
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            
            # print("Successfully connected to Supabase")
            
        except Exception as e:
            # print(f"Error initializing database: {e}")
            raise

    def get_companies(self):
        """Get all companies from ads table"""
        try:
            # Remove access from selection
            response = self.supabase.table('ads').select(
                'id, name, website, description, category, embedding, views'
            ).execute()
            
            # print(f"Retrieved {len(response.data)} companies")
            
            df = pd.DataFrame(response.data)
            
            # Check for records with null embeddings
            null_embeddings = df[df['embedding'].isna()]
            if not null_embeddings.empty:
                # print(f"Found {len(null_embeddings)} records without embeddings")
                embedding_columns = null_embeddings[['id', 'name', 'website', 'description', 'category']]
                self.update_missing_embeddings(embedding_columns)
                
                # Refresh data without access column
                response = self.supabase.table('ads').select(
                    'id, name, website, description, category, embedding, views'
                ).execute()
                df = pd.DataFrame(response.data)
            
            return df
            
        except Exception as e:
            # print(f"Error getting companies: {e}")
            return pd.DataFrame()

    def store_all_embeddings(self, companies: pd.DataFrame, embeddings: np.ndarray) -> bool:
        """Store embeddings directly in ads table"""
        try:
            for i, (_, company) in enumerate(companies.iterrows()):
                # Only update the embedding column
                self.supabase.table('ads').update({
                    'embedding': embeddings[i].tolist()
                }).eq('id', company['id']).execute()
                
            # print(f"Successfully stored {len(companies)} embeddings")
            return True
        except Exception as e:
            # print(f"Error storing embeddings: {e}")
            return False

    def search_similar_companies(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar companies using vector similarity"""
        try:
            # print(f"Searching for similar companies with embedding of length {len(query_embedding)}")  # Debug log
            
            # Get candidates for auction with debug logging
            # print("Executing database query...")  # Debug log
            response = self.supabase.rpc(
                'match_ads',
                {
                    'query_embedding': query_embedding,
                    'match_count': top_k,
                    'similarity_threshold': 0.1
                }
            ).execute()
            
            # print(f"Database response: {response.data}")  # Debug log
            
            if not response.data:
                # print("No companies found in database")  # Debug log
                return []
            
            # Prepare companies with similarities and bids
            results = []
            for item in response.data:
                if item.get('similarity', 0) > 0.3:  # Minimum similarity threshold
                    company = {
                        'id': item['id'],
                        'name': str(item['name']),
                        'website': str(item['website']) if item.get('website') else None,
                        'similarity': float(item['similarity']),
                        'bid': float(item['bid']) if item.get('bid') else 0.0
                    }
                    # print(f"Found company: {company}")  # Debug log
                    results.append(company)
            
            # print(f"Returning {len(results)} companies")  # Debug log
            return results
            
        except Exception as e:
            # print(f"Error searching similar companies: {e}")
            # print(f"Full error details: {str(e)}")
            return []

    def increment_views(self, companies: List[Dict]):
        """Increment view count for companies mentioned in response"""
        try:
            for company in companies:
                company_name = company.get('name', '')
                if not company_name:
                    continue
                    
                # print(f"Incrementing views for: {company_name}")  # Debug log
                
                # Get current views
                response = self.supabase.table('ads') \
                    .select('views') \
                    .eq('name', company_name) \
                    .execute()
                
                if response.data:
                    current_views = response.data[0].get('views', 0)
                    
                    # Update views count
                    update_response = self.supabase.table('ads') \
                        .update({'views': current_views + 1}) \
                        .eq('name', company_name) \
                        .execute()
                    
                    # print(f"Updated views for {company_name}: {current_views + 1}")  # Debug log
                    
                    # Log the view
                    self.insert_analytics_log(company_name, 'view')
                
            return True
            
        except Exception as e:
            # print(f"Error incrementing views: {e}")
            return False

    def insert_analytics_log(self, company_name: str, interaction_type: str = 'view'):
        """Insert analytics log for views"""
        try:
            if not company_name or not isinstance(company_name, str):
                return
            
            # print(f"Logging view for: {company_name}")  # Debug log
            
            self.supabase.table('analytics_logs').insert({
                'company_name': company_name,
                'interaction_type': interaction_type,
                'timestamp': datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            # print(f"Error inserting analytics log: {e}")
            pass  # Added pass statement

    def update_missing_embeddings(self, companies: pd.DataFrame):
        """Update embeddings for companies with null embeddings"""
        try:
            from .embeddings import EmbeddingManager
            embedding_manager = EmbeddingManager()
            
            # Create embeddings for companies
            embeddings = embedding_manager.create_embeddings(companies)
            
            # Update each company with its new embedding
            for i, (_, company) in enumerate(companies.iterrows()):
                self.supabase.table('ads').update({
                    'embedding': embeddings[i].tolist()
                }).eq('id', company['id']).execute()
                
            # print(f"Updated embeddings for {len(companies)} companies")
            
        except Exception as e:
            # print(f"Error updating missing embeddings: {e}")
            pass  # Added pass statement
    def verify_api_key(self, api_key: str) -> bool:
        """Verify if the API key is valid and not revoked"""
        if not api_key:
            print("No API key provided")
            return False
        
        try:
            # Clean up the key
            api_key = api_key.strip().strip('"\'')
            
            # print(f"Attempting to verify key: {api_key}")
            
            response = self.supabase.table('api_keys') \
                .select('id, key, revoked_at') \
                .eq('key', api_key) \
                .execute()
            
            # print(f"Full query response: {response}")
            # print(f"Response data: {response.data}")
            
            if response.data and len(response.data) > 0:
                key_data = response.data[0]
                # print(f"Found key data: {key_data}")
                is_valid = key_data.get('revoked_at') is None
                
                if is_valid:
                    print(f"Valid API key verified")
                    return True
                else:
                    print("Key found but was revoked")
                    return False
            
            print("No matching key found in database")
            return False
                
        except Exception as e:
            # print(f"Error verifying API key: {e}")
            # print(f"Full error details: {str(e)}")
            return False