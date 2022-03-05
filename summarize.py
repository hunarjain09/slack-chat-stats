from collections import defaultdict
from email.policy import default
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


inputParam = defaultdict(list)

def summary(text):
    result = []
    LANGUAGE = "english"
    SENTENCES_COUNT = '10%'

    nltk.download('punkt')
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        result.append(sentence)

    return " ".join(result)
"""
Input: data =[(user,message),(user,message)]
"""
def parse_input(input):
    for user, message in input:
        inputParam[user].append(message)

def get_all_messages():
    return " ".join([item for sublist in inputParam.values() for item in sublist])

def get_messages_by_user(user):
    return " ".join(inputParam[user])

def summarize(payload):
    parse_input(payload)
    return summary(get_all_messages())
    
    

