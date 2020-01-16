import requests
from keys import youtubeKey # 'keys.py' file in same directory
import json
import csv

OUTPUT_FILE_NAME = 'videos.csv'

def write_videos_to_file(items):
    # Collect rows data
    rows_to_write = []
    for item in items:
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        upload_date = item['snippet']['publishedAt']
        rows_to_write.append([video_id, title, description, upload_date])

    # Write rows sequentially to output file
    with open(OUTPUT_FILE_NAME, mode='a', encoding='utf-8') as videos_file:
        writer = csv.writer(videos_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
        for row in rows_to_write:
            writer.writerow(row)

# Create videos CSV file and write header row
with open(OUTPUT_FILE_NAME, mode='w') as videos_file:
    writer = csv.writer(videos_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
    writer.writerow(['Video ID', 'Title', 'Description', 'Upload Date'])

r = requests.get('https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername=PowerfulJRE&key=' + youtubeKey())
print(r.text)
response = json.loads(r.text)
uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
print(uploads_playlist_id)

are_more_pages = True
next_page_token = None
while are_more_pages:
    list_videos_request_url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50' + \
                                '&playlistId=' + uploads_playlist_id + '&key=' + youtubeKey()
    if next_page_token is not None:
        list_videos_request_url += '&pageToken=' + next_page_token
    
    r = requests.get(list_videos_request_url)
    response = json.loads(r.text)
    write_videos_to_file(response['items'])
    if 'nextPageToken' in response:
        next_page_token = response['nextPageToken']
    else:
        are_more_pages = False