import json, os, string, re
import en_core_web_sm
from nltk.stem.porter import PorterStemmer
from utils import timeStamp2Datetime, ms_timeStamp2Datetime, stopwords_remove, remove_emoji
nlp = en_core_web_sm.load()
ps=PorterStemmer()

CHAT_EFS_FILE_PATH = '/mnt/efs/files'

class ChatFileNotExist(Exception):
    pass

class Parser():
    def __init__(self, username, video_id, target_path, chat_file_path):
        self.username = username
        self.video_id = video_id
        self.target_path = target_path
        self.chat_file_path = chat_file_path
        self.chatDict = json.load(open(chat_file_path, 'r'))
        self.video_start_time = timeStamp2Datetime(self.chatDict['created_at'])

    def makeChatTranscriptDict(self):
        chatTranscriptDict = {'version': 1, 'chat_messages': []}
        for item in self.chatDict['chats']:
            time = ms_timeStamp2Datetime(item['timestamp'])
            original_text = item['message']
            commenter_name = item['author']['name']

            single_chat_info = {
                't': int((time - self.self.video_start_time).total_seconds()),
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
        comment_start_time = ms_timeStamp2Datetime(self.chatDict['chats'][0]['timestamp'])
        for item in self.chatDict['chats']:
            time = ms_timeStamp2Datetime(item['timestamp'])
            original_text = item['message']


            ## remove emojis (:thumb-up:)
            original_text = re.sub("\:.*?\:", "", original_text)

            ## remove punctuations and other emojis
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
            # print(processed_text)

            filtered = filtered+processed_text
            if int((time - self.video_start_time).total_seconds()) not in time_period:
                time_period.append(int((time - self.video_start_time).total_seconds()))
            
            if (time - comment_start_time).total_seconds() >= 15:
                if filtered != []:
                    chatTimeDocDict.append({'time': time_period, 'doc': filtered})
                    chatDocList.append(filtered)
                    chatTimeList.append(time_period)
                    comment_start_time = time
                    filtered = []
                    time_period = []
        
        return chatDocList, chatTimeDocDict





