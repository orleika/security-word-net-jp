from gscrapy import GoogleScrapy
from clean import Clean
from stopword import StopWord
from tokenizer import MeCabTokenizer
from tfidf import TfIdf
from pprint import pprint
from itertools import chain
from db import DB

def search_articles(keyword):
    google = GoogleScrapy(keyword.word)
    google.start()
    return google.articles

def tokenize(articles):
    results = []
    tokenizer = MeCabTokenizer(user_dic_path = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    for article in articles:
        clean = Clean(article.html)
        cleaned = clean.clean_html_and_js_tags().clean_text().clean_code()
        tokens = tokenizer.extract_noun_verbs_baseform(cleaned.text)
        results.append(tokens)
    return list(chain.from_iterable(results))

def trimmed_stopwords(db, tokens):
    stopwords = db.get_stopwords()
    sw = StopWord(tokens = tokens, stopwords = [stopword.word for stopword in stopwords])
    return sw.remove_stopwords()

def extract_keywords(keywords, tokens):
    df_list = [keyword.word for keyword in keywords]
    tfidf = TfIdf(df_list = df_list)
    return tfidf.new_keywords(tokens)

def save_new_keywords(db, keyword, tokens):
    for token in tokens:
        if not db.exist_word(token.word):
            pos= 1 if token.pos == '名詞' else 2
            db.save(token.word, keyword.layer + 1, pos, keyword.id)

def main():
    db = DB(host = 'mysql')
    keywords = db.max_layer()
    for keyword in keywords:
        articles = search_articles(keyword)
        tokens = tokenize(articles)
        trimmed_tokens = trimmed_stopwords(db, tokens)
        new_keywords = extract_keywords(keywords, trimmed_tokens)
        pprint(new_keywords)
        save_new_keywords(db, keyword, new_keywords)

if __name__ == '__main__':
    main()