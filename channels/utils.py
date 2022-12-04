from googleapiclient.discovery import build
import json
import pandas as pd
from nltk.corpus import stopwords
from nrclex import NRCLex
import re
from datetime import datetime

category_list = {"1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music", "15": "Pets & Animals", "17": "Sports", "18": "Short Movies", "19": "Travel & Events", "20": "Gaming", "21": "Videoblogging", "22": "People & Blogs", "23": "Comedy", "24": "Entertainment", "25": "News & Politics", "26": "Howto & Style", "27": "Education",
                 "28": "Science & Technology", "29": "Nonprofits & Activism", "30": "Movies", "31": "Anime/Animation", "32": "Action/Adventure", "33": "Classics", "34": "Comedy", "35": "Documentary", "36": "Drama", "37": "Family", "38": "Foreign", "39": "Horror", "40": "Sci-Fi/Fantasy", "41": "Thriller", "42": "Shorts", "43": "Shows", "44": "Trailers"}
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]



def get_channel_id(channel_name):
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQ85p4MhtQ9kPfpdlE7sa-hYpzjYgR-Fk'
    youtube = build('youtube', 'v3', developerKey=api_key)
    yt_r = youtube.search().list(
        part="id",
        maxResults=1,
        order="relevance",
        q=channel_name,
        type="channel"
    )
    response = yt_r.execute()

    return response['items'][0]['id']['channelId']


def get_channel_stats(channel_id):
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQ85p4MhtQ9kPfpdlE7sa-hYpzjYgR-Fk'
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.channels().list(
        part='snippet,contentDetails',
        id=channel_id)
    response = request.execute()
    data = dict(title=response['items'][0]['snippet']['title'],
                uploadId=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
    return data


def get_all_videos(uploads):
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQ85p4MhtQ9kPfpdlE7sa-hYpzjYgR-Fk'
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_videos = []
    nextPageToken = 'temp'
    flag = True

    while flag:
        if nextPageToken is None:
            flag = False
        else:
            if nextPageToken == 'temp':
                request = youtube.playlistItems().list(part='contentDetails,snippet',
                                                       playlistId=uploads, maxResults=50)
            else:
                request = youtube.playlistItems().list(part='contentDetails,snippet',
                                                       playlistId=uploads, maxResults=50, pageToken=nextPageToken)
            response = request.execute()
            nextPageToken = response.get('nextPageToken')
            for i in range(len(response['items'])):
                if not response['items'][i]['snippet']['publishedAt'].startswith('2022'):
                    flag = False
                    break
                all_videos.append(
                    response['items'][i]['contentDetails']['videoId'])

    return get_video_data(all_videos)


def get_video_data(videos):
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQ85p4MhtQ9kPfpdlE7sa-hYpzjYgR-Fk'
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_video_data = []

    for i in range(0, len(videos), 50):
        request = youtube.videos().list(
            part="snippet,statistics,status",
            id=','.join(videos[i:i+50])
        )

        response = request.execute()
        for video in response['items']:
            if 'viewCount' in video['statistics']:
                data = dict(

                    month=months[int(
                        video['snippet']['publishedAt'].split("-")[1]) - 1],
                    day =  days[datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").weekday()],
                    channel=video['snippet']['channelTitle'],
                    view=int(video['statistics']['viewCount']),
                    like=int(video['statistics'].get('likeCount', 0)),
                    comment=int(video['statistics'].get('commentCount', 0)),
                )
                all_video_data.append(data)

    return all_video_data


def group_data(rawData):
    grouped_data = []
    for key in rawData:
        grouped_data.append(dict(month="", name=key, n=0))
        temp_dict = {}
        for video in rawData[key]:
            m = video['month']
            temp_dict[m] = temp_dict.get(m, 0) + video['view']
        for m in months:
            grouped_data.append(dict(month=m, name=key, n=temp_dict.get(m, 0)))
    return grouped_data

def bubble_data(rawData):
    bubbles = []
    for key in rawData:
        temp_dict = {}
        l = len(rawData[key])
        # print(l)
        for video in rawData[key]:
            d = video['day']
            if video['view'] != 0:
                temp_dict[d] = temp_dict.get(d, 0) + (video['like']/video['view'])
            temp_dict[d+"r"] = temp_dict.get(d+"r",0) + video['comment']
        for d in days:
            avg_ratio = round(temp_dict.get(d,0)*100/l,2)
            avg_comment = round(temp_dict.get(d+"r",0)/l)
            # print(d, temp_dict.get(d), temp_dict.get(d+"r"))
            bubbles.append(dict(x=d, name=key, y=avg_ratio, r=avg_comment))
    return bubbles
def comment_sentiment(channelId):
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQ85p4MhtQ9kPfpdlE7sa-hYpzjYgR-Fk'
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.commentThreads().list(
        part="snippet",
        allThreadsRelatedToChannelId=channelId,
        maxResults=100
    )
    response = request.execute()

    comment_text = ""
    for item in response['items']:
        comment_text += item['snippet']['topLevelComment']['snippet']['textDisplay']

    return preprocess(comment_text)


def preprocess(rawText):

    cleanText = rawText.strip().replace("\n", " ")
    re.sub("(?:\@|http?\://|https?\://|www)\S+", "", cleanText)
    re.sub("[^\w\s]+", "", cleanText)
    cleanText = cleanText.lower()
    re.sub("\d+","", cleanText)
    re.sub("#\S+"," ", cleanText)
    # .replace(r"(?:\@|http?\://|https?\://|www)\S+", "",regex=True)
    # .replace(r"[^\w\s]+", "", regex=True).lower()
    # .replace(r"\d+", "", regex=True)
    # .replace(r"#\S+", " ", regex=True)
    
    stop_words = stopwords.words("english")
    # cleanText = cleanText.apply(
    #     lambda comment: " ".join(
    #         [word for word in comment.split() if word not in stop_words])
    # )
    words = cleanText.split()
    str_comment = ""
    for word in words:
        if word not in stop_words:
            str_comment += word +","

    text_object = NRCLex(str_comment)
    # print(text_object.raw_emotion_scores)
    
    data=text_object.raw_emotion_scores
    
    total = 0
    for emo in data:
        total += data.get(emo, 0)

    emotion_json=[]
    order_emotion=['anticipation', 'sadness','disgust', 'joy', 'fear','surprise',
                    'negative','positive', 'trust', 'anger']
    for emo in order_emotion:
        if(data.get(emo) == None):
            adj_score=0
        else:
            adj_score=data.get(emo)/total
        emotion_json.append(dict(
            axis=emo.title(),
            value=adj_score
        ))
    return emotion_json
