import openai

model = "gpt-4o-mini"

client = openai.Client()

def generate_fake_article():
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

    messages = [
        {"role": "system", "content": requirements},
        {"role": "user", "content": "Generate one title and subtitle pair."}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=50
    ).choices[0].message.content.strip()

    # Split the response into title and subtitle
    title, subtitle = response.split("\n")

    content_requirements = f"""
    Write a short piece, fiction or non-fiction, any style, using the given title and subtitle. The first line should be the title of the essay, the second line should be the subtitle, and the third line should be blank. The rest of the content should be the body of the essay. Neither the title nor subtitle should have any formatting. The content itself can have markdown. Here is the title and subtitle to use:

    {title}
    {subtitle}

    For example:

    The History of the Internet
    A Brief Overview

    The internet has a long and storied history. It began as a research project in the 1960s and has since grown into a global network that connects billions of people around the world. The internet has revolutionized the way we communicate, work, and play. It has changed the way we access information, conduct business, and interact with one another. The internet has brought the world closer together and made it easier than ever to connect with people from all walks of life. In this essay, we will explore the history of the internet and its impact on society.
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

