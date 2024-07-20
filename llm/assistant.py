# Assistant. Handles user interactions using natural language. Designing currently to be compatible with Flask web-interface and in the future Gopher+NLP.
import datetime
from flask import jsonify
import openai
import data
import json
import re

client = openai.Client()
model = "gpt-4o-mini"

# The following are functions that will give access to automate various tasks in the LiveLog system giving abilities to the assistant. Maybe should replace getter and setter with unified like I accidentally did with context?
# List articles from a given user.
def list_articles(conn, user_id, author_id=None):
    if not author_id:
        author_id = user_id
    articles = conn.execute('SELECT * FROM articles WHERE author_id = ? and DRAFT = 0', (author_id,)).fetchall()
    if articles:
        article_list = "The following articles were retrieved.\n\n" 
        # Use markdown to make it easier
        for article in articles:
            article_list += f"Article ID: {article['id']}\nTitle: {article['title']}\nSubtitle: {article['subtitle']}\nTLDR: {article['tldr']}"
        return f"Retrieved articles for author with id: {author_id}.\n\n{article_list}"
    return 

def list_drafts(conn, user_id):
    drafts = conn.execute('SELECT * FROM articles WHERE author_id = ? and DRAFT = 1', (user_id,)).fetchall()
    if drafts:
        draft_list = "The following drafts were retrieved.\n\n" 
        for draft in drafts:
            draft_list += f"Draft ID: {draft['id']}\nTitle: {draft['saved_title']}\nSubtitle: {draft['saved_subtitle']}\nContent:\n{draft['saved_content']}"
        return f"Retrieved drafts...\n\n{draft_list}"

# Get full details of an article, if it is published and exists of course.
def get_article(conn, article_id):
    article = conn.execute('SELECT * FROM articles WHERE id = ? and DRAFT = 0', (article_id,)).fetchone()
    if article:
        return f"Retrieved article with id: {article_id}.\n\nTitle: {article['title']}\nSubtitle: {article['subtitle']}\nContent:\n{article['content']}"
    return f"Article with id: {article_id} not found."

# Create a new article and return the article id.
def create(conn, user_id):
    conn.execute('INSERT INTO articles (author_id) VALUES (?)', (user_id,))
    article_id = conn.execute('SELECT id FROM articles WHERE author_id = ? ORDER BY id DESC LIMIT 1', (user_id,)).fetchone()['id']
    return f"Article created with id: {article_id}."

def title(conn, article_id, title):
    # Check if article exists and if user is author.
    conn.execute('UPDATE articles SET saved_title = ? WHERE id = ?', (title, article_id))
    if conn.total_changes == 0:
        return f"Article with id: {article_id} not found or user is not the author of this article."
    return f"Title set for article with id: {article_id}."

def get_title(conn, article_id):
    title = conn.execute('SELECT title FROM articles WHERE id = ?', (article_id,)).fetchone()
    if title:
        return f"Retrieved title for article with id: {article_id}.\n\n{title['title']}"
    return f"No title found for article with id: {article_id}."

def subtitle(conn, article_id, subtitle):
    conn.execute('UPDATE articles SET saved_subtitle = ? WHERE id = ?', (subtitle, article_id))
    if conn.total_changes == 0:
        return f"Article with id: {article_id} not found or user is not the author of this article."
    return f"Subtitle set for article with id: {article_id}."

def get_subtitle(conn, article_id):
    subtitle = conn.execute('SELECT subtitle FROM articles WHERE id = ?', (article_id,)).fetchone()
    if subtitle:
        return f"Retrieved subtitle for article with id: {article_id}.\n\n{subtitle['subtitle']}"
    return f"No subtitle found for article with id: {article_id}."

