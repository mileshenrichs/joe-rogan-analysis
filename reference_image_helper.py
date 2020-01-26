##
# Reference Image Helper
#
# In order to classify each frame as either being Joe talking, a guest talking, or something else,
# an image similarity algorithm is used.  This requires a reference image to match against for both Joe and the guest(s).
# The JRE recording studio background has changed over time, so a different reference image is required for each
# unique time period.  This helper is responsible for knowing which reference images should be used for any given episode number
# and returning a (Joe, guest) image path tuple from the get_reference_images(episode_number) function.
##
import os

RANGE_REFERENCES = {
    400: {
        'Joe': os.path.join('rogan_reference_images', '400to420_joe.jpg'),
        'Guest': os.path.join('rogan_reference_images', '400to420_guest.jpg'),
        'Similarity Threshold': 16
    },
    421: {
        'Joe': os.path.join('rogan_reference_images', '421to449_joe.jpg'),
        'Guest': os.path.join('rogan_reference_images', '421to449_guest.jpg'),
        'Similarity Threshold': 18
    },
    450: {
        'Joe': os.path.join('rogan_reference_images', '450to1290_joe.jpg'),
        'Guest': os.path.join('rogan_reference_images', '450to1290_guest.jpg'),
        'Similarity Threshold': 18
    }
}

def get_range_reference(episode_number):
    if episode_number >= 400 and episode_number <= 420:
        return RANGE_REFERENCES[400]
    elif episode_number >= 421 and episode_number <= 449:
        return RANGE_REFERENCES[421]
    elif episode_number >= 450 and episode_number <= 1290:
        return RANGE_REFERENCES[450]

def get_reference_images(episode_number):
    range_reference = get_range_reference(episode_number)
    if range_reference is not None:
        return (range_reference['Joe'], range_reference['Guest'])
    else:
        raise ValueError('episode_number passed to get_cluster_similarity_thresholds() was invalid', episode_number)

def get_cluster_similarity_threshold(episode_number):
    range_reference = get_range_reference(episode_number)
    if range_reference is not None:
        return range_reference['Similarity Threshold']
    else:
        raise ValueError('episode_number passed to get_cluster_similarity_threshold() was invalid', episode_number)