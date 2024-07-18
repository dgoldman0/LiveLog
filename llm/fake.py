import openai

model = "gpt-4o-mini"

client = openai.Client()

def generate_fake_article():

    """You are a content generator. Write a short essay, fiction or non-fiction, any style. The first line should be the title of the essay, the second line should be the subtitle, and the third line should be blank. The rest of the content should be the body of the essay. Neither the title nor subtitle should have any formatting. For example:

    Title
    Subtitle

    [Content]

    Example.

    Title: The History of the Internet
    Subtitle: A Brief Overview

    The internet has a long and storied history. It began as a research project in the 1960s and has since grown into a global network that connects billions of people around the world. The internet has revolutionized the way we communicate, work, and play. It has changed the way we access information, conduct business, and interact with one another. The internet has brought the world closer together and made it easier than ever to connect with people from all walks of life. In this essay, we will explore the history of the internet and its impact on society."""

    messages = [{"role": "system", "content": "You are a content generator. Write a short essay, fiction or non-fiction, any style. The first line should be the title of the essay, the second line should be the subtitle, and the third line should be blank. The rest of the content should be the body of the essay."}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=2000
        ).choices[0].message.content.strip()

    # Split the response into title, subtitle, and content
    title, subtitle, content = response.split("\n", 2)

    return title, subtitle, content