def content(conn, article_id, content):
    content = content.replace('\\"', '"').replace('\\n', '\n')
    conn.execute('UPDATE articles SET saved_content = ? WHERE id = ?', (content, article_id))
    if conn.total_changes == 0:
        return f"Article with id: {article_id} not found or user is not the author of this article."
    return f"Draft content has been successfully updated and finalized for article with id: {article_id}. New finalized content:\n\n{content}"

def get_content(conn, article_id):
    content = conn.execute('SELECT content FROM articles WHERE id = ?', (article_id,)).fetchone()
    if content:
        return f"Retrieved content for article with id: {article_id}.\n\n{content['content']}"
    return f"No content found for article with id: {article_id}."

def tags(conn, article_id=None):
    # Get article tags and count.
    if article_id:
        tags = conn.execute('SELECT tag, COUNT(tag) AS count FROM article_tags WHERE article_id = ? GROUP BY tag', (article_id,)).fetchall()
    else:
        tags = conn.execute('SELECT tag, COUNT(tag) AS count FROM article_tags GROUP BY tag').fetchall()
    if tags:
        tag_list = ', '.join([f"{tag} ({count})" for tag, count in tags])
        return f"Retrieved tags and tag count for article with id: {article_id}.\n\n{tag_list}"
    return f"No tags found for article with id: {article_id}."

# Will need to pass userid at some point because only author should be able to read evaluation
def evaluation(conn, user_id, article_id):
    article = conn.execute('SELECT author_id, EVALUATION FROM articles WHERE id = ?', (article_id,)).fetchone()
    if article and article['author_id'] == user_id:
        return f"The evaluation for article with id: {article_id} is as follows.\n\n{article['EVALUATION']}"
    return f"Attempted to retrieve evaluation for article with id: {article_id}, but no evaluation was found or accessible."

# Need to combine or something...

def parse_command(response):
    # Define a regular expression pattern to capture the command
    pattern = re.compile(r'^(drafts\(\)|articles\(\d*\)|create\(\)|article\(\d+\)|title\(\d+, ".*?"\)|title\(\d+\)|subtitle\(\d+, ".*?"\)|subtitle\(\d+\)|content\(\d+, ".*?"\)|content\(\d+\)|tags\(\d*\)|evaluation\(\d+\)|subtitle\(".*?"\)|respond\(".*?"\)|now\(\))$', re.MULTILINE)
    # Search for the command in the response
    match = pattern.search(response.strip())
    
    if match:
        return match.group(0)
    else:
        return None
    
