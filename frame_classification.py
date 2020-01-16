from PIL import Image
import imagehash
import os
import re
from colorthief import ColorThief
from pathlib import Path
from shutil import copyfile

# def rgb_to_hex(rgb):
#     return '#%02x%02x%02x' % rgb

# from tkinter import Tk, Canvas

# VIDEO_ID = '438 aJeGeclGDpQ'
# sb_folder_path = os.path.join('storyboards', VIDEO_ID)

# color_thief = ColorThief(os.path.join(sb_folder_path, 'frame_691.jpg'))
# dominant_color = rgb_to_hex(color_thief.get_color(quality=6))

# root = Tk()
# root.geometry('160x90')
# canvas = Canvas(root)
# canvas.pack()
# a = canvas.create_rectangle(0, 0, 160, 90, fill=dominant_color)
# root.mainloop()





REFERENCE_IMAGE_MAP_JOE = {
    400: os.path.join('rogan_reference_images', 'joe_400to449.jpg')
}

REFERENCE_IMAGE_MAP_GUEST = {
    400: os.path.join('rogan_reference_images', 'guest_400to449.jpg')
}

SIMILARITY_THRESHOLD = {
    'Joe': 16,
    'Guest': 20
}

VIDEO_ID = '939 A0yd5vAf3Gk'
sb_folder_path = os.path.join('storyboards', VIDEO_ID)

rogan_reference_hash = imagehash.average_hash(Image.open(REFERENCE_IMAGE_MAP_JOE[400]),)
guest_reference_hash = imagehash.average_hash(Image.open(REFERENCE_IMAGE_MAP_GUEST[400]))

hash_joe = imagehash.average_hash(Image.open(os.path.join(sb_folder_path, 'frame_138.jpg'))) 
hash_not_joe = imagehash.average_hash(Image.open(os.path.join(sb_folder_path, 'frame_212.jpg')))
hash_screen = imagehash.average_hash(Image.open(os.path.join(sb_folder_path, 'frame_734.jpg')))

# rogan_reference_hash = imagehash.phash(Image.open(REFERENCE_IMAGE_MAP_JOE[400]))
# guest_reference_hash = imagehash.phash(Image.open(REFERENCE_IMAGE_MAP_GUEST[400]))

# hash_joe = imagehash.phash(Image.open(os.path.join(sb_folder_path, 'frame_138.jpg'))) 
# hash_not_joe = imagehash.phash(Image.open(os.path.join(sb_folder_path, 'frame_212.jpg')))
# hash_screen = imagehash.phash(Image.open(os.path.join(sb_folder_path, 'frame_734.jpg')))

print('joe hash: ' + str(hash_joe))
print('not joe hash: ' + str(hash_not_joe))
print('joe hash diff ' + str(hash_joe - rogan_reference_hash))
print('not joe hash diff ' + str(hash_not_joe - rogan_reference_hash))
print('joe to guest hash diff: ' + str(hash_joe - guest_reference_hash))
print('guest to guest hash diff: ' + str(hash_not_joe - guest_reference_hash))
print('joe to screen hash diff: ' + str(hash_joe - hash_screen))
print('guest to screen hash diff: ' + str(hash_not_joe - hash_screen))

image_pools = {
    'JOE_ROGAN': [],
    'GUEST': [],
    'OTHER': []
}

def summarize_runs(frames_list):
    i = 0
    while(i < len(frames_list) - 1):
        j = i + 1
        while(j < len(frames_list) and frames_list[j] == frames_list[j - 1] + 1):
            j += 1

        if i != j - 1:
            print(str(frames_list[i]) + ' to ' + str(frames_list[j - 1]))
        else:
            print(str(frames_list[i]))
        i = j

