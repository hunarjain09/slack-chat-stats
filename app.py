from flask import Flask, request
import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


app = Flask(__name__)

@app.route('/', method=['POST'])
def hello_world():
    req_data = request.form
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

    logger = logging.getLogger(__name__)
    conversation_history = []
    # channel_id from the slack request
    channel_id = req_data.getlist('channel_id')
    try:
        # last 100 conversations
        result = client.conversations_history(channel=channel_id, limit=100)
        messages = result["messages"]
        users = set()
        for message in messages:
            # unique users in the conversation
            users.add(message['user'])
            # create a conversation history of user and message
            conversation_history.append((message['user'], message['text'].decode('utf-8')))
        # call NLP library
        logger.info("{} messages found in {}".format(len(conversation_history), id))
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

    return 'Hello Sammy!'

