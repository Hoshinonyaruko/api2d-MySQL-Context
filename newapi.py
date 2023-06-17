from flask import Flask, request, jsonify
from flaskext.mysql import MySQL
import uuid
import datetime
import requests
import json

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '数据库密码'
app.config['MYSQL_DATABASE_DB'] = '数据库名称'
app.config['MYSQL_DATABASE_HOST'] = '数据库地址'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
mysql.init_app(app)

MAX_TOKENS = 4096
def truncate_history(history, prompt):
    def tokens_count(message):
        return len(message["content"])

    token_count = sum([tokens_count(entry) for entry in history]) + len(prompt)
    if token_count <= MAX_TOKENS:
        return history
    
    # Step 1: Set assistant replies to None
    truncated_history = [entry for entry in history if entry["role"] == "user"]
    token_count = sum([tokens_count(entry) for entry in truncated_history]) + len(prompt)
    if token_count <= MAX_TOKENS:
        return truncated_history
    
    # Step 2: Remove history elements from the beginning until it fits within MAX_TOKENS
    while token_count > MAX_TOKENS:
        truncated_history.pop(0)
        token_count = sum([tokens_count(entry) for entry in truncated_history]) + len(prompt)
    
    return truncated_history

def create_conversation(conversation_id):
    cursor = mysql.get_db().cursor()
    query = "INSERT INTO conversations (id) VALUES (%s)"
    cursor.execute(query, (conversation_id,))
    mysql.get_db().commit()


def add_message(conversation_id, parent_message_id, text, role):
    db = mysql.get_db()
    cursor = db.cursor()
    message_id = str(uuid.uuid4())

    query = """
        INSERT INTO messages (id, conversation_id, parent_message_id, text, role)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (message_id, conversation_id, parent_message_id, text, role))
    db.commit()
    return message_id

def get_history(conversation_id, parent_message_id):
    cursor = mysql.get_db().cursor()
    query = "SELECT text, role FROM messages WHERE conversation_id = %s AND id <= %s ORDER BY created_at ASC"
    cursor.execute(query, (conversation_id, parent_message_id))
    rows = cursor.fetchall()
    history = []
    current_query = None
    for text, role in rows:
        if role == "user":
            if current_query is not None:
                history.append({"role": "user", "content": current_query})
            current_query = text
        else:  # role == "assistant"
            if current_query is not None:
                history.append({"role": "user", "content": current_query})
                current_query = None
            history.append({"role": "assistant", "content": text})
    if current_query is not None:
        history.append({"role": "user", "content": current_query})
    return history

@app.route('/conversation', methods=['POST'])
def chat():
    data = request.get_json()
    message_text = data.get("message")
    conversation_id = data.get("conversationId")
    parent_message_id = data.get("parentMessageId")

    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        create_conversation(conversation_id)
        parent_message_id = None

    user_message_id = add_message(conversation_id, parent_message_id, message_text, "user")

    history = []
    if parent_message_id:
        history = get_history(conversation_id, parent_message_id)
        print("history: " + str(history))

        # Truncate history to fit within token limit
        history = truncate_history(history, message_text)
        print("truncated history: " + str(history))

    response_text = call_chatgpt_api(prompt=message_text, history=history)

    assistant_message_id = add_message(conversation_id, user_message_id, response_text, "assistant")

    response = {
        "response": response_text,
        "conversationId": conversation_id,
        "messageId": assistant_message_id
    }
    return jsonify(response)

def call_chatgpt_api(prompt, history):
    url = "https://openai.api2d.net/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Content-Length": None,  # We will compute this later
        "Authorization": "Bearer your token"
    }
    messages = history[:]
    messages.append({"role": "user", "content": prompt})
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "safe_mode": False
    }
    json_data = json.dumps(data)
    headers["Content-Length"] = str(len(json_data))
    proxies = {
        "http": None,
        "https": None
    }
    response = requests.post(url, headers=headers, data=json_data, proxies=proxies)
    if response.status_code == 200:
        response_data = response.json()
        print(f"API response: {response_data}")  # Add debug information
        return response_data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=46130,debug=True)


#CREATE TABLE conversations (
#     id VARCHAR(255) PRIMARY KEY
# );

# CREATE TABLE messages (
#     id VARCHAR(255) PRIMARY KEY,
#     conversation_id VARCHAR(255),
#     parent_message_id VARCHAR(255),
#     text TEXT NOT NULL,
#     role ENUM('user', 'assistant') NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (conversation_id) REFERENCES conversations(id),
#     FOREIGN KEY (parent_message_id) REFERENCES messages(id)
# );