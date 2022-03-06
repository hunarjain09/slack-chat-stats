from collections import defaultdict
from email.policy import default
import nltk
from rake_nltk import Rake
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import json
import requests
import urllib.parse
import regex as re
import networkx as nx
import numpy as np
from nltk.tokenize.punkt import PunktSentenceTokenizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from rake_nltk import Rake

inputParam = defaultdict(list)


def summary_v1(text, summary_percentage="2%"):
    result = []
    LANGUAGE = "english"
    #SENTENCES_COUNT = '2%'

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
    return summary(get_all_messages())


def summary_by_user(user):
    return summary_v1(get_messages_by_user(user))


def init(payload):
    parse_input(payload)
    nltk.download('stopwords')


def summary_for_all_users():
    user_summary = defaultdict()
    for user in inputParam.keys():
        user_summary[user] = summary_by_user(user)
    return user_summary

def textrank(document):
    sentence_tokenizer = PunktSentenceTokenizer()
    sentences = sentence_tokenizer.tokenize(document)
    bow_matrix = CountVectorizer().fit_transform(sentences)
    normalized = TfidfTransformer().fit_transform(bow_matrix)
    similarity_graph = normalized * normalized.T
    nx_graph = nx.from_scipy_sparse_matrix(similarity_graph)
    scores = nx.pagerank(nx_graph)
    sentence_array = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    sentence_array = np.asarray(sentence_array)
    fmax = float(sentence_array[0][0])
    fmin = float(sentence_array[len(sentence_array) - 1][0])
    temp_array = []

    # Normalization
    for i in range(0, len(sentence_array)):
        if fmax - fmin == 0:
            temp_array.append(0)
        else:
            temp_array.append((float(sentence_array[i][0]) - fmin) / (fmax - fmin))
    threshold = (sum(temp_array) / len(temp_array)) + 0.2
    sentence_list = []
    for i in range(0, len(temp_array)):
        if temp_array[i] > threshold:
            sentence_list.append(sentence_array[i][1])
    seq_list = []
    for sentence in sentences:
        if sentence in sentence_list:
            seq_list.append(sentence)
    return seq_list

def summary(text):
    summary = ""
    summary_token = textrank(text)
    for i in summary_token:
        summary += i + " "
    return summary


def check_negativity():
    text = get_all_messages()
    r = requests.post(
        "https://api.deepai.org/api/sentiment-analysis",data={'text': text,},
                      headers={'api-key': '52057243-836c-4eee-9186-ebb1ef285947'})
    resp = r.json()
    sentiments=resp['output']
    negativity=(sentiments.count('Negative')/len(sentiments))
    return "{:.2f}%".format(negativity*100)

# def extract_keyword(text,frequencies=4):
#     keywords = []
#     input = urllib.parse.quote(text)
#     url = f"http://yake.inesctec.pt/yake/v2/extract_keywords?content={input}" \
#           f"&max_ngram_size=3&number_of_keywords=20&highlight=true"
#     response = requests.get(url)
#     res_json = response.json()
#     if res_json['keywords']:
#         keyword = sorted(res_json['keywords'], key=lambda x: x['score'])
#     for val in keyword[-frequencies:]:
#         keywords.append(val['ngram'])
#     return ','.join(keywords)

def extract_keyword(text, k=4):
    text = re.sub(r"<@[A-Z]\w+>","", text)
    rake_nltk_var = Rake()
    rake_nltk_var.extract_keywords_from_text(text)
    keyword_extracted = rake_nltk_var.get_ranked_phrases()
    return ','.join(keyword_extracted[:k])

def get_top_keywords(user=None):
    if user:
        return extract_keyword(get_messages_by_user(user))
    else:
        return extract_keyword(get_all_messages())