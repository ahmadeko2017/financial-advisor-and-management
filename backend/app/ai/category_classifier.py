"""
Baseline category classifier utilities (TF-IDF + Linear model).

Provides:
  - train(texts, labels, threshold) -> saves artifacts to ml_artifacts/
  - load_model() -> lazy load artifacts
  - predict(input) -> category_id | None with confidence/top_k
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]  # backend/
ARTIFACT_DIR = ROOT_DIR / "ml_artifacts"
MODEL_PATH = ARTIFACT_DIR / "category_model.pkl"
META_PATH = ARTIFACT_DIR / "category_meta.json"


def _threshold_default() -> float:
    try:
        return float(get_settings().model_config.get("CATEGORY_THRESHOLD", 0.5))  # type: ignore[attr-defined]
    except Exception:
        return float(getattr(get_settings(), "CATEGORY_THRESHOLD", 0.5))


@dataclass
class PredictionResult:
    category_id: Optional[str]
    confidence: float
    top_k: list[tuple[str, float]]
    model_version: str | None = None


class CategoryClassifier:
    def __init__(self, vectorizer, model, label_encoder: dict[str, int], model_version: str, threshold: float = 0.5):
        self.vectorizer = vectorizer
        self.model = model
        self.label_encoder = label_encoder  # mapping label -> index
        self.index_to_label = {v: k for k, v in label_encoder.items()}
        self.model_version = model_version
        self.threshold = threshold

    def predict(self, text: str, top_k: int = 3) -> PredictionResult:
        if not text:
            return PredictionResult(category_id=None, confidence=0.0, top_k=[], model_version=self.model_version)

        X = self.vectorizer.transform([text])
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[0]
        elif hasattr(self.model, "decision_function"):
            scores = self.model.decision_function(X)
            # Convert decision scores to pseudo-probabilities
            exp = np.exp(scores - np.max(scores))
            probs = exp / exp.sum()
        else:
            probs = np.zeros(len(self.index_to_label))

        best_idx = int(np.argmax(probs))
        confidence = float(probs[best_idx]) if probs.size else 0.0
        category_id = self.index_to_label.get(best_idx)

        sorted_indices = np.argsort(probs)[::-1]
        top = []
        for idx in sorted_indices[:top_k]:
            label = self.index_to_label.get(int(idx))
            if label is None:
                continue
            top.append((label, float(probs[int(idx)])))

        if confidence < self.threshold:
            return PredictionResult(category_id=None, confidence=confidence, top_k=top, model_version=self.model_version)

        return PredictionResult(category_id=category_id, confidence=confidence, top_k=top, model_version=self.model_version)


def _ensure_artifact_dir():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def load_model() -> Optional[CategoryClassifier]:
    """
    Lazy-load classifier from artifacts. Returns None if artifacts missing or load fails.
    """
    try:
        from joblib import load
    except ImportError:
        logger.warning("joblib not installed; cannot load classifier artifacts")
        return None

    if not MODEL_PATH.exists() or not META_PATH.exists():
        logger.info("Category model artifacts not found at %s", ARTIFACT_DIR)
        return None

    try:
        obj = load(MODEL_PATH)
        with META_PATH.open() as f:
            meta = json.load(f)
        threshold = float(meta.get("threshold", _threshold_default()))
        return CategoryClassifier(
            vectorizer=obj["vectorizer"],
            model=obj["model"],
            label_encoder=obj["label_encoder"],
            model_version=meta.get("model_version", "unknown"),
            threshold=threshold,
        )
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to load category classifier: %s", exc)
        return None


def train(
    texts: Iterable[str],
    labels: Iterable[str],
    threshold: float = 0.5,
    model_version: Optional[str] = None,
) -> None:
    """
    Train a baseline TF-IDF + Logistic Regression classifier and persist artifacts.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
    except ImportError as exc:
        raise RuntimeError("scikit-learn is required for training; install it first") from exc

    texts_list = list(texts)
    labels_list = list(labels)
    if not texts_list or not labels_list or len(texts_list) != len(labels_list):
        raise ValueError("texts and labels must be non-empty and of equal length")

    label_encoder: dict[str, int] = {}
    for lbl in labels_list:
        if lbl not in label_encoder:
            label_encoder[lbl] = len(label_encoder)
    y = np.array([label_encoder[lbl] for lbl in labels_list])

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_features=5000,
    )
    X = vectorizer.fit_transform(texts_list)

    clf = LogisticRegression(max_iter=1000, multi_class="auto", n_jobs=2)
    clf.fit(X, y)

    model_version = model_version or f"v{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    _ensure_artifact_dir()

    try:
        from joblib import dump
    except ImportError as exc:
        raise RuntimeError("joblib is required to persist classifier artifacts") from exc

    dump({"vectorizer": vectorizer, "model": clf, "label_encoder": label_encoder}, MODEL_PATH)
    with META_PATH.open("w") as f:
        json.dump(
            {
                "model_version": model_version,
                "created_at": datetime.utcnow().isoformat(),
                "threshold": threshold,
            },
            f,
        )
    logger.info("Saved category classifier artifacts to %s (version=%s)", ARTIFACT_DIR, model_version)


def predict_category(description: str, model: Optional[CategoryClassifier] = None) -> PredictionResult:
    """
    Convenience wrapper: load model (if not provided) and predict.
    Returns category_id=None if no model or below threshold.
    """
    if model is None:
        model = load_model()
    if model is None:
        return PredictionResult(category_id=None, confidence=0.0, top_k=[], model_version=None)
    return model.predict(description or "")
