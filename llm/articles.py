import openai

client = openai.Client()

model = "gpt-4o"

def generate_tags(content):
    messages = [{"role": "system", "content": "You are an article tag generator. Give a list of comma separated tags based on the article given."}, {"role": "user", "content": content}]
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