##
#  Flatten Storyboard
#
#  USAGE
#  > python flatten_storyboard.py [episode_number] [episode_youtube_video_id]
#
#  eg:
#  # flatten storyboard images for JRE episode #400
#  > python flatten_storyboard.py 400 TjQcaK2Oa4w
#
##

from PIL import Image
import os
import re
import sys

# "Flattens" the download storyboard frames for the given episode number.
# Splits the tiled storyboard frame images into single-frame segments
# Assumes download_storyboard() has already been called for given episode number.
def flatten_storyboard(episode_number, episode_youtube_video_id):
    # Each frame in a story board is 160px x 90px
    FRAME_DIMS = (160, 90)

    video_directory_name = str(episode_number) + ' ' + episode_youtube_video_id
    sb_folder_path = os.path.join('storyboards', video_directory_name)

    num_storyboards = 0
    for file in os.listdir(sb_folder_path):
        if file.startswith('frame_'):
            print('This storyboard has already been flattened')
            sys.exit(1)

        match = re.findall(r'storyboard_([0-9]+)', os.fsdecode(file))
        num_storyboards = max(num_storyboards, int(match[0]) + 1)

    current_frame_index = 0
    for current_sb_index in range(num_storyboards):
        sb_img_path = os.path.join(sb_folder_path, 'storyboard_' + str(current_sb_index) + '.jpg')

        sb = Image.open(sb_img_path)
        sb_width, sb_height = sb.size

        cols = sb_width // FRAME_DIMS[0]
        rows = sb_height // FRAME_DIMS[1]

        for i in range(rows):
            for j in range(cols):
                frame_boundaries = (FRAME_DIMS[0] * j, FRAME_DIMS[1] * i, FRAME_DIMS[0] * (j + 1), FRAME_DIMS[1] * (i + 1))
                sb_crop = sb.crop(frame_boundaries)
                frame_save_name = 'frame_' + str(current_frame_index) + '.jpg'
                frame_save_path = os.path.join(sb_folder_path, frame_save_name)
                sb_crop.save(frame_save_path)
                current_frame_index += 1

if __name__ == '__main__':
    flatten_storyboard(int(sys.argv[1]), sys.argv[2])