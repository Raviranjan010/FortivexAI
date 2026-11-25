from google import genai
from google.genai import errors
import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sklearn.metrics.pairwise import cosine_similarity

from .config import get_settings
from .models import ChunkEmbedding


def _embed(client, model, contents, task):
    result = client.models.embed_content(model=model, contents=contents, config={"task_type": task})
    vectors = [item.values for item in result.embeddings or []]
    if len(vectors) != len(contents) or any(not vector for vector in vectors):
        raise ValueError("Invalid embedding response")
    return vectors


def semantic_scores(db, chunks, query):
    settings = get_settings()
    model = settings.gemini_embedding_model
    if not model or not settings.gemini_api_key:
        return None
    vectors = {row.chunk_id: row.vector for row in db.scalars(select(ChunkEmbedding).where(
        ChunkEmbedding.model == model, ChunkEmbedding.chunk_id.in_([chunk.id for chunk in chunks])
    ))}
    try:
        client = genai.Client(api_key=settings.gemini_api_key, http_options={"timeout": 8000})
        missing = [chunk for chunk in chunks if chunk.id not in vectors]
        # Bound first-use work for a newly uploaded, large corpus.
        if len(missing) > 100:
            missing = missing[:100]
        if missing:
            new_vectors = _embed(client, model, [chunk.text for chunk in missing], "RETRIEVAL_DOCUMENT")
            try:
                with db.begin_nested():
                    for chunk, vector in zip(missing, new_vectors, strict=True):
                        db.add(ChunkEmbedding(chunk_id=chunk.id, model=model, vector=vector))
                        vectors[chunk.id] = vector
                db.commit()
            except IntegrityError:
                return None
        if len(vectors) != len(chunks):
            return None
        query_vector = _embed(client, model, [query], "RETRIEVAL_QUERY")
        return cosine_similarity(query_vector, [vectors[chunk.id] for chunk in chunks])[0]
    except (ValueError, errors.APIError, httpx.RequestError):
        return None
