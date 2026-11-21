"""
vector_db_examples.py - the same tiny "store 3 policy snippets, search one question" job in
FAISS, Chroma, Qdrant, pgvector and Pinecone, so you can compare their APIs side by side.

Only FAISS is installed in the course environment. The other examples run only if their
library (and, for servers, a running service or API key) is available; otherwise they print
how to set them up. Install commands:
    pip install chromadb                     # Chroma (embedded, no server needed)
    pip install qdrant-client                # Qdrant (":memory:" mode needs no server)
    pip install "psycopg[binary]" pgvector   # pgvector (needs PostgreSQL with the vector extension)
    pip install pinecone                     # Pinecone (needs a PINECONE_API_KEY, paid cloud service)
APIs change between versions: check each project's docs (links in resources.md).

Run it:  python code/vector_db_examples.py
"""
import os

TEXTS = ["Tents have a 5-year warranty against manufacturing defects.",
         "Standard delivery takes 3 to 5 business days.",
         "Gift cards are valid for 3 years from purchase."]
IDS = ["warranty", "shipping", "giftcards"]
QUESTION = "What guarantee do tents come with?"


def embed(texts):
    """Same embedding model for every store, so results are comparable."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(texts, normalize_embeddings=True).astype("float32")


# ------------------------------------------------------------------ FAISS
def demo_faiss(vecs, qvec):
    import faiss
    index = faiss.IndexFlatIP(vecs.shape[1])          # exact search by dot product (= cosine for unit vectors)
    index.add(vecs)                                    # FAISS stores only vectors; we keep ids/texts in a Python list
    scores, idx = index.search(qvec, 2)
    print("FAISS   ->", [(IDS[i], round(float(s), 3)) for i, s in zip(idx[0], scores[0])])
    # For millions of vectors you would use an approximate index, e.g.:
    #   index = faiss.IndexHNSWFlat(384, 32)          # HNSW graph, 32 links per node
    # and save it with faiss.write_index(index, "policies.faiss")


# ------------------------------------------------------------------ Chroma
def demo_chroma(vecs, qvec):
    try:
        import chromadb
    except ImportError:
        print("Chroma  -> not installed (pip install chromadb). Skipped.")
        return
    client = chromadb.Client()                         # in-memory; chromadb.PersistentClient(path="db") saves to disk
    col = client.get_or_create_collection("policies", metadata={"hnsw:space": "cosine"})
    col.add(ids=IDS, documents=TEXTS, embeddings=vecs.tolist(),
            metadatas=[{"doc": i} for i in IDS])       # metadata lets you filter: where={"doc": "warranty"}
    res = col.query(query_embeddings=qvec.tolist(), n_results=2)
    print("Chroma  ->", list(zip(res["ids"][0], [round(1 - d, 3) for d in res["distances"][0]])))


# ------------------------------------------------------------------ Qdrant
def demo_qdrant(vecs, qvec):
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, PointStruct, VectorParams
    except ImportError:
        print("Qdrant  -> not installed (pip install qdrant-client). Skipped.")
        return
    client = QdrantClient(":memory:")                  # local mode; QdrantClient(url="http://localhost:6333") for a server
    client.create_collection("policies", vectors_config=VectorParams(size=vecs.shape[1], distance=Distance.COSINE))
    client.upsert("policies", points=[PointStruct(id=i, vector=v.tolist(), payload={"name": n, "text": t})
                                      for i, (v, n, t) in enumerate(zip(vecs, IDS, TEXTS))])
    hits = client.query_points("policies", query=qvec[0].tolist(), limit=2).points
    print("Qdrant  ->", [(h.payload["name"], round(h.score, 3)) for h in hits])


# ------------------------------------------------------------------ pgvector
def demo_pgvector(vecs, qvec):
    dsn = os.getenv("PG_DSN")                          # e.g. postgresql://user:pass@localhost:5432/rag  (never hard-code)
    if not dsn:
        print("pgvector-> set PG_DSN to a Postgres database with the 'vector' extension. Skipped.")
        print("          SQL it would run:\n"
              "          CREATE EXTENSION IF NOT EXISTS vector;\n"
              "          CREATE TABLE chunks (id text PRIMARY KEY, body text, embedding vector(384));\n"
              "          SELECT id, 1 - (embedding <=> %s) AS cosine FROM chunks ORDER BY embedding <=> %s LIMIT 2;")
        return
    import psycopg
    from pgvector.psycopg import register_vector
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)                          # teaches psycopg to send numpy arrays as vectors
        conn.execute("CREATE TABLE IF NOT EXISTS chunks (id text PRIMARY KEY, body text, embedding vector(384))")
        for i, t, v in zip(IDS, TEXTS, vecs):
            conn.execute("INSERT INTO chunks VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", (i, t, v))
        rows = conn.execute("SELECT id, 1 - (embedding <=> %s) FROM chunks ORDER BY embedding <=> %s LIMIT 2",
                            (qvec[0], qvec[0])).fetchall()   # <=> is pgvector's cosine-distance operator
        print("pgvector->", [(r[0], round(float(r[1]), 3)) for r in rows])


# ------------------------------------------------------------------ Pinecone
def demo_pinecone(vecs, qvec):
    if not os.getenv("PINECONE_API_KEY"):
        print("Pinecone-> set PINECONE_API_KEY (managed cloud service, may cost money). Skipped.")
        return
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone()                                    # reads PINECONE_API_KEY from the environment
    name = "course-policies"
    if name not in pc.list_indexes().names():
        pc.create_index(name, dimension=vecs.shape[1], metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"))   # check docs for current regions
    index = pc.Index(name)
    index.upsert(vectors=[(i, v.tolist(), {"text": t}) for i, v, t in zip(IDS, vecs, TEXTS)])
    res = index.query(vector=qvec[0].tolist(), top_k=2, include_metadata=True)
    print("Pinecone->", [(m.id, round(m.score, 3)) for m in res.matches])


if __name__ == "__main__":
    vectors = embed(TEXTS)
    query_vec = embed([QUESTION])
    print("Question:", QUESTION)
    for demo in (demo_faiss, demo_chroma, demo_qdrant, demo_pgvector, demo_pinecone):
        try:
            demo(vectors, query_vec)
        except Exception as err:                       # a broken optional backend must not stop the others
            print(f"{demo.__name__} failed: {type(err).__name__}: {err}")
