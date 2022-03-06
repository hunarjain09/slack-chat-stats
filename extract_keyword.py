import requests
import urllib.parse
def extract_keyword(text):
  keywords=[]
  input = urllib.parse.quote(text)
  url=f"http://yake.inesctec.pt/yake/v2/extract_keywords?content={input}&max_ngram_size=3&number_of_keywords=20&highlight=true"
  x = requests.get(url)
  a = x.json()
  if a['keywords']:
    keyword=sorted(a['keywords'],key=lambda x : x['score'])
  for val in keyword[-4:]:
    keywords.append(val['ngram'])
  return keywords