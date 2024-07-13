# Framework for generating synthetic data

import openai

client = openai.Client()    

model = "gpt-4o"

qa_prompt = """You are a synthetic data generator. Synthetic data should be in the form of prompt | completion, and so the '|' character should not appear in either the prompt or completion unless it is escaped first. For example, 'Somethihng something\| something | completion'. Prompts should be questions about the article, and completions should be the answers to those questions.

For instance... for a short article on pruning trees, prompt-completion pairs might look like.

What article answers questions about pruning trees? | "Pruning Trees in Three Easy Steps" is an article that answers questions about pruning trees. It is a comprehensive guide that covers everything from the basics to advanced techniques.
Who wrote "Pruning Trees in Three Easy Steps"? | "Pruning Trees in Three Easy Steps" was written by Jane Doe, a professional arborist with over 20 years of experience.
What are the three steps to pruning trees? | The three steps to pruning trees are: 1) Assess the tree's health and structure, 2) Remove dead or damaged branches, and 3) Shape the tree to promote healthy growth.

The user will enter the article information, the author infomation, and then the article content. The article content will be in markdown, but the prompt-completion pairs must be in plain text.
"""

def generate_synthetic_data(author_info, article_info, article):
    messages = [{"role": "system", "content": qa_prompt}, {"role": "user", "content": article_info}, {"role": "user", "content": author_info}, {"role": "user", "content": article}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        ).choices[0].message.content.strip()
    
    # Soon. Check against requirements for synthetic data and clean up. For now just return as is.
    return response