def execute_command(conn, user_id, conversation_history, input_text, response):
    # Parse the command from the response
    context = ""
    command = parse_command(response)
    if command is None:
        raise ValueError("Invalid command: " + response)
    if command.startswith("articles("):
        # Extract author_id from the command
        match = re.match(r'articles\((\d*)\)', command)
        if match:
            author_id = match.group(1)
            context = list_articles(conn, user_id, author_id)
        else:
            context = list_articles(conn, user_id)
    elif command.startswith("drafts()"):
        context = list_drafts(conn, user_id)
    elif command.startswith("create()"):
        # Call the create function
        context = create(conn, user_id)
    elif command.startswith("article("):
        # Extract id and title from the command
        match = re.match(r'article\((\d+)"\)', command)
        if match:
            article_id = int(match.group(1))
            context = get_article(conn, id, article_id)
    elif command.startswith("title("):
        # Extract id and title from the command
        match = re.match(r'title\((\d+), "(.*?)"\)', command)
        if match:
            id = int(match.group(1))
            new_title = match.group(2)
            context = title(conn, id, new_title)
        else:
            # Extract id only
            match = re.match(r'title\((\d+)\)', command)
            if match:
                id = int(match.group(1))
                context = get_title(conn, id)
    elif command.startswith("subtitle("):
        # Extract id and subtitle from the command
        match = re.match(r'subtitle\((\d+), "(.*?)"\)', command)
        if match:
            id = int(match.group(1))
            subtitle = match.group(2)
            context = subtitle(conn, id, subtitle)
        else:
            # Extract id only
            match = re.match(r'subtitle\((\d+)\)', command)
            if match:
                id = int(match.group(1))
                context = get_subtitle(conn, id)
    elif command.startswith("content("):
        # Extract id and content from the command
        match = re.match(r'content\((\d+), "(.*?)"\)', command)
        if match:
            id = int(match.group(1))
            new_content = match.group(2)
            context = content(conn, id, new_content)
        else:
            # Extract id only
            match = re.match(r'content\((\d+)\)', command)
            if match:
                id = int(match.group(1))
                context = get_content(conn, id)
    elif command.startswith("tags("):
        # Extract article_id if provided
        match = re.match(r'tags\((\d*)\)', command)
        if match:
            article_id = match.group(1)
            if article_id:
                context = tags(int(conn, article_id))
            else:
                context = tags()
    elif command.startswith("evaluation("):
        # Extract id from the command
        match = re.match(r'evaluation\((\d+)\)', command)
        if match:
            id = int(match.group(1))
            context = evaluation(conn, user_id, id)
    elif command.startswith("now()"):
        # Get date and time
        current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f"The date and time is {current}."
    elif command.startswith("respond("):
        # Extract context from the command
        match = re.match(r'respond\((.*?)\)', command)
        if match:
            context = f"Internal analysis of conversation history which under normal circumstances will be hidden from the end user: {match.group(1)}"
    else:
        raise ValueError("Invalid command")

    # Add the response to the conversation history.
    conn.execute('INSERT INTO conversation_history (user_id, centry) VALUES (?, ?)', (user_id, json.dumps({"role": "assistant", "content": context})))

    system_message = """You are the voxsite portal for LiveLog. LiveLog is among the first voxsite platforms dedicated to authorship.
    
    LiveLog has a shared data model. Users agree to share their content to improve the voxsite, and LiveLog creates a tailored voxsite for the author, based on their own content. While there will be a web interface for now, the goal is to have the voxsite [GopherAI](https://github.com/dgoldman0/gopherAI) ready from early on.
    
    If linking to articles, etc., use relative links. For instance,
    /article/3/draft for linking to draft editor with id 3.
    /article/1 to view article with id 1.
    /blog/5 for linking to the blog with id 5."""

    messages = [{"role": "system", "content": system_message}]
    for row in conversation_history:
        messages.append(json.loads(row['centry']))
    messages.append({"role": "user", "content": input_text})
    messages.append({"role": "assistant", "content": context})
    messages.append({"role": "system", "content": "Use the information provided to write a response to the user."})
    response = client.chat.completions.create(
            model=model, 
            messages=messages,
            max_tokens=3000
        ).choices[0].message.content.strip()
    conn.execute('INSERT INTO conversation_history (user_id, centry) VALUES (?, ?)', (user_id, json.dumps({"role": "assistant", "content": response})))
    return response

