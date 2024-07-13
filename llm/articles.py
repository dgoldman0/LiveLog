import openai

client = openai.Client()

model = "gpt-4o"

tag_prompt = """You are an article tag generator.
Tags can be one to three words and can be informative, genre-related, topic-related, or style-related.

Include examples such as "technology trends, AI development, digital art, sustainable living, health tips,
creative writing, education strategies, social media, mental health awareness, renewable energy, historical analysis,
cooking recipes, travel guides, environmental conservation, personal finance, fitness routines, literary criticism,
fashion trends, space exploration, cybersecurity, startup culture, photography tips, film reviews, parenting advice, language learning,
virtual reality, ethical hacking, mindfulness practices, urban planning, cultural heritage, financial markets, DIY projects,
climate change, political commentary, robotics advancements, biotechnology, blockchain technology, philosophical debates,
interior design, wilderness survival, game development, online privacy, oceanography, modern art, culinary techniques,
wildlife conservation, renewable resources, ancient civilizations, digital marketing, entrepreneurial tips, sustainable architecture,
public health, social justice, quantum computing, alternative medicine, space missions, agricultural innovations, music theory,
relationship advice, automotive technology, science fiction, fantasy worlds, dystopian futures, epic adventures, magical realism,
speculative fiction, space opera, urban fantasy, post-apocalyptic, time travel, alien encounters, parallel universes,
supernatural beings, steampunk, cyberpunk, mythological tales, heroic quests, dark fantasy, alternate history, futuristic societies,
supernatural horror.

Give a list of comma-separated tags based on the article provided.
"""

def generate_tags(content, existing_tags=None):
    messages = [{"role": "system", "content": tag_prompt}]
    if existing_tags:
        tag_info = ', '.join([f"{tag} ({count})" for tag, count in existing_tags.items()])
        messages.append({"role": "user", "content": f"Existing Tags Across All Articles {tag_info}\n\nUse these tags as inspiration to generate new tags."})
    messages.append({"role": "user", "content": content})

    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        ).choices[0].message.content.strip().split(',')
    
    return response

def generate_tldr(content):
    messages = [{"role": "system", "content": "You are a TLDR generator. Give a short summary of the article given."}, {"role": "user", "content": content}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        ).choices[0].message.content.strip()
    
    return response