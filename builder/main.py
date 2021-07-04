import json, os
from gensim import models, corpora
from gensim.models.ldamodel import LdaModel

class MyCorpus(object):
    def __init__(self, chatDocList, dictionary):
        self.chatDocList = chatDocList
        self.dictionary = dictionary
    def __iter__(self):
        for line in self.chatDocList:
            # assume there's one document per line, tokens separated by whitespace
            yield self.dictionary.doc2bow(line)

def buildLDAModel(target_path, video_id, chatDocList):
    ## build dictionary
    dictionary = corpora.Dictionary(chatDocList)
    dictionary.save('{}/{}.dict'.format(target_path, video_id))

    ## build corpus
    corpus_mm = MyCorpus(chatDocList, dictionary)
    corpora.MmCorpus.serialize('{}/{}_corpus.mm'.format(target_path, video_id), corpus_mm)
    corpus_mm = corpora.MmCorpus('{}/{}_corpus.mm'.format(target_path, video_id))
        
    ## train model
    num_topics = int(len(chatDocList)/10)
    try :
        lda = LdaModel(corpus=corpus_mm, id2word=dictionary, num_topics=num_topics, alpha=0.25, eta='auto', random_state=1, passes=3, iterations=70)
        temp_file = '{}/{}_lda_model'.format(target_path, video_id)
        lda.save(temp_file)
    except ZeroDivisionError:
        print('{} chatDocList is sparse'.format(target_path))
        return -1, '{} chatDocList is sparse'.format(target_path)
    except Exception as err:
        print('{} {}'.format(target_path, err))
        return -1, '{} {}'.format(target_path, err)
    else:
        print('LDA model built!')
        return 1, 'LDA model built!'

def main(username, video_id, target_path, chat_file_path, source):
    if source == 'twitch':
        from parser.twitch import Parser

    if source == 'youtube':
        from parser.youtube import Parser
    
    print('start parsing')
    parser = Parser(username, video_id, target_path, chat_file_path)

    chatTranscriptDict = parser.makeChatTranscriptDict()
    chatDocList, chatTimeDocDict = parser.makeNLPFiles()
    
    with open("{}/chatTranscriptDict.dict".format(target_path), 'w') as f:
        json.dump(chatTranscriptDict, f)
        f.close()
    with open('{}/{}_docList.txt'.format(target_path, video_id), 'w') as f:
        json.dump(chatDocList, f)
        f.close()
    with open('{}/{}_chatTimeDocDict.txt'.format(target_path, video_id), 'w') as f:
        json.dump(chatTimeDocDict, f)
        f.close()

    for filename in ['chatTranscriptDict.dict', '{}_docList.txt'.format(video_id), '{}_chatTimeDocDict.txt'.format(video_id)]:
        if not os.path.isfile('{}/{}'.format(target_path, filename)):
            return 1, 'builder missing files for building LDA model'
    print('start building LDA model')
    res, msg = buildLDAModel(target_path, video_id, chatDocList)
    if res < 0:
        return -1, msg

    for filename in ['{}_lda_model'.format(video_id), '{}_corpus.mm'.format(video_id)]:
        if not os.path.isfile('{}/{}'.format(target_path, filename)):
            return 1, 'LDA model is missing'
    return 0, 'succeeded'


        
    
