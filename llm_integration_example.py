#!/usr/bin/env python3
"""
LLM Integration Example
Demonstrates how to use crawled data for AI-powered visa Q&A
"""

import json


class VisaKnowledgeBase:
    """Simple knowledge base for visa information"""
    
    def __init__(self, data_path='data/crawled_pages.json'):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.pages = json.load(f)
        
        print(f"📚 Loaded {len(self.pages)} pages into knowledge base")
    
    def search_by_country(self, country):
        """Find all pages for a specific country"""
        return [p for p in self.pages if p['country'].lower() == country.lower()]
    
    def search_by_keywords(self, keywords):
        """Find pages containing specific keywords"""
        results = []
        for page in self.pages:
            content = (page['title'] + ' ' + page['content_text']).lower()
            if any(kw.lower() in content for kw in keywords):
                results.append(page)
        return results
    
    def get_visa_types(self, country):
        """Extract visa types for a country"""
        pages = self.search_by_country(country)
        visa_types = set()
        
        for page in pages:
            if 'visa' in page['tags']:
                # Extract visa type from title
                title = page['title']
                if 'visa' in title.lower():
                    visa_types.add(title)
        
        return list(visa_types)
    
    def build_context_for_llm(self, query_country, query_keywords):
        """Build context string for LLM prompt"""
        
        # Find relevant pages
        country_pages = self.search_by_country(query_country)
        keyword_pages = self.search_by_keywords(query_keywords)
        
        # Combine and deduplicate
        relevant_pages = list({p['url']: p for p in (country_pages + keyword_pages)}.values())
        
        # Build context
        context_parts = []
        for page in relevant_pages[:5]:  # Limit to top 5 for token efficiency
            context_parts.append(f"""
Source: {page['url']}
Title: {page['title']}
Country: {page['country']}
Content: {page['content_text'][:1000]}...
Tags: {', '.join(page['tags'])}
---
""")
        
        return '\n'.join(context_parts)


def create_llm_prompt(user_question, knowledge_base):
    """Create a complete LLM prompt with context"""
    
    # Parse user question to extract country and keywords
    # (In real implementation, use NLP or ask user)
    country = "Australia"  # Example
    keywords = ["skilled", "visa", "eligibility"]  # Example
    
    # Build context from knowledge base
    context = knowledge_base.build_context_for_llm(country, keywords)
    
    # Create prompt
    prompt = f"""You are an immigration visa expert assistant. Use the following verified information from official immigration websites to answer the user's question accurately.

CONTEXT FROM OFFICIAL SOURCES:
{context}

USER QUESTION:
{user_question}

INSTRUCTIONS:
1. Answer the question based ONLY on the provided context
2. Cite the specific source URL for any claims you make
3. If the context doesn't contain enough information, say so clearly
4. Provide step-by-step guidance if the user is asking about applying
5. Mention any important requirements or conditions
6. Be clear about what is eligibility criteria vs. application process

ANSWER:
"""
    
    return prompt


def demonstrate_llm_integration():
    """Show how to use crawled data for LLM Q&A"""
    
    print("🧠 LLM Integration Demo\n")
    print("=" * 60)
    
    # Load knowledge base
    kb = VisaKnowledgeBase('data/example_output.json')
    
    # Example query
    user_question = "Am I eligible for a skilled worker visa in Australia if I'm 32 years old with a master's degree in computer science?"
    
    print(f"\n❓ User Question:\n{user_question}\n")
    
    # Create LLM prompt
    prompt = create_llm_prompt(user_question, kb)
    
    print("📝 Generated LLM Prompt:\n")
    print(prompt[:1500] + "...\n")
    
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("   1. Send this prompt to OpenAI API, Anthropic Claude, or local LLM")
    print("   2. The LLM will generate an answer with source citations")
    print("   3. Display answer to user with clickable source links")
    print("   4. Allow user to ask follow-up questions")
    
    print("\n🎯 Integration Options:")
    print("   • LangChain: Chain multiple prompts for complex queries")
    print("   • Vector DB: Use embeddings for semantic search")
    print("   • RAG: Retrieve relevant chunks dynamically")
    print("   • Fine-tuning: Train model on immigration domain")


def demonstrate_search():
    """Show knowledge base search capabilities"""
    
    print("\n\n🔍 Knowledge Base Search Demo\n")
    print("=" * 60)
    
    kb = VisaKnowledgeBase('data/example_output.json')
    
    # Search by country
    print("\n📍 Searching for Australia visas...")
    aus_pages = kb.search_by_country("Australia")
    print(f"   Found {len(aus_pages)} pages")
    for page in aus_pages[:3]:
        print(f"   • {page['title']}")
    
    # Search by keywords
    print("\n🔑 Searching for 'skilled' + 'eligibility'...")
    keyword_pages = kb.search_by_keywords(['skilled', 'eligibility'])
    print(f"   Found {len(keyword_pages)} pages")
    for page in keyword_pages[:3]:
        print(f"   • {page['title']} ({page['country']})")
    
    # Get visa types
    print("\n📋 Available visa types in Canada...")
    visa_types = kb.get_visa_types("Canada")
    for vtype in visa_types:
        print(f"   • {vtype}")


if __name__ == '__main__':
    demonstrate_llm_integration()
    demonstrate_search()
    
    print("\n" + "=" * 60)
    print("✨ Demo complete!")
