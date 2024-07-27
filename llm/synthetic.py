# Framework for generating synthetic data

import openai

client = openai.Client()    

model = "gpt-4o-mini"

# Generates knowledge based training pairs from article information.
def generate_knowledge_pairs(author_info, article_info, article):
    requirements = """
    **Requirements for training data**

    Data should be in the form of prompt | completion, and so the '|' character should not appear in either the prompt or completion unless it is escaped first. For example, 'Somethihng something\| something | completion'. Prompts should be questions about the article, and completions should be the answers to those questions.

    ### Specifications by Content Type:

    1. **Fiction:**
    - Focus on plot, characters, themes, and setting.
    - Example:
        - Prompt: What is the central conflict in "The Lost Island"? | Completion: The central conflict in "The Lost Island" is the protagonist's struggle to survive on an uncharted island while uncovering its hidden secrets.
        - Prompt: Who is the protagonist of "The Lost Island"? | Completion: The protagonist of "The Lost Island" is Jack Harper, a marine biologist who is stranded on the island after a shipwreck.
    
    2. **Non-Fiction:**
    - Focus on facts, data, instructions, and insights.
    - Example:
        - Prompt: What does the article "The Benefits of Daily Exercise" discuss? | Completion: "The Benefits of Daily Exercise" discusses the positive impacts of regular physical activity on mental and physical health.
        - Prompt: Who conducted the research mentioned in "The Benefits of Daily Exercise"? | Completion: The research mentioned in "The Benefits of Daily Exercise" was conducted by Dr. Emily Collins and her team at the University of Health Sciences.

    3. **History:**
    - Focus on events, dates, figures, and significance.
    - Example:
        - Prompt: What is the main topic of the article "The Rise and Fall of the Roman Empire"? | Completion: The main topic of "The Rise and Fall of the Roman Empire" is the historical account of the Roman Empire's expansion, peak, and eventual decline.
        - Prompt: Who was the first emperor of Rome mentioned in the article? | Completion: The first emperor of Rome mentioned in the article is Augustus Caesar.

    4. **Poetry:**
    - Focus on themes, motifs, stylistic devices, and interpretations.
    - Example:
        - Prompt: What is the theme of the poem "Whispers of Autumn"? | Completion: The theme of "Whispers of Autumn" is the transient beauty of nature and the inevitability of change.
        - Prompt: Who is the author of "Whispers of Autumn"? | Completion: The author of "Whispers of Autumn" is Emily Hart, a contemporary poet known for her nature-themed works.

    ### Additional Examples:

    1. **Science Article:**
    - Prompt: What is the main focus of "The Mysteries of Quantum Physics"? | Completion: The main focus of "The Mysteries of Quantum Physics" is to explore the fundamental principles of quantum mechanics and their implications for our understanding of the universe.
    - Prompt: Who authored "The Mysteries of Quantum Physics"? | Completion: "The Mysteries of Quantum Physics" was authored by Dr. Michael Reynolds, a theoretical physicist at MIT.

    2. **Technology Article:**
    - Prompt: What innovations are discussed in "The Future of Artificial Intelligence"? | Completion: "The Future of Artificial Intelligence" discusses innovations such as machine learning, neural networks, and ethical considerations in AI development.
    - Prompt: Which company is highlighted for its advancements in AI? | Completion: The company highlighted for its advancements in AI is OpenAI, known for its cutting-edge research and development.

    3. **Biography:**
    - Prompt: Who is the subject of "The Life of Marie Curie"? | Completion: The subject of "The Life of Marie Curie" is the renowned physicist and chemist who discovered radium and polonium.
    - Prompt: What achievements of Marie Curie are highlighted in the article? | Completion: The achievements highlighted include her two Nobel Prizes in Physics and Chemistry, and her pioneering research on radioactivity.

    4. **Travel Article:**
    - Prompt: What destination is featured in "Exploring the Wonders of Kyoto"? | Completion: The featured destination in "Exploring the Wonders of Kyoto" is the historic city of Kyoto, Japan, known for its temples, gardens, and cultural heritage.
    - Prompt: What are the must-see attractions mentioned in the article? | Completion: The must-see attractions include Kinkaku-ji (the Golden Pavilion), Fushimi Inari Shrine, and the Arashiyama Bamboo Grove.

    5. **Cooking Recipe:**
    - Prompt: What dish is the focus of "The Perfect Spaghetti Carbonara"? | Completion: The focus of "The Perfect Spaghetti Carbonara" is the traditional Italian pasta dish made with eggs, cheese, pancetta, and pepper.
    - Prompt: What ingredients are needed for Spaghetti Carbonara? | Completion: The ingredients needed are spaghetti, eggs, Parmesan cheese, pancetta, black pepper, and salt."""

    qa_prompt = f"""You are a synthetic data generator. Synthetic data should be in the form of prompt | completion, and so the '|' character should not appear in either the prompt or completion unless it is escaped first. For example, 'Somethihng something\| something | completion'. Prompts should be questions about the article, and completions should be the answers to those questions.
    Requirements:
    {requirements}

    The user will enter the article information, the author infomation, and then the article content. The article content will be in markdown, but the prompt-completion pairs must be in plain text.
    """
    messages = [{"role": "system", "content": qa_prompt}, {"role": "user", "content": article_info}, {"role": "user", "content": author_info}, {"role": "user", "content": article}, {"role": "system", "content": "Generate synthetic data based on the article information.\nFollow the format of prompt|completion\nprompt|completion"}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=2500
        ).choices[0].message.content.strip()
    
    # Instruct the system to evaluate whether a data set is consistent with the requirements. Maybe start w/ messages = [{"role": "system", "content": "Evaluate the synthetic data set based on the requirements provided."}, {"role": "user", "content": response}, {"role": "user", "content": requirements}]
    # TBD

    # Convert to array of pairs
    response = [[element.strip() for element in pair.split("|")] for pair in response.split('\n') if pair.strip()]
    return response

