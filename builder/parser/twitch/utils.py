import json, re
from datetime import datetime as dt

def timeStamp2Datetime(timeStamp: str) -> dt:
#     timeStamp = '2020-07-05T17:29:56.891Z'
    timeStamp = timeStamp[0:10].split('-')+timeStamp[11:19].split(':')
    time = dt(int(timeStamp[0]), int(timeStamp[1]), int(timeStamp[2]), hour=int(timeStamp[3]), minute=int(timeStamp[4]), second=int(timeStamp[5]))
    return(time)


def ms_timeStamp2Datetime(ms_timeStamp: int) -> dt:
    return dt.fromtimestamp(int(ms_timeStamp/1000000))


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

from spacy.lang.en.stop_words import STOP_WORDS
def stopwords_remove(filtered):
    no_chars = ["'", "’", "‘"]
    stop = list(STOP_WORDS)+['', 'cant', 'lol', 'ok', 'wow', 'xd', 'hi', 'ya', 'yay', 'np']
    for i in range(len(stop)):
        for c in stop[i]:
            if c in no_chars:
                stop[i] = stop[i].replace(c, "")
    return [n for n in filtered if n not in stop]


def getRawAudioDuration(chat_target_path: str, videoID: str) -> int:
    f = open(f'{chat_target_path}/{videoID}.json', 'r')
    chatDict = json.load(f)
    res = list(re.search('(.*)h(.*)m(.*)s', chatDict['duration']).group(1,2,3))
    w = [3600, 60, 1]
    duration = sum([w[i] * int(res[i]) for i in range(3)])
    return duration

