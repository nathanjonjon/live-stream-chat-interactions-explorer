import chat_download
def main(username: str, video_id: str, target_path: str, source: str):
    if source == 'twitch':
        chat_file_path = chat_download.twtich(username, video_id, target_path)
        return chat_file_path
    if source == 'youtube':
        chat_file_path = chat_download.youtube(username, video_id, target_path)
        return chat_file_path
    return ''
    
