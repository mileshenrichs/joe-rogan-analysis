import requests
import re
import os
import sys
import json
import math
from pathlib import Path

def download_storyboard(video_id, episode_number):
    r = requests.get('https://www.youtube.com/watch?v=' + video_id)
    video_html = r.text

    match = re.findall(r'playerStoryboardSpecRenderer.*?(\{.+?\})', video_html)
    if not match:
        print('No storyboard available :(')
        sys.exit(1)

    spec_json = match[0].replace(r'\\', '').replace('\\', '')
    spec = json.loads(spec_json)
    spec_url = spec['spec']
    print(spec_url)

    match = re.findall(r'(http.*?)\|.*?#M\$M#(.*?)\|(\d+)#(\d+)#(\d+)#(\d+)#(\d+)#\d+#M\$M#([^|]*).*?$', spec_url)
    print(match)

    http = match[0][0].replace('$L', '2')
    frameCount = int(match[0][4])
    frameRowLength = int(match[0][5])
    frameRowCount = int(match[0][6])
    sigh = match[0][7]
    http += '&sigh=' + sigh

    # Create directory for video storyboard images
    storyboard_directory = os.path.join('storyboards', str(episode_number) + ' ' + video_id)
    Path(storyboard_directory).mkdir(parents=True, exist_ok=True)

    # Download storyboard images and put them in directory
    num_storyboards = math.ceil(frameCount / frameRowLength / frameRowCount)
    for i in range(num_storyboards):
        storyboard_src = http.replace('$N', 'M' + str(i))
        print(storyboard_src)
        storyboard_img = requests.get(storyboard_src)
        with open(storyboard_directory + '/storyboard_' + str(i) + '.jpg', 'wb') as output:
            output.write(storyboard_img.content)


if __name__ == '__main__':
    download_storyboard(sys.argv[2], int(sys.argv[1]))