# import Levenshtein
from sentence_transformers import SentenceTransformer
import re
from collections import Counter
import math
from scipy.spatial import distance

# model = SentenceTransformer('all-mpnet-base-v2')

def get_embedding(sentence, model, type='sbert'):
    # model = SentenceTransformer('all-mpnet-base-v2') if type == 'sbert' else SentenceTransformer('bert-base-nli-mean-tokens')
    embedding = model.encode([sentence])[0]  # Get the 1D embedding vector
    return embedding

def calculate_embedding_similarity(embedding1, embedding2):
    similarity = 1 - distance.cosine(embedding1, embedding2)
    return similarity
    
    
def calculate_sentence_similarity(sentence1, sentence2, type='sbert'):
    model = SentenceTransformer("all-mpnet-base-v2") if type == 'sbert' else SentenceTransformer('bert-base-nli-mean-tokens')
    
    embedding1 = model.encode([sentence1])[0]  # Get the 1D embedding vector
    embedding2 = model.encode([sentence2])[0]  # Get the 1D embedding vector

    return calculate_embedding_similarity(embedding1, embedding2)


def preprocess_text(text):
    text = text.lower()
    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    return text


def calculate_cosine_similarity(text1, text2):
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)

    # Create token vectors
    vector1 = Counter(text1.split())
    vector2 = Counter(text2.split())

    # Compute dot product
    dot_product = sum(vector1[key] * vector2[key] for key in vector1 if key in vector2)

    # Compute magnitude of vectors
    magnitude1 = math.sqrt(sum(vector1[key] ** 2 for key in vector1))
    magnitude2 = math.sqrt(sum(vector2[key] ** 2 for key in vector2))

    # Handle division by zero error
    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    # Compute cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    return similarity


def calculate_jaccard_similarity(text1, text2):
    text1 = set(preprocess_text(text1).split())
    text2 = set(preprocess_text(text2).split())

    # Compute Jaccard similarity
    intersection = len(text1.intersection(text2))
    union = len(text1) + len(text2) - intersection

    # Handle division by zero error
    if union == 0:
        return 0

    similarity = intersection / union
    return similarity


if __name__ == "__main__":
    # Example usage
    string1 = """ > [builder 2/3] RUN apt update && apt install -y --no-install-recommends         ca-certificates         exuberant-ctags         gcc         git         libncurses5-dev         make         python         python-dev         wget     && rm -rf /var/lib/apt/lists/*:
  404  Not Found
Err:4 http://deb.debian.org/debian stretch-updates Release
  404  Not Found
Ign:5 http://security.debian.org/debian-security stretch/updates InRelease
Err:6 http://security.debian.org/debian-security stretch/updates Release
  404  Not Found [IP: 151.101.2.132 80]
Reading package lists...
E: The repository 'http://deb.debian.org/debian stretch Release' does not have a Release file.
E: The repository 'http://deb.debian.org/debian stretch-updates Release' does not have a Release file.
E: The repository 'http://security.debian.org/debian-security stretch/updates Release' does not have a Release file.
"""

    string2 = """ > [builder 2/3] RUN apt update && apt install -y --no-install-recommends         ca-certificates         exuberant-ctags         gcc         git         libncurses5-dev         make         python         python-dev         wget     && rm -rf /var/lib/apt/lists/*:
Err:4 http://security.debian.org/debian-security stretch/updates Release
  404  Not Found [IP: 151.101.130.132 80]
Err:5 http://deb.debian.org/debian stretch Release
  404  Not Found
Err:6 http://deb.debian.org/debian stretch-updates Release
  404  Not Found
Reading package lists...
E: The repository 'http://security.debian.org/debian-security stretch/updates Release' does not have a Release file.
E: The repository 'http://deb.debian.org/debian stretch Release' does not have a Release file.
E: The repository 'http://deb.debian.org/debian stretch-updates Release' does not have a Release file.
"""


    # Calculate similarity
    cosine_similarity = calculate_cosine_similarity(string1, string2)
    jaccard_similarity = calculate_jaccard_similarity(string1, string2)
    similarity_bert_base = calculate_sentence_similarity(string1, string2, type='bert-base')
    similarity_sbert = calculate_sentence_similarity(string1, string2, type='sbert')

    print("Cosine Similarity:", cosine_similarity)
    print("Jaccard Similarity:", jaccard_similarity)
    print("Sentence Similarity (bert base):", similarity_bert_base)
    print("Sentence Similarity (sbert):", similarity_sbert)
