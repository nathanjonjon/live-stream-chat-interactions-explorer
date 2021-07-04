import json, os, string
from utils import timeStamp2Datetime, stopwords_remove, remove_emoji
import en_core_web_sm
from nltk.stem.porter import PorterStemmer
nlp = en_core_web_sm.load()
ps=PorterStemmer()

BASE_FILE_PATH = '/code'

class Parser():
    def __init__(self, username, video_id, target_path, chat_file_path):
        self.username = username
        self.video_id = video_id
        self.target_path = target_path
        self.chat_file_path = chat_file_path
        self.chatDict = json.load(open(chat_file_path, 'r'))
        self.video_start_time = self.chatDict['video']['created_at']

    def makeChatTranscriptDict(self):
        chatTranscriptDict = {'version': 1, 'chat_messages': []}
        video_start_time = timeStamp2Datetime(self.chatDict['video']['created_at'])
        for item in self.chatDict['comments']:
            time = timeStamp2Datetime(item['created_at'])
            original_text = item['message']['body']
            commenter_name = item['commenter']['display_name']

            single_chat_info = {
                't': int((time - video_start_time).total_seconds()),
                'u': commenter_name,
                'msg': original_text
            }
            chatTranscriptDict['chat_messages'].append(single_chat_info)

        return chatTranscriptDict

    def makeNLPFiles(self):
        chatTimeDocDict = []
        chatDocList = []
        chatTimeList = []
        filtered = []
        time_period = []
        video_start_time = timeStamp2Datetime(self.chatDict['video']['created_at'])
        comment_start_time = timeStamp2Datetime(self.chatDict['comments'][0]['created_at'])
        for item in self.chatDict['comments']:
            time = timeStamp2Datetime(item['created_at'])
            original_text = ""
            try:
                fragments = item['message']['fragments']
            except KeyError:
                print('fragments not a key')
                continue
            for fragment in fragments:
                if 'emoticon' in fragment:
                    continue
                else:
                    original_text = original_text+fragment['text']

            ## remove emotes
            emotes_vocab_list = json.load(open(f"{BASE_FILE_PATH}/builder/parser/twitch/emotes_vocab.txt", 'r'))
            original_text = ' '.join([term for term in original_text.split(' ') if term not in emotes_vocab_list])

            ## remove punctuations and emojis
            ## lower all letters
            processed_text = remove_emoji(original_text.translate(str.maketrans('', '', (string.punctuation+'’'))).lower())
            
            ## remove digits and words that contain non-alphabet char and http
            processed_text = ''.join(i for i in processed_text if not i.isdigit())
            processed_text = ' '.join([term for term in processed_text.split(' ') if term.isalpha() and 'http' not in term])

            ## remove stop words, prep, conj, etc.
            doc = nlp(processed_text)
            processed_text = stopwords_remove([token.text for token in doc if len(token.text) > 1 and token.pos_ in ['PROPN', 'VERB', 'NOUN', 'ADJ', 'ADV']])
            
            ## stemming
            processed_text = [ps.stem(w) for w in processed_text]

            filtered = filtered+processed_text
            if int((time - video_start_time).total_seconds()) not in time_period:
                time_period.append(int((time - video_start_time).total_seconds()))
            
            if (time - comment_start_time).total_seconds() >= 15:
                if filtered != []:
                    chatTimeDocDict.append({'time': time_period, 'doc': filtered})
                    chatDocList.append(filtered)
                    chatTimeList.append(time_period)
                    comment_start_time = time
                    filtered = []
                    time_period = []
        
        return chatDocList, chatTimeDocDict





