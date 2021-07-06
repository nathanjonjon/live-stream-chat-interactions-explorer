import boto3, time, os

AWS_S3_REGION = os.getenv('AWS_S3_REGION')
TRANSCRIBE_BUCKET = os.getenv('TRANSCRIBE_BUCKET')

class Transcriber():
    def __init__(self, username: str, video_id: str):
        self.username = username
        self.video_id = video_id
        self.client = boto3.client('transcribe', region_name=AWS_S3_REGION)

    def startTranscribeJob(self, filepath: str):
        filename = filepath.split('/')[-1]
        try:
            response = self.client.start_transcription_job(
                TranscriptionJobName='transcribe-{}-{}-{}'.format(self.username, self.video_id, filename),
                LanguageCode='en-GB', # get language code based on the username
                MediaFormat='wav',
                Media={
                    'MediaFileUri': 's3://{}/{}'.format(TRANSCRIBE_BUCKET, filepath)
                },
                OutputBucketName=TRANSCRIBE_BUCKET,
                OutputKey='{}/{}/transcriptions/'.format(self.username, self.video_id)
            )
        except self.client.exceptions.ConflictException:
            print('{} was processed already'.format(filename))

    def getTranscribeJob(self, filepath):
        filename = filepath.split('/')[-1]
        while True:
            try:
                response = self.client.get_transcription_job(
                    TranscriptionJobName='transcribe-{}-{}-{}'.format(self.username, self.video_id, filename)
                )
            except self.client.exceptions.BadRequestException as e:
                print('BadRequestException')
                return 1
            print(filename, response['TranscriptionJob']['TranscriptionJobStatus'])
            if response['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                break
            else:
                time.sleep(5)
        return 0