# Groups similar images together.  Most images should fall into either the 'JOE_ROGAN' or 'GUEST' pool.
# Any images that do
def cluster_images(sb_folder_path):
    # This data structure stores each cluster as a member of a list.
    # Each cluster is a tuple in the form (cluster_head_hash, [cluster_frames]), the hash value of 
    # the cluster's head frame and the list of frame indexes that are part of this cluster.
    clustered_images = []

    # For each frame, evaluate its similarity to the "head" image for each
    # existing image cluster.  If it is similar, add it to the cluster.
    # If it is not sufficiently similar to any existing clusters, make it the head of a new cluster.
    for image_name in os.listdir(sb_folder_path):
        if image_name.startswith('frame_'):
            match = re.match(r'frame_(\d+).jpg', image_name)
            frame_number = int(match.group(1))
            frame_image = Image.open(os.path.join(sb_folder_path, image_name))
            frame_image_hash = imagehash.average_hash(frame_image)

            added_to_existing_cluster = False
            for cluster in clustered_images:
                if frame_image_hash - cluster[0] <= 16: # belongs in cluster
                    cluster[1].append(frame_number)
                    added_to_existing_cluster = True
                    break
            if not added_to_existing_cluster:
                clustered_images.append((frame_image_hash, [frame_number]))

    clustered_images.sort(key=lambda c:len(c[1]), reverse=True)
    return clustered_images

def write_clusters_to_disk(sb_folder_path, clustered_images):
    clusters_dir = os.path.join(sb_folder_path, 'clusters')
    Path(clusters_dir).mkdir(parents=True, exist_ok=True)

    i = 1
    for cluster in clustered_images:
        cluster_dir = os.path.join(clusters_dir, 'cluster_' + str(i) + ' (' + str(len(cluster[1])) + ')')
        Path(cluster_dir).mkdir(parents=True, exist_ok=True)

        for frame_number in cluster[1]:
            original_frame_path = os.path.join(sb_folder_path, 'frame_' + str(frame_number) + '.jpg')
            copied_frame_path = os.path.join(cluster_dir, 'frame_' + str(frame_number) + '.jpg')
            copyfile(original_frame_path, copied_frame_path)

        i += 1

print('\n')
clustered_images = cluster_images(sb_folder_path)
print(str(len(clustered_images)) + ' clusters\n')
for cluster in clustered_images:
    print(len(cluster[1]))

write_clusters_to_disk(sb_folder_path, clustered_images)

# for image_name in os.listdir(sb_folder_path):
#     if image_name.startswith('frame_'):
#         match = re.match(r'frame_(\d+).jpg', image_name)
#         frame_number = int(match.group(1))
#         frame_image = Image.open(os.path.join(sb_folder_path, image_name))
        
#         frame_image_hash = imagehash.average_hash(frame_image)
#         rogan_similarity = frame_image_hash - rogan_reference_hash
#         guest_similarity = frame_image_hash - guest_reference_hash

#         if rogan_similarity < SIMILARITY_THRESHOLD['Joe']:
#             image_pools['JOE_ROGAN'].append(frame_number)
#         elif guest_similarity < SIMILARITY_THRESHOLD['Guest']:
#             image_pools['GUEST'].append(frame_number)
#         else:
#             image_pools['OTHER'].append(frame_number)

# print(len(image_pools['JOE_ROGAN']))
# image_pools['JOE_ROGAN'].sort()
# # print(image_pools['JOE_ROGAN'])

# # summarize_runs(image_pools['JOE_ROGAN'])

# print('\n')
# print('Joe frames: ' + str(len(image_pools['JOE_ROGAN'])))
# print('Guest frames: ' + str(len(image_pools['GUEST'])))
# print('Other frames: ' + str(len(image_pools['OTHER'])))





# import face_recognition
# from PIL import Image
# import os

# VIDEO_ID = '801 KQIuHGbKckY'
# sb_folder_path = os.path.join('storyboards', VIDEO_ID)
# frame_path = os.path.join(sb_folder_path, 'frame_575.jpg')
# print(frame_path)

# image = face_recognition.load_image_file(frame_path)
# face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2, model='cnn')
# print(face_locations)

# for face_location in face_locations:

#     # Print the location of each face in this image
#     top, right, bottom, left = face_location
#     print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

#     # You can access the actual face itself like this:
#     face_image = image[top:bottom, left:right]
#     pil_image = Image.fromarray(face_image)
#     pil_image.show()