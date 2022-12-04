from django.shortcuts import render
from django.http import HttpResponse

from googleapiclient.discovery import build
import json
import pandas as pd
import numpy as np
import pycountry

from .utils import *
from . import static_data as sd


pd.options.mode.chained_assignment = None


def popular_videos(r):
    region = r.GET.get('region', '').split(",")

    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    youtube = build('youtube', 'v3', developerKey=api_key)

    popular_videos = []
    for code in region:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=code,
            maxResults=50
        )
        response = request.execute()

        for video in response['items']:
            data = dict(region=code, channel=video['snippet']['channelTitle'],
                        date=video['snippet']['publishedAt'],
                        views=int(video['statistics']['viewCount']),
                        category=sd.category_list[video['snippet']
                            ['categoryId']]
                        )
            popular_videos.append(data)

    df = pd.DataFrame(popular_videos)

    popular_json = []
    for r in region:
        new_df = df[df['region'] == r]
        cat_df = new_df.groupby('category', as_index=False)['views'].sum()
        cat_list = cat_df.sort_values(
            'views', ascending=False).head(5).category.to_list()
        child = []
        for c in cat_list:
            channel_df = new_df[new_df['category'] == c].groupby(
                'channel', as_index=False)['views'].sum().head(5)
            grand_child = []
            for index, row in channel_df.iterrows():
                grand_child.append(
                    dict(name=row['channel'], value=row['views']))
            cat_data = dict(name=c, children=grand_child)
            child.append(cat_data)
        data = dict(name=pycountry.countries.get(alpha_2=r).name,
                    children=child
                    )
        popular_json.append(data)
    response_json = { 'name': 'Popular', 'children': popular_json}
    return HttpResponse(json.dumps(response_json), content_type='application/json')


def bubbles(r):
    region = r.GET.get('region', '').split(",")

    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    youtube = build('youtube', 'v3', developerKey=api_key)

    popular_videos = []
    for code in region:
        request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=code,
                maxResults=50
        )
        response = request.execute()

        for video in response['items']:
            data = dict(region=code,
                        date=video['snippet']['publishedAt'],
                    views=int(video['statistics']['viewCount']),
                    like=int(video['statistics'].get('likeCount', 0)),
                    comment=int(video['statistics'].get('commentCount', 0)),
                    category=sd.category_list[video['snippet']['categoryId']])
            popular_videos.append(data)

    df = pd.DataFrame(popular_videos)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.day_name()
    df['ratio'] = df['like']/df['views'] * 100

    bubble_resp = {}
    bubble_resp['Popular-bubble'] = get_bubble(df)
    for r in region:
        new_df = df[df['region'] == r]
        country = pycountry.countries.get(alpha_2=r).name
        bubble_resp['Popular-'+country+'-bubble'] = get_bubble(new_df)
        cat_df = new_df.groupby('category', as_index=False)['views'].sum()
        cat_list = cat_df.sort_values(
            'views', ascending=False).head(5).category.to_list()
        for c in cat_list:
            q_df = new_df[new_df['category'] == c]
            bubble_resp["Popular-"+country+"-"+c+"-bubble"] = get_bubble(q_df)
    return HttpResponse(json.dumps(bubble_resp), content_type="application/json")


def emotions(r):
    region = r.GET.get('region', '').split(",")

    api_key = 'AIzaSyDWCn3WD8BUE1Z6JSI9cyf7j7QlDa9NoCk'
    # api_key = 'AIzaSyAQoWWjjn4RWtSJCyqsUq1dq134YZWzUgU'
    youtube = build('youtube', 'v3', developerKey=api_key)

    popular_videos = []
    for code in region:
        request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=code,
                maxResults=50
        )
        response = request.execute()

        for video in response['items']:
            data = dict(region = code,
                    title = video['snippet']['title'],
                    description = video['snippet']['description'],
                   category = sd.category_list[video['snippet']['categoryId']],
                   views = int(video['statistics']['viewCount']))
            popular_videos.append(data)

    df = pd.DataFrame(popular_videos)
    emotion_resp = {}
    text_object = preprocess(df)
    emotion_resp['Popular-emotion'] = get_emotions(text_object)
    emotion_resp['Popular-words'] = get_words(text_object)

    for r in region:
        new_df = df[df['region'] == r]
        country = pycountry.countries.get(alpha_2=r).name
        text_object = preprocess(new_df)
        emotion_resp['Popular-'+country+'-emotion'] = get_emotions(text_object)
        emotion_resp['Popular-'+country+'-words'] = get_words(text_object)
        cat_df = new_df.groupby('category', as_index=False)['views'].sum()
        cat_list = cat_df.sort_values(
            'views', ascending=False).head(5).category.to_list()
        for c in cat_list:
            q_df = new_df[new_df['category'] == c]
            text_object = preprocess(q_df)
            emotion_resp["Popular-"+country+"-"+c+"-emotion"] = get_emotions(text_object)
            emotion_resp["Popular-"+country+"-"+c+"-words"] = get_words(text_object)

    return HttpResponse(json.dumps(emotion_resp), content_type="application/json")


#Channels
