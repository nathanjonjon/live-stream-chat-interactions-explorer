import os, subprocess, json, requests, re

class ChatFileNotExist(Exception):
    pass

class ExternalAPIFail(Exception):
    pass

class ResponseUnexpected(Exception):
    pass

def twtich(username, video_id, target_path):
    ## may need to prepare your own setting.json to fetch chat logs from Twtich with tcd
    response_code = subprocess.call(['tcd', '-v', str(video_id), '-f', 'json', '-o', target_path])
    
    if response_code != 0 or not os.path.isfile('{}/{}.json'.format(target_path, video_id)):
        raise ChatFileNotExist()
    
    chat_file_path = f'{target_path}/{video_id}.json'
    return chat_file_path


def youtube(username, video_id, target_path):
    ## get video info from YouTube
    ## may need to register an api key to fetch info of a video
    API_KEY = os.getenv('YT_API_KEY')
    YT_API_BASE_URL = 'https://www.googleapis.com/youtube/v3/'
    YT_API_ENDPOINT = f'{YT_API_BASE_URL}videos?part=contentDetails,liveStreamingDetails&id={video_id}&key={API_KEY}'

    r = requests.get(YT_API_ENDPOINT)
    if r.status_code != 200:
        raise ExternalAPIFail(r.text)
    try:
        video_info = json.loads(r.text)
        created_at = video_info['items'][0]['liveStreamingDetails']['actualStartTime']
        duration = video_info['items'][0]['contentDetails']['duration']
        res = re.search("PT(([0-9]*)H)?([0-9]+)M([0-9]+)S", duration)
        if res.group(2):
            duration = f"{res.group(2)}h{res.group(3)}m{res.group(4)}s"
        else:
            duration = f"0h{res.group(3)}m{res.group(4)}s"
    except Exception as e:
        raise ResponseUnexpected(f"Unexpected error: {e}")
        
    ## download chats and build video info
    from chat_downloader import ChatDownloader
    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    all_chat_list = []
    chat_logs = ChatDownloader().get_chat(yt_url)
    for chat in chat_logs:
        all_chat_list.append(chat)

    video_chat_info = {
        'username': username,
        'video_id': video_id,
        'created_at': created_at,
        'duration': duration,
        'chats': all_chat_list
    }

    ## write file in base path
    with open(f'{target_path}/{video_id}.json', 'w') as f:
        json.dump(video_chat_info, f)
    f.close()
    chat_file_path = f'{target_path}/{video_id}.json'
    return chat_file_path

