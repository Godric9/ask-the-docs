import re

from pathlib import Path
from fastembed import TextEmbedding


def fix_size_chunker(text: str, size : int, overlap : int = 0) -> list[str]:
    """Splitting text by fixed size.
    """

    assert(size > overlap)

    chunks = []

    pas = size - overlap
    for i in range(0, len(text), pas):
        chunks.append(text[i:i+size])

    return chunks

def combine_sentences(sentences, buffer_size=1):
    # Go through each sentence dict
    for i in range(len(sentences)):

        # Create a string that will hold the sentences which are joined
        combined_sentence = ''

        # Add sentences before the current one, based on the buffer size.
        for j in range(i - buffer_size, i):
            # Check if the index j is not negative (to avoid index out of range like on the first one)
            if j >= 0:
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += sentences[j]['sentence'] + ' '

        # Add the current sentence
        combined_sentence += sentences[i]['sentence']

        # Add sentences after the current one, based on the buffer size
        for j in range(i + 1, i + 1 + buffer_size):
            # Check if the index j is within the range of the sentences list
            if j < len(sentences):
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += ' ' + sentences[j]['sentence']

        # Then add the whole thing to your dict
        # Store the combined sentence in the current sentence dict
        sentences[i]['combined_sentence'] = combined_sentence

    return sentences


def semantic_chunker(text : str) -> list[str]:
    single_sentences_list = re.split(r'(?<=[.?!])\s+', text)
    sentences = [{'sentence': x, 'index' : i} for i, x in enumerate(single_sentences_list)]

    sentences = combine_sentences(sentences=sentences)


SEPARATORS = ["\n\n", "\n", ".", "?", "!", " ", ""]

def recursif_token_chunker(text: str, chunk_size: int, separators: list[str]= SEPARATORS) -> list[str]:
    """Splitting text by recursively look at characters.
    
    Recursively tries to split by different characters to find one
    that works.
    """

    if len(text) <= chunk_size or not separators:
        return [text]

    sep, smaller_separator = separators[0], separators[1:]

    if sep:
        splits = text.split(sep=sep)
    else:
        splits = [text]

    chunks = []
    current_chunks = ""

    for i, split in enumerate(splits):
        segment = current_chunks + (sep if current_chunks else "") + split


        if len(segment) <= chunk_size:
            current_chunks = segment
        else:
            if current_chunks:
                chunks.extend(recursif_token_chunker(text=current_chunks,separators=smaller_separator, chunk_size=chunk_size))
            current_chunks = split

    if current_chunks:
        chunks.extend(recursif_token_chunker(text=current_chunks,separators=smaller_separator, chunk_size=chunk_size))
    return chunks