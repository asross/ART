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
thread = client.beta.threads.create()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        return jsonify([c.content[0].text.value for c in messages.data])
    except:
        return jsonify([])

@app.route('/messages', methods=['POST'])
def post_message():
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=request.form['question']
    )

    client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=OPENAI_ASST_ID
    )

    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
