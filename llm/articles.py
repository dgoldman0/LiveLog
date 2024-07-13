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

Give a list of comma-separated tags based on the article provided. Must include at least three genre and three topic tags, at least two reading level, and at least 20 tags in total.
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

# Evaluate article
def evaluate_article(content):
    rubric = """### Comprehensive Content Quality Rubric

This rubric is designed to evaluate a wide range of content types, from technical information to creative works like haikus. It encompasses various dimensions of analysis to ensure a thorough assessment of content quality. Each dimension is assessed based on detailed criteria. The rubric is divided into major content types, each with specific criteria.

#### General Criteria (Applicable to All Content Types)

1. **Clarity and Coherence**
   - Unclear, disjointed, and difficult to follow.
   - Somewhat clear but with noticeable gaps and inconsistencies.
   - Generally clear with minor inconsistencies.
   - Clear and coherent with a logical flow.
   - Exceptionally clear and coherent, with a seamless flow.

2. **Grammar and Mechanics**
   - Numerous errors in grammar, spelling, and punctuation.
   - Several errors that distract from the content.
   - Some errors but generally readable.
   - Few errors, mostly minor.
   - Virtually no errors, polished and professional.

3. **Originality and Creativity**
   - Lacks originality, highly derivative.
   - Somewhat original but with common ideas.
   - Shows originality with some creative elements.
   - Original and creative, stands out.
   - Highly original, exceptionally creative.

#### Technical Content

1. **Accuracy and Reliability**
   - Numerous factual errors, unreliable sources.
   - Several errors, some unreliable sources.
   - Generally accurate, mostly reliable sources.
   - Accurate with reliable sources.
   - Highly accurate, authoritative sources.

2. **Depth of Analysis**
   - Superficial, lacks depth.
   - Basic analysis, limited depth.
   - Moderate depth, covers main points.
   - Thorough analysis, covers key details.
   - In-depth analysis, comprehensive coverage.

3. **Relevance and Application**
   - Not relevant, little practical application.
   - Limited relevance, some practical application.
   - Generally relevant, practical application.
   - Relevant with clear practical application.
   - Highly relevant, significant practical application.

#### Creative Content (Poetry, Haiku, Short Stories)

1. **Imagery and Descriptive Language**
   - Lacks imagery, very plain.
   - Minimal imagery, basic descriptions.
   - Some imagery, decent descriptions.
   - Good use of imagery, vivid descriptions.
   - Excellent imagery, highly evocative descriptions.

2. **Emotional Impact**
   - No emotional impact, very flat.
   - Minimal emotional impact, somewhat flat.
   - Some emotional impact, moderately engaging.
   - Strong emotional impact, engaging.
   - Exceptional emotional impact, highly engaging.

3. **Form and Structure**
   - Poor structure, difficult to follow.
   - Basic structure, somewhat disorganized.
   - Adequate structure, generally organized.
   - Good structure, well-organized.
   - Excellent structure, exceptionally well-organized.

#### Informative Content (Essays, Articles)

1. **Thesis and Purpose**
   - No clear thesis or purpose.
   - Weak thesis, unclear purpose.
   - Clear thesis and purpose, adequately developed.
   - Strong thesis, well-developed purpose.
   - Compelling thesis, exceptionally well-developed purpose.

2. **Evidence and Support**
   - Lacks evidence, unsupported claims.
   - Minimal evidence, weak support.
   - Adequate evidence, reasonably supported.
   - Strong evidence, well-supported.
   - Extensive evidence, exceptionally well-supported.

3. **Organization and Flow**
   - Poorly organized, difficult to follow.
   - Basic organization, somewhat disjointed.
   - Generally organized, minor flow issues.
   - Well-organized, smooth flow.
   - Exceptionally well-organized, seamless flow.

#### Multimedia Content (Videos, Podcasts)

1. **Production Quality**
   - Poor production quality, distracting issues.
   - Basic production quality, some issues.
   - Adequate production quality, minor issues.
   - Good production quality, few issues.
   - Excellent production quality, professional.

2. **Engagement and Interest**
   - Not engaging, very boring.
   - Minimally engaging, somewhat boring.
   - Moderately engaging, generally interesting.
   - Highly engaging, very interesting.
   - Exceptionally engaging, captivating.

3. **Content Delivery**
   - Poor delivery, difficult to understand.
   - Basic delivery, some clarity issues.
   - Adequate delivery, generally clear.
   - Good delivery, clear and effective.
   - Excellent delivery, exceptionally clear and effective.

### Scoring Instructions

Each criterion is assessed without numerical values during the evaluation process. The final score is determined based on the overall quality across all criteria. 

**Overall Quality Rating:**
- Exceptional: All criteria consistently meet the highest standard.
- Very Good: Most criteria meet high standards with a few minor areas for improvement.
- Good: Meets basic standards across all criteria with some areas for enhancement.
- Satisfactory: Meets minimum standards but has several areas needing improvement.
- Needs Improvement: Fails to meet minimum standards in multiple criteria. 

### Usage Instructions

- Evaluate each criterion separately for the content type.
- Provide comments to justify scores and offer constructive feedback.
- Use the total score to determine overall content quality based on the final rating.

Evaluate the following content based on the comprehensive content quality rubric. Provide detailed feedback on each criterion to assess the quality of the content. Again, do not use numeric scoring. Give a final determination of the overall quality rating based on the evaluation with the options of 'exceptional, very Good, good, satisfactory, or needs improvement. This final score should be on a new line, by itself, nothing else, no formatting.'"""

    messages = [{"role": "system", "content": rubric}, {"role": "user", "content": content}]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        ).choices[0].message.content.strip()

    # Get the final score
    response = response.split('\n')[-1].lower()
    # Double check that the format is correct as a valid score.
    if response in ['exceptional', 'very good', 'good', 'satisfactory', 'needs improvement']:
        # Convert to numeric score with exceptional = 4, very good = 3, good = 2, satisfactory = 1, needs improvement = 0
        score_map = {'exceptional': 4, 'very good': 3, 'good': 2, 'satisfactory': 1, 'needs improvement': 0}
        return score_map[response]