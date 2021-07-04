import json, gensim, string
from nltk.stem.porter import PorterStemmer
import en_core_web_sm
from utils import stopwords_remove, remove_emoji

class Discoverer():
    def __init__(self, lda, dictionary, chatTranscriptDict):
        self.nlp = en_core_web_sm.load()
        self.ps = PorterStemmer()
        self.lda = lda
        self.dictionary = dictionary
        self.chatTranscriptDict = chatTranscriptDict

    def calculateSimilarity(self, query, target):
        return gensim.matutils.cossim(query, target)

    def queryProcess(self, query):
        ## query processing
        
        query = remove_emoji((query).translate(str.maketrans('', '', (string.punctuation+'’'+'\n'))).lower())
        query = ''.join(i for i in query if not i.isdigit())
        query = ' '.join([term for term in query.split(' ') if term.isalpha() and 'http' not in term])
        doc = self.nlp(query)
        query = stopwords_remove([token.text for token in doc if len(token.text) > 1 and token.pos_ in ['PROPN', 'VERB', 'NOUN', 'ADJ', 'ADV']])     
        query_stemmed = [self.ps.stem(w) for w in query]
        query_doc2bow = self.dictionary.doc2bow(query_stemmed)
        query_doc2bow = self.lda[query_doc2bow]
        if query_doc2bow == []:
            # print('term not exist')
            return [], [], []
            # terms too scrace are filtered by LDA
        return query_doc2bow, query_stemmed, query

    def findClusters(self, target_path: str, video_id: str, debug: bool=True):
        top_tens = []
        for topic in self.lda.print_topics(num_topics=10, num_words=20):
          #print('topic is:',topic)
          top_tens.append([self.dictionary[term[0]] for term in self.lda.get_topic_terms(topic[0])])
        
        all_chats = json.load(open('{}/{}_chatTimeDocDict.txt'.format(target_path, video_id), 'r'))
        top_chats = []
        for topic in top_tens:
            topic_doc = ' '.join(topic)
            topic_doc, topic_stemmed, topic_text = self.queryProcess(topic_doc)
            for chats in all_chats:
                representative = {'msg': '','t': 0, 'num': -1}
                texts = ' '.join(chats['doc'])
                time = chats['time']
                chats, chats_stemmed, chats_text = self.queryProcess(texts)
                similarity = self.calculateSimilarity(topic_doc, chats)
                if similarity > 0.9:
                    chat_candidates = [(chat_raw_data['msg'], chat_raw_data['t']) for chat_raw_data in self.chatTranscriptDict['chat_messages'] if chat_raw_data['t'] in time]
                    for item in chat_candidates:
                        if 'http' in item[0]:
                            continue
                        # print(item[0])
                        chats, chats_stemmed, chats_text = self.queryProcess(item[0])
                        if chats == []:
                            continue
                        commonTerms = set(topic_stemmed).intersection(chats_stemmed)
                        keywords = [chats_text[i] for i in range(len(chats_stemmed)) if chats_stemmed[i] in commonTerms]
                        if len(keywords) > representative['num']:
                            representative = {'msg': item[0],'t': item[1], 'num': len(keywords)}
                    top_chats.append({'time': time, 'text': texts, 'keyChat': representative})
        return top_chats

    def isInteraction(self, transcription: str, start: int, end: int ,top_chats: list):
      query, query_stemmed, query_text = self.queryProcess(transcription)
      for chat in top_chats:
        if start in chat['time'] and end in chat['time']:
          target, target_stemmed, target_text = self.queryProcess(chat['text'])
          similarity = self.calculateSimilarity(query, target)

          ## return key words of the topic
          if similarity > 0.2:
            commonTerms = set(query_stemmed).intersection(target_stemmed)
            keywords = [query_text[i] for i in range(len(query_stemmed)) if query_stemmed[i] in commonTerms]
            if len(keywords) <= 1:
                return (False, '', (chat['keyChat']['t'], chat['keyChat']['msg']))
            output = []
            for term in keywords:
                if term in output:
                    continue
                output.append(term)
            output = ' '.join(output)
            return (True, output, (chat['keyChat']['t'], chat['keyChat']['msg']))
          return (False, '', (chat['keyChat']['t'], chat['keyChat']['msg']))
