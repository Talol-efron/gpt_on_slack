import openai
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv('.env') 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

openai.api_key = os.getenv("OPENAI_API_KEY")
app = App(token=SLACK_BOT_TOKEN)

messages = []
max_tokens = 8192

def add_message(messages, role, content, max_tokens):
    new_message = {
        "role": role,
        "content": content
    }
    messages.append(new_message)

    while total_tokens(messages) > max_tokens:
        messages.pop(0)

    return messages


def total_tokens(messages):
    token_count = 0

    for message in messages:
        token_count += len(message["content"]) + 1  # "content"のトークン数と役割分の1トークン

    return token_count


initial_system_message = "You are intelligent, gentlemanly and calm. You are often charming."
messages = add_message(messages, "system", initial_system_message, max_tokens)

@app.event("app_mention")
def mention_handler(body, say):
    global messages
    text = body['event']['text']
    user = body['event']['user']

    # メンションを取り除く
    prompt = text.replace(f'<@{user}>', '').strip()

    try:
        # Add the user's message to the messages list
        messages = add_message(messages, "user", prompt, max_tokens)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )

        # 返信を取得し、Slackに送信
        reply = response.choices[0]["message"]["content"].strip()
        say(f'<@{user}> \n {reply}')

        # Add the assistant's reply to the messages list
        messages = add_message(messages, "assistant", reply, max_tokens)
        print(total_tokens(messages))

    except Exception as e:
        # Handle any exceptions that may occur
        say(e)

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
