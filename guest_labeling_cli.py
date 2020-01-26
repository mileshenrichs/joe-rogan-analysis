##
#  Guest Labeling Command Line Interface
#
#  I have to manually guest-specific information for each episode.  This CLI provides me an easy workflow to
#  examine each episode description and add my labels to the videos.csv file.
#
#  USAGE
#  > python guest_labeling_cli.py
#  
##

import csv
import re

VIDEO_LIST_FILE_NAME = 'videos.csv'
VIDEO_LABELS_FILE_NAME = 'video_guest_labels.csv'

def is_jre_podcast_episode(csv_row):
    match = re.match(r'Joe Rogan Experience #(\d+) - (.*)', csv_row['Title'])
    return match is not None

labeled_video_ids = []
with open(VIDEO_LABELS_FILE_NAME, mode='r+') as labels_file:
    labels_reader = csv.DictReader(labels_file)
    labels_writer = csv.DictWriter(labels_file, fieldnames=['Video ID', 'Guest Vocation', 'Guest Gender', 'Guest Race'], \
                                    delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')

    # Read labels file to determine which videos have already been labeled
    for row in labels_reader:
        labeled_video_ids.append(row['Video ID'])

    print(len(labeled_video_ids))



    with open(VIDEO_LIST_FILE_NAME, mode='r+', encoding='utf-8') as videos_file:
        videos_reader = csv.DictReader(videos_file)

        for row in videos_reader:
            if is_jre_podcast_episode(row) and row['Video ID'] not in labeled_video_ids:
                print(row['Title'])
                print(row['Description'] + '\n')

                print('Please input labels.  To quit, input \'q\'.')
                vocation = input('Guest Vocation: ') or 'comedian'
                if(vocation == 'q'): break
                gender = input('Guest Gender: ') or 'M'
                race = input('Guest Race: ') or 'white'

                new_row = {'Video ID': row['Video ID'], 'Guest Vocation': vocation, 'Guest Gender': gender, 'Guest Race': race}
                labels_writer.writerow(new_row)
                labeled_video_ids.append(row['Video ID'])

    print('yar')