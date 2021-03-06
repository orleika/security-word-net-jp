# -*- coding: utf-8 -*-
from gsearch import GoogleScrapy
from clean import Clean
from stopword import StopWord
from tokenizer import MeCabTokenizer
from tfidf import TfIdf
from db import DB
import numpy
import re
from itertools import chain
from pprint import pprint

class Theme:

    def __init__(self, theme):
        self.theme = theme

    @staticmethod
    def search_articles(keywords):
        search_word = ' '.join(keywords)
        google = GoogleScrapy(search_word)
        google.start()
        return google.articles

    @staticmethod
    def tokenize(sentence, pos='default'):
        tokenizer = MeCabTokenizer(user_dic_path = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        if pos == 'noun':
            tokens = tokenizer.extract_noun_baseform(sentence)
        elif pos == 'verbs':
            tokens = tokenizer.extract_verbs_baseform(sentence)
        elif pos == 'noun_verbs':
            tokens = tokenizer.extract_noun_verbs_baseform(sentence)
        else:
            tokens = tokenizer.extract_baseform(sentence)
        return tokens

    @staticmethod
    def tokenize_surface(pos='noun_verbs'):
        def surface(sentence):
            return [token.surface for token in Theme.tokenize(sentence, pos)]

    @staticmethod
    def clean(sentence):
        return Clean(sentence).clean_html_and_js_tags().clean_text().text

    @staticmethod
    def trimmed_stopwords(tokens):
        db = DB(host = 'mysql')
        stopwords = db.get_stopwords()
        sw = StopWord(tokens = tokens, stopwords = [stopword.word for stopword in stopwords])
        return sw.remove_stopwords()

    @staticmethod
    def divide(article):
        return list(filter(None, map(str.strip, re.findall(r'[^。．？！…?!　\n]+(?:[。。．？！…?!　\n]|$)', article))))

    @staticmethod
    def is_sentence(sentence):
        tokens = Theme.tokenize(sentence, pos='verbs')
        if len(tokens) == 0 or len(sentence) > 100 or len(sentence) < 10:
            return False
        else:
            return True

    # input: keywords
    # output: articles
    def search():
        return

    # input: articles
    # output: [[nouns, verb][...]...]
    def extract_noun():
        return

    # input: sentences,
    def clustering():
        return

    def get(self):
        # standardize
        keywords = self.trimmed_stopwords(self.tokenize(self.theme, pos='noun_verbs'))
        # search about theme
        articles = self.search_articles([keyword.surface for keyword in keywords][:3])
        # clean
        docs = map(self.clean, articles)
        # divide sentences
        sentences_cand = map(self.divide, docs)
        sent = []
        for s in sentences_cand:
            sent.append(list(filter(self.is_sentence, s)))
        sentences = list(chain.from_iterable(sent))
        # tfidf format
        sentence_tokens = []
        for sentence in sentences:
            noun_tokens = [token.surface for token in self.tokenize(sentence, pos='noun')]
            sentence_tokens.append(' '.join(noun_tokens))
        # vectorize
        vector = TfIdf.vector(sentence_tokens)
        # clustering
        cluster = numpy.array(TfIdf.cluster(vector, clusters=3))
        # retrieve opinion with tf
        tfidf_score_index = numpy.argsort(numpy.array([sum(v) for v in vector.toarray()]))[::-1]
        opinions = []
        for i in range(3):
            # retrieve vector index by cluster
            c_index = numpy.where(cluster == i)
            for k in tfidf_score_index:
                if k in c_index[0]:
                    opinions.append(sentences[k])
                    break
        return opinions
