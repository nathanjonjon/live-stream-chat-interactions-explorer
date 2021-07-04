from spacy.lang.en.stop_words import STOP_WORDS
import json, os, subprocess, re, boto3
from botocore.exceptions import ClientError

def createMoment(video_id, start, end, label, keyword, keyChatTime, keyChatMsg):
    if len(keyword) == 0:
      description = keyChatMsg
    else:
      description = 'keywords: "{}"\n{}'.format(keyword.replace(' ', ', '), keyChatMsg)
    payload = {
        "video": str(video_id),
        "context": {
            "start_seconds": int(start),
            "end_seconds": int(end),
            "description": description
        },
        "category": "CHAT_EVENT",
        "source": "CHAT_LOG",
        "video_time": int(keyChatTime),
        "label": label
    }
    return payload

def stopwords_remove(filtered):
    no_chars = ["'", "’", "‘"]
    stop = list(STOP_WORDS)+['', 'cant', 'lol', 'ok',
                             'wow', 'xd', 'hi', 'ya', 'yay', 'np']
    for i in range(len(stop)):
        for c in stop[i]:
            if c in no_chars:
                stop[i] = stop[i].replace(c, "")
    return [n for n in filtered if n not in stop]

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

def upload_file(file_name, bucket, object_name):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        return False
    return True

def download_file(file_name, bucket, object_name):
  if object_name is None:
      object_name = file_name
  s3_client = boto3.client('s3')
  try:
      response = s3_client.download_file(bucket, object_name, file_name)
  except ClientError as e:
      return False
  return True


def getRawAudioDuration(target_path: str, video_id: str, source: str) -> int:
    f = open(f'{target_path}/{video_id}.json', 'r')
    chatDict = json.load(f)
    res = list(re.search('(.*)h(.*)m(.*)s', chatDict['duration']).group(1,2,3))
    w = [3600, 60, 1]
    duration = sum([w[i] * int(res[i]) for i in range(3)])
    return duration

def makeClips(target_path: str, username: str, video_id: str, timeList: list, source: str):
    wav_file_path = '{}/{}.wav'.format(target_path, video_id)
    if not os.path.isfile(wav_file_path):
        return []
    duration = getRawAudioDuration(target_path, video_id, source)
    path = '{}/soundclips_to_transcribe'.format(target_path)
    if not os.path.isdir(path):
        subprocess.call(['mkdir', path])

    filepaths = []
    for item in timeList:
        start = item[0]
        end = item[1]
        output_path = '{}/{}/soundclips_to_transcribe/{}-{}.wav'.format(username, video_id, start, end)
        inDuration = ((start-30) in range(duration) and end in range(duration))
        filepaths.append((output_path, inDuration))
        if not inDuration:
          continue
        subprocess.call(['ffmpeg', '-ss', str(start-30), '-i', wav_file_path, '-t', str(end-start+30), '-acodec', 'copy', '{}/{}-{}.wav'.format(path, start, end), '-y'])
    return filepaths



