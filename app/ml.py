"""Very small TF‑IDF + cosine similarity recommender."""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from .models import Recipe
from . import db

class Recommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self.ids = []
        # Don't call _fit() during initialization
        # self._fit()

    def _fit(self):
        recipes = Recipe.query.all()
        docs = [r.ingredients for r in recipes]
        self.ids = [r.id for r in recipes]
        if docs:
            self.tfidf_matrix = self.vectorizer.fit_transform(docs)

    def recommend(self, query, topk=5):
        if self.tfidf_matrix is None:
            self._fit()  # Try to fit if not already done
        if self.tfidf_matrix is None:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = linear_kernel(q_vec, self.tfidf_matrix).flatten()
        top_idx = sims.argsort()[-topk:][::-1]
        return [Recipe.query.get(self.ids[i]) for i in top_idx if sims[i] > 0]

# Create the recommender instance but don't initialize data yet
recommender = Recommender()

def refresh():
    recommender._fit()