from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = None


def get_model():
    global model

    if model is None:
        print("Loading AI model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded!")

    return model


def get_embedding(skill_text):
    model = get_model()
    return model.encode(skill_text)


def calculate_similarity(skill1, skill2):
    embedding1 = get_embedding(skill1)
    embedding2 = get_embedding(skill2)

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )

    return float(similarity[0][0])