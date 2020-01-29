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
from guest_name_extractor import get_guest_names

VIDEO_LIST_FILE_NAME = 'videos.csv'
VIDEO_LABELS_FILE_NAME = 'video_guest_labels.csv'

def is_jre_podcast_episode(csv_row):
    match = re.match(r'Joe Rogan Experience #(\d+) - (.*)', csv_row['Title'])
    return match is not None

labeled_video_ids = []
with open(VIDEO_LABELS_FILE_NAME, mode='r+') as labels_file:
    labels_reader = csv.DictReader(labels_file)
    labels_writer = csv.DictWriter(labels_file, fieldnames=['Video ID', 'Guest Names', 'Guest Vocation', 'Guest Gender', 'Guest Race'], \
                                    delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')

    known_label_rows = []

    # Read labels file to determine which videos have already been labeled
    for row in labels_reader:
        labeled_video_ids.append(row['Video ID'])
        known_label_rows.append(row)

    print(len(labeled_video_ids))

    # Associate known info that was labeled previously with each person
    known_people = {}
    for label_row in known_label_rows:
        people_names = label_row['Guest Names'].split('|')
        for person in people_names:
            known_people[person] = (label_row['Guest Vocation'], label_row['Guest Gender'], label_row['Guest Race'])

    with open(VIDEO_LIST_FILE_NAME, mode='r+', encoding='utf-8') as videos_file:
        videos_reader = csv.DictReader(videos_file)

        for row in videos_reader:
            if is_jre_podcast_episode(row) and row['Video ID'] not in labeled_video_ids:
                print(row['Title'])
                print(row['Description'] + '\n')

                print('Please input labels.  To quit, input \'q\'.')
                guest_names_set = get_guest_names(row['Title'])
                guest_names_str = '|'.join(guest_names_set)
                guest_names = input('Guest Name(s) [' + guest_names_str + ']: ') or guest_names_str
                first_guest_name = guest_names.split('|')[0]

                if(guest_names == 'q'): break

                # Determine default values for each label field
                vocation_default = 'comedian'
                gender_default = 'M'
                race_default = 'white'
                if first_guest_name in known_people:
                    known_person = known_people[first_guest_name]
                    vocation_default = known_person[0]
                    gender_default = known_person[1]
                    race_default = known_person[2]

                vocation = input('Guest Vocation [' + vocation_default + ']: ') or vocation_default
                gender = input('Guest Gender [' + gender_default + ']: ') or gender_default
                race = input('Guest Race [' + race_default + ']: ') or race_default

                new_row = {'Video ID': row['Video ID'], 'Guest Names': guest_names, 'Guest Vocation': vocation, 'Guest Gender': gender, 'Guest Race': race}
                labels_writer.writerow(new_row)
                labeled_video_ids.append(row['Video ID'])

                for person in guest_names.split('|'):
                    known_people[person] = (vocation, gender, race)
                print('\n\n\n\n')

    print('yar')