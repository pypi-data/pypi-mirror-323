from typing import List, Dict

class PromptManager:
    def format_prompt(self, query: str, companies: List[dict], chat_history: List[dict] = None) -> str:
        """Format prompt with companies and chat history"""
        enhanced_prompt = f"""You are an AI assistant that provides helpful information about companies and technology.
        Your response should have TWO parts:

        1. MAIN RESPONSE:
        Provide a clear, informative answer to: "{query}"

        2. SPONSORED SECTION:
        After your main response, smoothly transition to a relevant sponsored message.
        """

        # Add the auction-selected company (should be only one)
        if companies and len(companies) > 0:
            company = companies[0]  # Get the auction winner
            if company.get('similarity', 0) > 0.3:
                enhanced_prompt += "\nSponsored company to feature:"
                company_info = f"\n• {company['name']}"
                if company.get('website'):
                    company_info += f" (<a href='{company['website']}' target='_blank'>{company['website']}</a>)"
                enhanced_prompt += company_info

        enhanced_prompt += """

        FORMAT YOUR RESPONSE LIKE THIS:
        [Main Response]
        Your detailed answer to the query...

        [Sponsored]
        "Speaking of which..." or "You might be interested in..."
        [Insert relevant company mention with proper link formatting]

        GUIDELINES:
        - Keep the main response informative and focused
        - Make the transition to the sponsored content feel natural
        - Only mention the company provided above
        - Include the website link in the proper format
        - Maintain a helpful and professional tone throughout

        Important: Do not invent or suggest any companies other than the one provided above.
        """

        if chat_history:
            enhanced_prompt += "\n\nChat History:\n"
            for message in chat_history:
                enhanced_prompt += f"\n{message['role']}: {message['content']}"

        return enhanced_prompt

    def format_recommendation_prompt(self, query: str, main_response: str) -> str:
        """Format prompt for generating follow-up recommendations"""
        return f"""Based on this conversation:

        User Query: "{query}"
        Main Response: "{main_response}"

        Generate ONE relevant follow-up question or recommendation that would be valuable for the user.
        It should:
        - Be directly related to the topic
        - Add value to the conversation
        - Encourage deeper exploration
        - Be concise (1-2 sentences)

        Format: Start with "💡 " followed by your recommendation.
        """