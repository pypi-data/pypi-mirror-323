from typing import List, Dict

class PromptManager:
    def format_prompt(self, query: str, companies: List[dict], chat_history: List[dict] = None) -> str:
        """Format prompt with companies and chat history"""
        enhanced_prompt = f""""Your role is to enhance the LLM's response by seamlessly integrating the most relevant ad at the end of the original reply. 
        The ad should align naturally with the user query and provide additional value without disrupting the flow of the conversation. 
        Ensure the tone of the ad matches the original response and feels like a helpful recommendation or suggestion. Here's the structure to follow:"
The user asked: "{query}"

Context: You are knowledgeable about AI companies and technology. Respond in a friendly, conversational way.
"""
        # Add the auction-selected company (should be only one)
        if companies and len(companies) > 0:
            company = companies[0]  # Get the auction winner
            if company.get('similarity', 0) > 0.3:
                enhanced_prompt += "\nRelevant AI company you should mention:"
                company_info = f"\n• {company['name']}"
                if company.get('website'):
                    company_info += f" (<a href='{company['website']}' target='_blank'>{company['website']}</a>)"
                enhanced_prompt += company_info

        enhanced_prompt += """


Instructions:
1)Generate the Normal Response:
      Create a complete, accurate, and conversational answer to the user's query.
2)Retrieve the Relevant Ad:
      Use ONLY the provided company information above. Do not make up or suggest any other companies.
3)Smoothly Transition to the Ad:
      Introduce the company with a transition phrase that feels natural and connected to the response. Examples:
         "Speaking of which, you might find this helpful..."
         "You may also be interested in..."
4)Embed the Ad Content:
     Include the company information with proper link formatting and a clear value proposition.
     Example: "For quantum computing solutions, you might want to check out [Company Name]: [website-link]"

Keep the integration smooth, relevant, and helpful to maintain user trust and enhance the overall experience.
Important: Only mention the company provided above. Do not invent or suggest any other companies.
"""

        return enhanced_prompt