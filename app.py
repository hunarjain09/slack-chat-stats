from flask import Flask, request
import logging
import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from summarize import summarize, summary_for_all_users, init


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
        for message in messages:
            # unique users in the conversation
            if 'user' in message:
                # users.add('@'+get_username(message['user'],client))
                # create a conversation history of user and message
                conversation_history.append((message['user'], message['text']))
        # call NLP library\
        init(conversation_history)
        if req_data.get('text'):
            total_summary = summary_for_all_users()
            get_users_arr = req_data.get('text').split(' ')
            summary = {}
            for userdata in get_users_arr:
                user = re.findall(r"[A-Z]\w+",userdata)
                summary[f"<@{user[0]}>"] = total_summary[user[0]]
        else:
            summary = summarize()
        logger.info("{} messages found in {}".format(len(conversation_history), id))
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
    return summary



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

