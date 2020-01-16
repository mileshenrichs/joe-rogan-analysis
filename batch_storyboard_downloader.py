##
#  Batch Storyboard Downloader
#
#  USAGE
#  > python batch_storyboard_downloader.py [from_episode_number] [to_episode_number]
#
#  eg:
#  # download storyboards for episodes 800 through 900
#  > python batch_storyboard_downloader.py 800 900
#
##

from download_storyboard import download_storyboard
import csv
import sys
import re
import time

VIDEO_LIST_FILE_NAME = 'videos.csv'

from_index = int(sys.argv[1])
to_index = int(sys.argv[2])

# Returns True if the given episode is #[episode_number]
def is_episode_number(episode, episode_number):
    match = re.match(r'Joe Rogan Experience #(\d+) - (.*)', episode['Title'])
    if match is not None and int(match.group(1)) == episode_number:
        print(match.group(1))
        return True

    return False

# Fetches row of episode with given number from videos list CSV
def get_episode_details(reader, episode_number):
    videos_file.seek(0)
    next(reader)
    for row in reader:
        if is_episode_number(row, episode_number):
            return row

with open(VIDEO_LIST_FILE_NAME, mode='r', encoding='utf-8') as videos_file:
    reader = csv.DictReader(videos_file)

    for episode_number_to_download in range(from_index, to_index):
        episode = get_episode_details(reader, episode_number_to_download)
        if episode is not None:
            episode_youtube_video_id = episode['Video ID']
            download_storyboard(episode_youtube_video_id, episode_number_to_download)
            # Take a break between downloads
            time.sleep(10)

print('done')