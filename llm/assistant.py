# Assistant. Handles user interactions using natural language. Designing currently to be compatible with Flask web-interface and in the future Gopher+NLP.
import openai
import data

client = openai.Client()

def process_input(user_id, input_text):
    # Get convesation history from the database.
    conn = data.get_db_connection()
    conversation_history = conn.execute('SELECT * FROM conversation_history WHERE user_id = ? ORDER BY timestamp DESC', (user_id,)).fetchall()
    system_message = """You are the voxsite portal for LiveLog. LiveLog is among the first voxsite platforms dedicated to authorship. LiveLog has a shared data model. Users agree to share their content to improve the voxsite, and LiveLog creates a tailored voxsite for the author, based on their own content. While there will be a web interface for now, the goal is to have the voxsite [GopherAI](https://github.com/dgoldman0/gopherAI) ready from early on."""
    # Eventually run through a security pre-processor.
    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": input_text})