# Include later:    drafts() - List drafts from the user.
def process_input(user_id, input_text):
    # Get convesation history from the database.
    conn = data.get_db_connection()
    conversation_history = conn.execute('SELECT centry FROM conversation_history WHERE user_id = ? ORDER BY stamp DESC', (user_id,)).fetchall()
    # Need to decide what to instruct it to do about encoding. Maybe HTML enoding and then it's decoded afterwards in the command? 
    system_message = """You are a voxsite portal service interface. Your task is to consider the conversation provided and determine which one of the following commands should be executed. One must be executed.
    
    There is no need to find the user id, as the system already has it stored.

    article(id) - Get title, subtitle, and full content of an article with the provided id. If the article is not published, the draft content will be retrieved.
    articles(author_id) - List articles published from a given user. Leave author_id blank to list articles by the user.
    drafts() - Get a list of drafts from the user.
    create() - Create a new livelog entry.
    title(id, title) - Set the draft title of the livelog entry with the provided id
    title(id) - Get the published title of the livelog entry with the provided id, if it is published, otherwise will get the draft title.
    subtitle(id, subtitle) - Set the draft subtitle of the livelog entry with the provided id
    subtitle(id) - Get the subtitle of the livelog entry with the provided id, if it is published, otherwise will get the draft subtitle.
    content(id, content) - Set the draft content of the livelog entry with the provided id. Escape quotes, new lines, etc. as needed.
    content(id) - Get the content of the livelog entry with the provided id, if it is published, otherwise will get the draft content.
    tags(article_id) - List tags for a given article. Leave article_id blank to list all tags and their counts.
    evaluation(id) - Get the evaluation of the livelog entry with the provided id
    now() - Give the current date and time in the format YYYY-MM-DD HH:MM:SS
    respond(context) - Use this command if there is already enough information to respond. This command will automatically generate a response based on the conversation history. The context should be clear enough to provide a full response, without any additional input.
    
    Determine which command should be executed based on the conversation provided.
    
    For instance,
    
    If the user says "I want to create a new livelog entry", you should execute the command
    create()
    
    or


    If the user says "I want to set the title of my first livelog entry to 'My First Livelog Entry'", you should execute the command
    title(1, "My First Livelog Entry")
    
    or
    
    If the user wants to know the date or time of the current moment, you should execute the command
    now()

    or

    If the user says "What is the title of my first livelog entry" and conversation history already indicates the title is "My First Livelog Entry", you should execute the command
    response("The title of your first livelog entry is 'My First Livelog Entry'.")

    Only  one command can be executed. If uncertain of what to do, request further instructions. Use of response is appropriate where the next step is going to be replying directly to the user.

    This system is a backend toolkit system, not a system to reply to a end user directly. The only valid output is one of the commands listed.
    """

    cont = True
    command = ""
    while cont:
        messages = [{"role": "system", "content": system_message}]
        for row in conversation_history:
            messages.append(json.loads(row['centry']))
        messages.append({"role": "user", "content": input_text})

        conn.execute('INSERT INTO conversation_history (user_id, centry) VALUES (?, ?)', (user_id, json.dumps({"role": "user", "content": input_text})))
            
        response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000
            ).choices[0].message.content.strip()
        
        # Get the last line of the response and execute
        command = response.split('\n')[-1]
        # Run a sanity check.
        messages = [{"role": "system", "content": "You are a sanitory check system. Your task is to determine if the command selected is reasonable, based on the conversation history and most recent message."}]
        # Convert whole conversation history to string for now.
        history = '\n'.join([f"{row['role']}: {row['content']}" for row in conversation_history])
        history += f"\nuser: {input_text}"
        messages.append({"role": "user", "content": history})
        messages.append({"role": "assistant", "content": f"Selected command: {command}"})
        messages.append({"role": "system", "content": "Determine if the command is reasonable based on the conversation history and most recent message in the conversation history provided. Respond only with 'yes' or 'no' and nothing else."})
        check = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000
            ).choices[0].message.content.strip()
        if check == "yes":
            cont = False
        else:
            print(check)
            print(conversation_history)
    result = execute_command(conn, user_id, conversation_history, input_text, command)
    conn.commit() # Maybe should share conn throughout and commit at the end?
    conn.close()
    return result

def get_conversation_history(user_id, include_system_context=False):
    conn = data.get_db_connection()
    conversation_history = conn.execute('SELECT * FROM conversation_history WHERE user_id = ? ORDER BY stamp ASC', (user_id,)).fetchall()
    conn.close()
    if include_system_context:   
        return [json.loads(row['centry']) for row in conversation_history]
    # Return all user messages but only the second of every pair of assistant messages because they're background context.
    first = True
    history = []    
    for row in conversation_history:
        row = json.loads(row['centry'])
        if row['role'] == 'user':
            history.append(row)
        elif not first:
            first = True
            history.append(row)
        else: 
            first = False

    return history
