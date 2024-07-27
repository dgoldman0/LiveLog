import openai

model = "gpt-4o-mini"

client = openai.Client()

def generate_fake_article(current_list = None):
    requirements = """
    You are a title and subtitle pair generator. The following are examples. The title and subtitle can be any topic at all, fiction, non-fiction, fantasy, it does not matter.

    Examples:

    Echoes of the Past
    Uncovering Ancient Civilizations

    Quantum Realities
    Exploring the Mysteries of the Universe

    Culinary Journeys
    A Tour of Global Flavors

    The Art of Mindfulness
    Finding Peace in a Hectic World

    Digital Nomads
    The New Age of Remote Work

    Beyond the Horizon
    Adventures in Space Exploration

    Whispers of the Wild
    Conservation Stories from the Animal Kingdom

    The Human Genome
    Unlocking the Secrets of Our DNA
    
    The title and subtitle should be in plain text."""

    pairs = ""
    if current_list and len(current_list) > 0:
        for title, subtitle in current_list:
            pairs += f"{title}\n{subtitle}\n"
    messages = [
        {"role": "system", "content": requirements},
        {"role": "assistant", "content": f"Current title and subtitle pairs:{pairs}\n"},
        {"role": "user", "content": "Generate one new title and subtitle pair."}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=50
    ).choices[0].message.content.strip()

    # Split the response into title and subtitle
    title, subtitle = response.split("\n")

    content_requirements = f"""
    Write a short piece, fiction or non-fiction, any style, using the given title and subtitle. Here is the title and subtitle to use:

    {title}
    {subtitle}

    Write just the content based on the title and subtitle. You may use markdown.
    """

    messages = [
        {"role": "system", "content": "You are a content generator. Generate a short piece using the given title and subtitle."},
        {"role": "user", "content": content_requirements}
    ]

    content = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2000
    ).choices[0].message.content.strip()

    return title, subtitle, content

