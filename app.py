from flask import Flask, request
import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


app = Flask(__name__)
auth_token = 'xoxb-3210173726865-3200014683316-nTkYQs8qDmjNe3R3X0eC81M3'
@app.route('/slack', methods=['POST'])
def hello_world():
    req_data = request.form
    client = WebClient(token=auth_token)

    logger = logging.getLogger(__name__)
    conversation_history = []
    # channel_id from the slack request
    channel_id = req_data.getlist('channel_id')
    try:
        # last 100 conversations
        result = client.conversations_history(channel=channel_id[0], limit=100)
        messages = result["messages"]
        users = set()
        for message in messages:
            # unique users in the conversation
            if 'user' in message:
                users.add(message['user'])
                # create a conversation history of user and message
                conversation_history.append((message['user'], message['text']))
        # call NLP library
        logger.info("{} messages found in {}".format(len(conversation_history), id))
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

    return str(conversation_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

