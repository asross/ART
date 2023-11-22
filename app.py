from flask import Flask, render_template, request, jsonify
import openai
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
OPENAI_ASST_ID = os.environ['OPENAI_ASST_ID']

app = Flask(__name__)

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/threads', methods=['POST'])
def create_thread():
    thread = client.beta.threads.create()
    return thread.id

@app.route('/messages/<thread_id>', methods=['GET'])
def get_messages(thread_id):
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return jsonify([c.content[0].text.value for c in messages.data])
    except:
        return jsonify([])

@app.route('/messages/<thread_id>', methods=['POST'])
def post_message(thread_id):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=request.json['message']
    )

    client.beta.threads.runs.create(
      thread_id=thread_id,
      assistant_id=OPENAI_ASST_ID
    )

    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
