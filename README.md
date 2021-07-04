# Live Stream Chat Interactions Explorer

This is an AI tool that helps users fetch chat logs and find interactions during a live stream. Currently, it supports 2 sources, Twitch and Youtube, using `LDA` for topic modeling and `AWS Transcribe` for converting audio clips to texts as quries to infer the model.

## Project Structure

- `chat_downloader` : Fetch stream information and chat logs by calling Twitch/Youtube API.
- `builder` : Parse the raw data returned by API and build corpus, dictionary and model.
- `discoverer` : Find the representative chats among all and indicate if they are moments where viewers are interacting with each other are with the streamer.
    -  `transcriber.py` : Transcribe audio clips (assuming `[video_id].wav` exists) according to the chats that could be potenital interactions by using [AWS Transcribe](https://aws.amazon.com/transcribe/)
- `sample` : A sample that contains the results of a [stream](https://www.twitch.tv/1049589594) belonging to a famous Twitch streamer natt3a. It includes chat logs, corpus, dictionary, transcriptions and some temp files.


## Data Preprocessing
1. Remove Twitch/Youtube emotes, emojis and punctuations
2. Remove digits, words in foreign language and urls
3. Remove stop words
4. Extract `PROPN`, `VERB`, `NOUN`, `ADJ`, `ADV` using `en_core_web_sm`
5. Stemming with `nltk.stem.porter.PorterStemmer`
6. Create a document with the preprocessed chat content within 15 seconds


## Usage
```
python3 chat_explorer.py [streamer_username] [stream_video_link]
```


## Sample Results

None of the chats is labeled since they are raw data from the provider; also, with the lack of enough compute resources to fine-tune the model or transcribe the whole stream, the hyperparameters are somewhat hardcoded and it only infers the model with the transcription when it finds potential interactions. However, my current algorithm works well on about 100 streams despite low recall rate sometimes, and it's capable of helping people find interesting moments in a stream.

- **FAN INTERACTIONS** : Topics that intensive chats and the streamer are talking about. Below shows a list of chats and the key words which involve in the chats and transcription andw may be the topics of their interactions.
    | Timestamp | Chat | Keywords |
    | --- | --- | --- |
    | 00:55:42 | never sell wtf | `"sell"` |
    | 01:03:33 | twitch has twittered they are working on their twitching | `"streaming, fine, work, video"` |
    | 01:05:25 | yes, you would be the favorite person at the 6-year olds birthday party if you could face ... | `"face, paint"` |
    | 01:06:26 | youre more likely to get ppl that want face paint lets be real | `"face, paint"` |
    | 01:13:15 | i mean, you would be perfect for an Australian Disney princess? | `"australian, disney"` |
    | 01:26:25 |  I like listening to podcasts of people just talking about | `"talk, podcast, cares, opinions, care, acting"` |  

- **HIGH ACTIVITY** : Intensive chats with a topic that may indicate an interaction among viewers. Below shows a list of the most representative chats.
    | Timestamp | Chat |
    | --- | --- |
    | 00:04:57 | nice password |
    | 00:06:41 | look mate, we promised we could do this in our tender proposal. You don't want me to  |be a LIAR, do you?!
    | 00:09:08 | talent announcements aren't an ESL thing anymore |
    | 00:10:48 | sure sure, what's your address, credit card number and first pet name, mothers maiden  |name
    | 00:12:24 | Hello this is SnypeR's mum. I've seen the way you speak to my son and I will not allow  |you to communicate with him 
    | 00:13:20 | everything is great in a fruit salad except buying the individual parts |
    | 00:17:58 | Brows be on point rn |
    | 00:22:27 | I haven't played league of legos for 6 years |
    | 00:24:45 | q max for maximum attack speed Kreygasm |
    | 00:30:15 | you would think a 'carry' role would be more impactful |
    | 00:30:53 | fax on fax on fax |
    | 00:32:01 | hi nat |
    | 00:32:46 | back in season 3 and 4 |
    | 00:38:14 | ranked or normal? |
    | 00:41:47 | ah dota |
    | 00:42:03 | ye I stopped playing league after season 4 |
    | 00:42:27 | this glass cannon stuff won't get you anywhere in dota |
    | 00:43:57 | i swear dota characters can kill me off screen |
    | 00:44:46 | also the shop is hella confusing |
    | 00:45:02 | i reckon league is easier to get into but i guess it’s really about what you play  |first
    | 00:46:10 | Been a minute |
    | 00:47:17 | Yeah, it'd be nice if they paid us to do nothing, that sounds fair to Saph :) |
    | 00:47:48 | tarzCrab |
    | 00:48:31 | kha’zix > rengar |
    | 00:49:00 | Ahhh, you got a supervisor that can't really handle pressure XD |
    | 00:50:12 | Been watching other streams and twitch , twitter and amazon are all down |
    | 00:50:13 | just finished first sem of software engo |
    | 00:51:39 | Yeah they are all down. We can't open another stream or there is an error |
    | 00:53:48 | I only opened Nats stream 8 minutes ago to be fair |
    | 00:56:01 | rip lol |
    | 00:56:26 | @rachemist lord dominiks regards as an adc |
    | 00:56:50 | if you dont need crit you can go seryldas or black cleaver |
    | 00:57:02 | bork is good against armor stackers |
    | 00:57:59 | i talked to him yesterday about giving me a raise and he said i had to take a class  |to get a cert and then i could...
    | 00:58:56 | thing is you need to do damage (which you need items for) for the lifesteal to be  |effective
    | 00:59:42 | so let your teammates deal with him or deal with him last |
    | 01:00:00 | twitch is twitching |
    | 01:03:31 | Saph can't even see the viewer count :P |
    | 01:06:48 | absolutely |
    | 01:07:44 | Yeah amazon twitter and many other websites apparently |
    | 01:14:33 | seriously? deepjimpact? hosted gfinity rocket league abc 10am |
    | 01:16:11 | black couch |
    | 01:16:47 | you know manic monday? |
    | 01:16:54 | yeah i read a book on it because i was trying to be helpful for you know who |
    | 01:17:52 | remember all those commercials hes been in |
    | 01:19:37 | wdym? youre a great actor, you pretend like you like us all the time :D |
    | 01:20:22 | you just have to submit the paperwork to them and get approved |
    | 01:21:17 | oh yes, a podcast could also get you into the guild |
    | 01:22:13 | RIP!!! |
    | 01:22:32 | she handles rejection well |
    | 01:24:02 | You should start your own podcast and become more successful |
    | 01:24:46 | we would let you plug your lco job |
    | 01:25:38 | damn this man really said the podcast is dead so you'd be a perfect fit for it |
    | 01:28:15 | Nat will be remembered |
    | 01:29:30 | I think old mate percy let out an EMP |
    | 01:30:10 | cuz the publo26 thing is still scrolling |
    | 01:30:50 | Okay soooo something is wrong with m y computer haha |
    | 01:32:21 | Just use microsoft paint and draw a pic of you. That will do right |
    | 01:33:24 | no internet in Melbourne ay |
    | 01:34:04 | typing oon a notepad |
    | 01:34:22 | juves stream is in the same boat |
    | 01:34:47 | hard reset |
    | 01:35:53 | take of your robe and wizard hat |
