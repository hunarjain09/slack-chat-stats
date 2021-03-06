import json

def get_response(name):
    response = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi {name}:wave:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Here is the summary of the chat: "
                }
            }
        ]
    }
    return response

def get_summary(text):
    message_summary = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
    return message_summary


def beautify_response(user_name, user_summaries=None, summary_details=None):
    bs = get_response(user_name)
    if user_summaries:
        for user, summary in user_summaries.items():
            bs['blocks'] += [get_summary(user+":"+summary)]
    if len(summary_details)>0:
        if 'top_reactions' in summary_details:
            bs['blocks'] += [ get_summary("Top message (reactions) :ghost: : " + summary_details['top_reactions'])]
        if 'top_replies' in summary_details:
            bs['blocks'] += [ get_summary("Top message (replies) :innocent: : " + summary_details['top_replies'])]
        if 'top_spammer' in summary_details:
            bs['blocks'] += [ get_summary("Top spammer (replies) :eyes: : " + summary_details['top_spammer'])]
        if 'top_keyword' in summary_details:
            bs['blocks'] += [ get_summary("Topics  :books: : " + summary_details['top_keyword'])]
        if 'group_negativity' in summary_details:
            bs['blocks'] += [get_summary("Group Negativity Index  :fearful: : " + summary_details['group_negativity'])]
    return bs