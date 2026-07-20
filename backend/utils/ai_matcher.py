from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading AI model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully")
def get_embedding(skill_text):
    """
    Converts a string of skills into an AI embedding.
    """

    embedding = model.encode(skill_text)

    return embedding
def calculate_similarity(skill1, skill2):
    """
    Calculates similarity between two skill sets.
    """

    embedding1 = get_embedding(skill1)
    embedding2 = get_embedding(skill2)

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )

    return float(similarity[0][0])