# Generates training pairs that prompt content and the resulting content matches the style of the sample piece.
def generate_style_pairs(sample):
    requirements = """
### Refined Requirements for Training Data

Data should be in the form of prompt | completion, and the '|' character should not appear in either the prompt or completion unless it is escaped first. For example, 'Something something\| something | completion'. Prompts should match the style and context of the sample provided, and completions should be the corresponding answers or content.

### Specifications by Content Type:

1. **Fiction:**
For fiction, prompts should inspire creative outputs that mirror the style and themes of the piece. Completions should capture the essence or tone of the original work, typically ranging from a few sentences to a paragraph long.

Examples:
- Write a mysterious scene in one paragraph. | The moon cast an eerie glow over the abandoned mansion, its shadows concealing secrets that had long been forgotten. Footsteps echoed in the empty hallways, a haunting reminder of the past.
- Craft a romantic dialogue in two sentences. | "I never knew love could feel like this," she whispered, her eyes locked with his. "Neither did I," he replied, drawing her closer.
- Compose a short poem inspired by nature. | In the heart of the forest, shadows dance and whispers linger, where love and loss intertwine beneath the ancient trees.

2. **Non-Fiction:**
For non-fiction, prompts should request brief, informative content that emulates the tone and structure of the piece. Completions should provide clear and relevant information, typically ranging from a sentence to a short paragraph.

Examples:
- Summarize a historical event in one paragraph. | In the heart of the ancient city, a decisive battle raged that would forever alter the course of history, as brave warriors clashed to defend their homeland.
- Write a ten-sentence mini editorial on human resilience. | The recent events have shown us that the human spirit is capable of remarkable resilience in the face of adversity.

3. **Expanded Topics:**
When a facet of the sample can be expanded upon without deviating from the original context, prompts should request a concise exploration of that topic. Completions should provide a detailed yet brief response, maintaining the style of the original piece.

Examples:
- Describe the process of cheese-making in one paragraph. | Cheese-making begins with curdling milk, either through natural souring or by adding rennet. The curds are then cut, cooked, and pressed to remove whey, followed by aging to develop flavor and texture.
- Write a paragraph on the impact of technology on education. | Technology has revolutionized education by providing access to vast resources and enabling interactive learning experiences. It has made education more accessible and engaging, breaking down traditional barriers."""

    style_prompt = f"""You are a synthetic data generator. Synthetic data should be in the form of prompt | completion, and so the '|' character should not appear in either the prompt or completion unless it is escaped first. For example, 'Somethihng something\| something | completion'. Prompts should be requests to generate content and completions should be the generated content. No multiline prompts or completions allowed.   
    {requirements}
    The user will enter a writing sample. The sample content will be in markdown, but the prompt-completion pairs must be in plain text and should not span multiple lines.
    """
    messages = [{"role": "system", "content": style_prompt}, {"role": "user", "content": sample}, {"role": "system", "content": "Generate synthetic data based on the sample provided.\nAdhere to the requirements especially the goal of matching style of the sample content. No questions allowed, only requests for content. Each prompt or completion must take up one line only each. Include at least ten pairs, or more if the sample is substantial enough.Follow the format of prompt|completion\nprompt|completion"}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=2500
        ).choices[0].message.content.strip()
    
    # Instruct the system to evaluate whether a data set is consistent with the requirements and include a rewrite only including the ones that follow the requirements. Maybe start w/ messages = [{"role": "system", "content": "Evaluate the synthetic data set based on the requirements provided."}, {"role": "user", "content": response}, {"role": "user", "content": requirements}]
    # TBD

    # Convert to array of pairs
    result = [[element.strip() for element in pair.split("|")] for pair in response.split('\n') if pair.strip()]
    return result