import argparse
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import chat_downloader
import builder
import discoverer

BASE_FILE_PATH = '/code'

class ChatDownloaderError(Exception):
	pass

class BuilderError(Exception):
	pass

class DiscovererError(Exception):
	pass

def create_dir(username, video_id):
    target_path = '{}/{}/{}'.format(BASE_FILE_PATH, username, video_id)
    Path(target_path).mkdir(parents=True, exist_ok=True)
    return target_path

class ChatExplorer():
    def __init__(self, username, video_id, source):
        self.username = username
        self.video_id = video_id
        self.source = source
        self.target_path = create_dir(username, video_id)
        self.chat_file_path = ""
        self.interactions = []
    
    def chat_download(self):
        chat_file_path = chat_downloader.main(self.username, self.video_id, self.target_path, self.source)
        if not chat_file_path:
            raise ChatDownloaderError()
        self.chat_file_path = chat_file_path
        return

    def build(self):
        status, msg = builder.main(self.username, self.video_id, self.target_path, self.chat_file_path, self.source)
        if status != 0:
            raise BuilderError(f'{self.username}, {self.video_id}, builder.py failed, {msg}, possibly because the stream was too short.')
        return

    def discover(self):
        status, interactions = discoverer.main(self.username, self.video_id, self.target_path, self.source)
        if status != 0 or interactions == []:
            raise DiscovererError(f'{self.username}, {self.video_id}, discoverer could not find any interactions')
        self.interactions = interactions

    def show_results(self):
        print(f"Interactions found: {self.interactions}")


def main(username: str, url: str) -> None:
    o = urlparse(url)
    if o.netloc not in ['www.twitch.tv', 'www.youtube.com']:
        print(f'url: {url} is unformatted.')
        return
    if o.netloc == 'www.twitch.tv':
        source = 'twitch'
        video_id = o.path.split('/')[-1]

    if o.netloc == 'www.youtube.com':
        source = 'youtube'
        video_id = parse_qs(o.query)['v'][0]

    chat_explorer = ChatExplorer(username, video_id, source)
    chat_explorer.chat_download()
    chat_explorer.build()
    chat_explorer.discover()
    chat_explorer.show_results()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username")
    parser.add_argument("url", help="url")
    args = parser.parse_args()
    username = args.username
    url = args.url
    main(username, url)
