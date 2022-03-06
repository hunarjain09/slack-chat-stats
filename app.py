from flask import Flask, request
import logging
import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import slack_util
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
        best_reply, best_reply_count, best_reaction_count, best_reaction = None, 0 , 0, None
        for message in messages:
            conversation_map = {
                'user': None,
                'message': None, 
                'conversation': None, 
                'number_of_replies': None, 
                'number_of_reactions': None
            }
            # unique users in the conversation
            if 'user' in message:
                conversation_map['user'] = message['user']
                conversation_map['message'] = message['text']
                conversation_map['conversation'] = (message['user'], message['text'])
                if 'has joined the channel' in message['text']:
                    continue
                if 'reactions' in message:
                    conversation_map['number_of_reactions'] = len(message['reactions'])
                if 'reply_count' in message: 
                    conversation_map['number_of_replies'] = message['reply_count']
                if conversation_map['number_of_reactions']:
                    if best_reaction is None:
                        best_reaction = conversation_map
                    elif conversation_map['number_of_reactions'] > best_reaction_count:
                        best_reaction = conversation_map
                if conversation_map['number_of_replies']:
                    if best_reply is None:
                        best_reply = conversation_map
                    elif conversation_map['number_of_replies'] > best_reply_count:
                        best_reply = conversation_map
                conversation_history.append(conversation_map)
        # call NLP library
        init([message['conversation'] for message in conversation_history])
        if req_data.get('text'):
            total_summary = summary_for_all_users()
            get_users_arr = req_data.get('text').split(' ')
            summary = {}
            for userdata in get_users_arr:
                user = re.findall(r"[A-Z]\w+",userdata)
                summary[f"<@{user[0]}>"] = total_summary[user[0]]
            summary_details = dict()
            if best_reply:
                summary_details['top_replies'] = f"<@{best_reply['user']}> : {best_reply['message']}"
            if best_reaction:
                summary_details['top_reactions'] = f"<@{best_reaction['user']}> : {best_reaction['message']}"
            final_summary = slack_util.beautify_response(user_name=f"<@{req_data.get('user_id')}>",
                                                         user_summaries=summary,
                                                         summary_details=summary_details)
        else:
            summary = summarize()
            final_summary = summary
        logger.info("{} messages found in {}".format(len(conversation_history), id))
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
    return final_summary



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

