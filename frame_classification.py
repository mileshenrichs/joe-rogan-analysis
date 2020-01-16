from PIL import Image
import imagehash
import os
import sys
import re
from pathlib import Path
from shutil import copyfile
from reference_image_helper import get_reference_images, get_cluster_similarity_threshold
import numpy as np

def do_frame_classification(video_id):
    sb_folder_path = os.path.join('storyboards', video_id)

    episode_number = int(video_id[:video_id.index(' ')])

    image_pools = {
        'JOE_ROGAN': [],
        'GUEST': [],
        'OTHER': []
    }

    # The similarity clustering algorithm works decently well, but often splits what should be one big cluster
    # into one pretty big cluster and another smaller cluster.  We can merge these clusters by evaluating
    # the differences in cluster average hashes across all images in the cluster and merging the clusters
    # that have sufficiently similar average hashes.
    def merge_clusters(clusters):
        # Minimum size (number of frames) for a cluster to be considered for merge
        CLUSTER_SIGNIFICANCE_MIN_SIZE = 4

        # Maximum Euclidean distance between two cluster average hashes for them to be merged
        CLUSTER_DISTANCE_THRESHOLD = 2.0

        # Accumulate array of ndarrays representing the average of each cluster's hashes
        # (a hash is represented as an ndarray of binary values)
        cluster_averages = []
        for cluster in clusters:
            if len(cluster[1]) >= CLUSTER_SIGNIFICANCE_MIN_SIZE:
                avg_hash_array = cluster[1][0][1].hash.flatten()

                # Accumulate hash arrays into a matrix
                for i in range(1, len(cluster[1])):
                    avg_hash_array = np.vstack([avg_hash_array, cluster[1][i][1].hash.flatten()])

                # Compute average of all frame hashes in the cluster
                mean_array = avg_hash_array.mean(axis=0)
                cluster_averages.append(mean_array)

        print('\nComparing average of first cluster to averages of all other clusters:')
        for i, cluster in enumerate(cluster_averages):
            euclidian_distance = np.linalg.norm(cluster - cluster_averages[0])
            print(str(i+1) + ': ' + str(euclidian_distance))

        print('\nComparing average of second cluster to averages of all other clusters:')
        for i, cluster in enumerate(cluster_averages):
            euclidian_distance = np.linalg.norm(cluster - cluster_averages[1])
            print(str(i+1) + ': ' + str(euclidian_distance))

    # Groups similar images together.  Most images should fall into either the 'JOE_ROGAN' or 'GUEST' pool.
    # Any images that do
    def cluster_images(sb_folder_path):
        # This data structure stores each cluster as a member of a list.
        # Each cluster is a tuple in the form (cluster_head_hash, [(frame_number, frame_hash)]), the hash value of 
        # the cluster's head frame and the list of frame numbers and their hashes that are part of this cluster.
        clustered_images = []

        similarity_threshold = get_cluster_similarity_threshold(episode_number)
        print('similarity_threshold: ' + str(similarity_threshold))

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
                    if frame_image_hash - cluster[0] <= similarity_threshold: # belongs in cluster
                        cluster[1].append((frame_number, frame_image_hash))
                        added_to_existing_cluster = True
                        break
                if not added_to_existing_cluster:
                    clustered_images.append((frame_image_hash, [(frame_number, frame_image_hash)]))

        clustered_images.sort(key=lambda c:len(c[1]), reverse=True)
        merge_clusters(clustered_images)
        return clustered_images

    def write_clusters_to_disk(sb_folder_path, clustered_images):
        clusters_dir = os.path.join(sb_folder_path, 'clusters')
        Path(clusters_dir).mkdir(parents=True, exist_ok=True)

        i = 1
        for cluster in clustered_images:
            cluster_dir = os.path.join(clusters_dir, 'cluster_' + str(i) + ' (' + str(len(cluster[1])) + ')')
            Path(cluster_dir).mkdir(parents=True, exist_ok=True)

            for frame in cluster[1]:
                frame_number = frame[0]
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


if __name__ == '__main__':
    do_frame_classification(sys.argv[1] + ' ' + sys.argv[2])