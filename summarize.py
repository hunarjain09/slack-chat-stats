from collections import defaultdict
from email.policy import default
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import json
import requests
import urllib.parse

inputParam = defaultdict(list)


def summary(text, summary_percentage):
    result = []
    LANGUAGE = "english"
    ##SENTENCES_COUNT = '2%'

    nltk.download('punkt')
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))

    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    for sentence in summarizer(parser.document, summary_percentage):
        result.append(" ".join(sentence.words))

    return "\n".join(result)


"""
Input: data =[(user,message),(user,message)]
"""


def parse_input(input):
    inputParam.clear()
    for user, message in input:
        inputParam[user].append(message)


def get_all_messages():
    return " ".join([item for sublist in inputParam.values() for item in sublist])


def get_messages_by_user(user):
    return " ".join(inputParam[user])


def summarize():
    return summary(get_all_messages(), "10%")


def summary_by_user(user):
    return summary(get_messages_by_user(user), "2%")


def init(payload):
    parse_input(payload)


def summary_for_all_users():
    user_summary = defaultdict()
    for user in inputParam.keys():
        user_summary[user] = summary_by_user(user)
    return user_summary


def extract_keyword(text,frequencies=4):
    keywords = []
    input = urllib.parse.quote(text)
    url = f"http://yake.inesctec.pt/yake/v2/extract_keywords?content={input}" \
          f"&max_ngram_size=3&number_of_keywords=20&highlight=true"
    response = requests.get(url)
    res_json = response.json()
    if res_json['keywords']:
        keyword = sorted(res_json['keywords'], key=lambda x: x['score'])
    for val in keyword[-frequencies:]:
        keywords.append(val['ngram'])
    return ','.join(keywords)

def get_top_keywords(user=None):
    if user:
        return extract_keyword(get_messages_by_user(user))
    else:
        return extract_keyword(get_all_messages())