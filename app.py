from flask import Flask, render_template, request, jsonify
import openai
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
OPENAI_ASST_ID = os.environ['OPENAI_ASST_ID']
UBER_URL = os.environ['UBER_URL']
FEED_URLS = [
    "https://www.youtube.com/watch?v=x10vL6_47Dw",
    "https://www.youtube.com/watch?v=IQiid4VGW9k",
    "https://www.youtube.com/watch?v=4teJen3bjyM"
]

def output_for(call):
    if call.function.name == 'displayDroneFeed':
        args = json.loads(call.function.arguments)
        dnum = int(args.get('drone_number', '1')) % len(FEED_URLS)
        return FEED_URLS[dnum]
    elif call.function.name == 'callShuttle':
        return UBER_URL
    else:
        raise ArgumentError(f"Unknown function {call.function}")

app = Flask(__name__)

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/threads', methods=['POST'])
def create_thread():
    thread = client.beta.threads.create()
    return thread.id

@app.route('/threads/<thread_id>', methods=['GET'])
def get_thread_messages(thread_id):
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return jsonify([c.content[0].text.value for c in messages.data])
    except:
        return jsonify([])

@app.route('/threads/<thread_id>', methods=['POST'])
def post_thread_message(thread_id):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=request.json['message']
    )

    run = client.beta.threads.runs.create(
      thread_id=thread_id,
      assistant_id=OPENAI_ASST_ID
    )

    return run.id

@app.route('/threads/<thread_id>/runs/<run_id>', methods=['GET'])
def poll_run(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(
      thread_id=thread_id,
      run_id=run_id
    )

    if run.status == 'requires_action':
        calls = run.required_action.submit_tool_outputs.tool_calls
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=[
                { "tool_call_id": call.id, "output": output_for(call) }
                for call in calls
            ]
        )

    return run.status

if __name__ == '__main__':
    app.run(debug=True)
