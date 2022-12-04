from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.discovery import build
import json
from .utils import *

def channel_stat(channels):
    channel_names = channels.GET.get('name','').split(",")
    channel_ids = []
    for cname in channel_names:
        channel_ids.append(get_channel_id(cname))

    channels = {}
    response = {}
    for cid in channel_ids:
        channels[cid] = get_channel_stats(cid)

    for cid in channel_ids:
        name = channels[cid]['title']
        uploadId = channels[cid]['uploadId']
        response[name] = get_all_videos(uploadId)

    grouped_response = {}
    grouped_response['stack'] = group_data(response)
    grouped_response['bubble'] = bubble_data(response)
    return HttpResponse(json.dumps(grouped_response), content_type='application/json')

def get_comments(channels):
    channel_names = channels.GET.get('name','').split(",")
    print(channel_names)
    channel_ids = []
    for cname in channel_names:
        channel_ids.append(get_channel_id(cname))
    response = []
    for cid in channel_ids:
        response.append(comment_sentiment(cid))
    response[0], response[2] = response[2], response[0]
    return HttpResponse(json.dumps(response), content_type='application/json')