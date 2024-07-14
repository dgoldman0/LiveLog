# Assistant. Handles user interactions using natural language. Designing currently to be compatible with Flask web-interface and in the future Gopher+NLP.
from flask import jsonify
import openai
import data
import json

client = openai.Client()
model = "gpt-4o"

def process_input(user_id, input_text):
    # Get convesation history from the database.
    conn = data.get_db_connection()
    conversation_history = conn.execute('SELECT centry FROM conversation_history WHERE user_id = ? ORDER BY timestamp DESC', (user_id,)).fetchall()
    system_message = """You are the voxsite portal for LiveLog. LiveLog is among the first voxsite platforms dedicated to authorship.
    
    LiveLog has a shared data model. Users agree to share their content to improve the voxsite, and LiveLog creates a tailored voxsite for the author, based on their own content. While there will be a web interface for now, the goal is to have the voxsite [GopherAI](https://github.com/dgoldman0/gopherAI) ready from early on.
    
    You may respond in plain text or markdown. Full markdown is supported."""
    # Eventually run through a security pre-processor.
    messages = [{"role": "system", "content": system_message}]
    for row in conversation_history:
        messages.append(json.loads(row['centry']))
    messages.append({"role": "user", "content": input_text})
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=100
        ).choices[0].message.content.strip()
    
    # Add the result to the conversation history. Make sure it's formatted as a proper assistant response.
    conn.execute("INSERT INTO conversation_history (user_id, centry) VALUES (?, ?)", (user_id, json.dumps({"role": "user", "content": input_text})))
    conn.execute('INSERT INTO conversation_history (user_id, centry) VALUES (?, ?)', (user_id, json.dumps({"role": "assistant", "content": response})))
    return response

def get_conversation_history(user_id):
    conn = data.get_db_connection()
    conversation_history = conn.execute('SELECT * FROM conversation_history WHERE user_id = ? ORDER BY stamp DESC', (user_id,)).fetchall()
    conn.close()
    # Convert each entry to JSON and return it.
    return jsonify([json.loads(row['centry']) for row in conversation_history])
