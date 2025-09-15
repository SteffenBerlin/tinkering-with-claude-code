#!/usr/bin/env python3
"""
Simple Research Agent Runner

This script provides an easy way to use the research agent.
Just run it and enter your research query!
"""

from src.research_agent import research_agent, ResearchAgentDependencies
from src.settings import settings

def main():
    print("🔍 Simple Research Agent")
    print("=" * 40)
    
    try:
        # Create agent dependencies
        deps = ResearchAgentDependencies(
            brave_api_key=settings.brave_api_key,
            session_id="research_session"
        )
        
        # Get user query
        query = input("\nWhat would you like to research? ")
        
        if not query.strip():
            print("Please enter a valid research query.")
            return
            
        # Run the research
        print(f"\n🔍 Researching: {query}")
        print("Please wait...")
        
        result = research_agent.run_sync(query, deps=deps)
        
        print("\n" + "=" * 60)
        print("📊 RESEARCH RESULTS:")
        print("=" * 60)
        print(result.output)
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTips:")
        print("- Make sure you have added your API keys to the .env file")
        print("- Check that you have internet connection")
        print("- Verify your Brave API key is valid")

if __name__ == "__main__":
    main()