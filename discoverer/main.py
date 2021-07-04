import os
import json
import re
import subprocess
from gensim.models.ldamodel import LdaModel
from gensim import models, corpora
from gensim.similarities.docsim import MatrixSimilarity, SparseMatrixSimilarity, Similarity
from utils import upload_file, download_file, makeClips, createMoment
from discoverer import Discoverer
from transcriber import Transcriber

TRANSCRIBE_BUCKET = os.environ['TRANSCRIBE_BUCKET']

def loadDictionaryAndCorpus(target_path: str, video_id: str):
    dictionary = corpora.Dictionary.load(
        '{}/{}.dict'.format(target_path, video_id))
    corpus_mm = corpora.MmCorpus(
        '{}/{}_corpus.mm'.format(target_path, video_id))
    return dictionary, corpus_mm


def loadLDAModel(target_path: str, video_id: str):
    temp_file = '{}/{}_lda_model'.format(target_path, video_id)
    lda = LdaModel.load(temp_file)
    return lda

def main(username: str, video_id: str, target_path: str, source: str):

    # load LDA model and dictionary
    dictionary, corpus_mm = loadDictionaryAndCorpus(target_path, video_id)
    lda = loadLDAModel(target_path, video_id)

    # find clusters for each topic
    f = open('{}/chatTranscriptDict.dict'.format(target_path), 'r')
    chatTranscriptDict = json.load(f)
    discoverer = Discoverer(lda, dictionary, chatTranscriptDict)
    top_chats = discoverer.findClusters(target_path, video_id)
    print('get 10 chat clusters from LDA')

    # make soundclips from top chat clusters
    timeList = [(chats['time'][0], chats['time'][-1]) for chats in top_chats]
    if not os.path.isdir('{}/soundclips_to_transcribe'.format(target_path)):
        subprocess.call(
            ['mkdir', '{}/soundclips_to_transcribe'.format(target_path)])
    all_filenames_path = [filename for filename in os.listdir(
        '{}/soundclips_to_transcribe'.format(target_path)) if 'wav' in filename]
    if all_filenames_path == []:
        filepaths = makeClips(target_path, username, video_id, timeList, source)
    else:
        filepaths = [('{}/{}/soundclips_to_transcribe/{}'.format(username, video_id, filename), True) for filename in all_filenames_path]
    if filepaths == []:
        print('soundclips missing')
        return 1, []
    print('soundclips made')
    # build transcriber
    transcribe = Transcriber(username, video_id)

    # upload soundclips to s3 and start a transcribe job
    for filepath, inDuration in filepaths:
        if not inDuration:
            continue
        upload_file('{}/{}'.format(target_path, filepath), TRANSCRIBE_BUCKET, filepath)
        transcribe.startTranscribeJob(filepath)

    # check job status, download JSON file and calculate the possibility of interaction
    if not os.path.isdir('{}/transcriptions'.format(target_path)):
      subprocess.call(['mkdir', '{}/transcriptions'.format(target_path)])

    interactions = []
    print('find interactions')
    for filepath, inDuration in filepaths:
      filename = filepath.split('/')[-1]
      start, end = (int(re.search('(.*)-(.*).wav', filename).group(1)),
                    int(re.search('(.*)-(.*).wav', filename).group(2)))

      if inDuration:
        if transcribe.getTranscribeJob(filepath) > 0:
            continue
        s3_filepath = 'transcriptions/transcribe-{}-{}-{}.json'.format(
            username, video_id, filename)
        download_file('{}/{}'.format(target_path, s3_filepath),
                      'transcribe-source-and-output', '{}/{}/{}'.format(username, video_id, s3_filepath))
        output = json.load(open('{}/transcriptions/transcribe-{}-{}-{}.json'.format(
            target_path, username, video_id, filename), 'r'))
        inputQuery = output['results']['transcripts'][0]['transcript']
      else:
        inputQuery = ''
      interactionFlag, keywords, keyChat = discoverer.isInteraction(
          inputQuery, start, end, top_chats)
      print(interactionFlag, keywords, keyChat)
      keyChatTime = keyChat[0]
      keyChatMsg = keyChat[1]
      if keyChatTime == 0 or keyChatMsg == '':
        continue
      if interactionFlag:
        interactions.append(createMoment(
            video_id, start-10, end+10, 'FAN INTERACTIONS', keywords, keyChatTime, keyChatMsg))
      else:
        interactions.append(createMoment(
            video_id, start-10, end+10, 'HIGH ACTIVITY', keywords, keyChatTime, keyChatMsg))

    print(interactions)
    return 0, interactions
