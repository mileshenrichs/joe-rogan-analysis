##
#  Guest Name Extractor
#
#  Provides a method to extract named entities from the title of a JRE episode video.
#  Used to determine which guest(s) appear in a podcast episode.
#
#  This depends on the NLTK library, whose data needs to be installed before attempting to use:
#  > import nltk
#  > nltk.download('popular')
#
#  Credit to Richard Weiss for the extraction code:
#  https://gist.github.com/onyxfish/322906#gistcomment-1485426
#
##
import nltk

def get_guest_names(video_title):
    sentences = nltk.sent_tokenize(video_title)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    def extract_entity_names(t):
        entity_names = []

        if hasattr(t, 'label') and t.label:
            if t.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in t]))
            else:
                for child in t:
                    entity_names.extend(extract_entity_names(child))

        return entity_names

    entity_names = []
    for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))

    entity_names.remove('Joe Rogan Experience')

    # Return unique names
    return set(entity_names)