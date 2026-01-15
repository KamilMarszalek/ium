import argparse
import re
from pathlib import Path

import hdbscan
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

HTML_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def _clean_text(s: pd.Series) -> pd.Series:
    s = s.astype("string").fillna("")
    s = s.str.replace(HTML_RE, " ", regex=True)
    s = s.str.replace(WS_RE, " ", regex=True).str.strip().str.lower()
    return s


def build_text(listings: pd.DataFrame) -> pd.Series:
    text_cols = [
        # "name",
        # "description",
        # "neighborhood_overview",
        # "host_about",
        # "bathrooms_text",
        "amenities",
        # "property_type",
        # "room_type",
    ]

    parts: list[pd.Series] = []
    for c in text_cols:
        if c in listings.columns:
            parts.append(_clean_text(listings[c]))

    if not parts:
        return pd.Series(
            [""] * len(listings),
            index=listings.index,
            dtype="string",
        )

    txt = parts[0]
    for p in parts[1:]:
        txt = txt + " | " + p

    txt = txt.where(txt.str.len() >= 10, other="")
    return txt


def create_embeddings(
    texts: pd.Series,
    *,
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 64,
    normalize: bool = True,
) -> np.ndarray:
    model = SentenceTransformer(model_name)

    all_embs: list[np.ndarray] = []
    for start in range(0, len(texts), batch_size):
        batch = texts.iloc[start : start + batch_size].tolist()
        embs = model.encode(
            batch,
            show_progress_bar=(start == 0),
            normalize_embeddings=normalize,
        )
        all_embs.append(np.asarray(embs, dtype=np.float32))

    return np.vstack(all_embs)


def maybe_reduce_dim(
    X: np.ndarray,
    *,
    pca_dim: int | None,
    random_state: int = 42,
) -> np.ndarray:
    if pca_dim is None or pca_dim <= 0 or pca_dim >= X.shape[1]:
        return X
    pca = PCA(n_components=pca_dim, random_state=random_state)
    return pca.fit_transform(X).astype(np.float32)


def choose_k_auto(
    X: np.ndarray,
    *,
    k_min: int = 2,
    k_max: int = 20,
    sample_size: int = 20000,
    random_state: int = 42,
) -> int:
    rng = np.random.default_rng(random_state)
    if len(X) > sample_size:
        idx = rng.choice(len(X), size=sample_size, replace=False)
        Xs = X[idx]
    else:
        Xs = X

    best_k = k_min
    best_score = -1.0

    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
        labels = km.fit_predict(Xs)
        if len(np.unique(labels)) < 2:
            continue
        score = silhouette_score(Xs, labels)
        if score > best_score:
            best_score = score
            best_k = k

    print(f"[auto-k] best_k={best_k} silhouette={best_score:.4f}")
    return best_k


def cluster_embeddings(
    X: np.ndarray,
    *,
    method: str,
    k: int | str = 8,
    random_state: int = 42,
    hdbscan_min_cluster_size: int = 50,
    hdbscan_min_samples: int | None = None,
) -> np.ndarray:
    method = method.lower().strip()

    if method == "hdbscan":
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=hdbscan_min_cluster_size,
            min_samples=hdbscan_min_samples,
            metric="euclidean",
        )
        labels = clusterer.fit_predict(X)
        return labels.astype(int)

    if method == "kmeans":
        kk: int
        if isinstance(k, str) and k == "auto":
            kk = choose_k_auto(X, random_state=random_state)
        else:
            kk = int(k)

        km = KMeans(n_clusters=kk, n_init="auto", random_state=random_state)
        labels = km.fit_predict(X)
        return labels.astype(int)

    raise ValueError("method must be one of: 'kmeans', 'hdbscan'")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listings", type=Path, default=Path("data/listings.csv"))
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("data/listing_segments.csv"),
    )
    ap.add_argument(
        "--emb-cache", type=Path, default=Path("data/listings_text_emb.npz")
    )
    ap.add_argument("--model", type=str, default="all-MiniLM-L6-v2")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument(
        "--method", type=str, default="hdbscan", choices=["hdbscan", "kmeans"]
    )
    ap.add_argument("--k", type=str, default="8", help="k for kmeans or 'auto'")
    ap.add_argument("--pca-dim", type=int, default=50, help="0 disables PCA")
    ap.add_argument("--random-state", type=int, default=42)
    ap.add_argument("--min-cluster-size", type=int, default=50)
    ap.add_argument("--min-samples", type=int, default=0, help="0 -> None")
    args = ap.parse_args()

    listings = pd.read_csv(args.listings, dtype={"id": "string"})
    listings = listings.rename(columns={"id": "listing_id"})
    listings = (
        listings.dropna(subset=["listing_id"])
        .drop_duplicates(subset=["listing_id"])
        .reset_index(drop=True)
    )

    texts = build_text(listings)
    X_emb: np.ndarray
    if args.emb_cache.exists():
        cache = np.load(args.emb_cache, allow_pickle=True)
        cached_ids = cache["listing_id"].astype(str)
        if np.array_equal(
            cached_ids,
            listings["listing_id"].astype(str).to_numpy(),
        ):
            X_emb = cache["emb"].astype(np.float32)
            print(
                f"[cache] loaded embeddings: {X_emb.shape} from {args.emb_cache}",
            )
        else:
            print(
                "[cache] cache exists but listing_id order/content differs -> recomputing"
            )
            X_emb = create_embeddings(
                texts,
                model_name=args.model,
                batch_size=args.batch_size,
                normalize=True,
            )
            np.savez_compressed(
                args.emb_cache,
                listing_id=listings["listing_id"].astype(str).to_numpy(),
                emb=X_emb,
            )
            print(f"[cache] saved embeddings: {X_emb.shape} to {args.emb_cache}")
    else:
        X_emb = create_embeddings(
            texts,
            model_name=args.model,
            batch_size=args.batch_size,
            normalize=True,
        )
        np.savez_compressed(
            args.emb_cache,
            listing_id=listings["listing_id"].astype(str).to_numpy(),
            emb=X_emb,
        )
        print(f"[cache] saved embeddings: {X_emb.shape} to {args.emb_cache}")
    pca_dim = args.pca_dim if args.pca_dim > 0 else None
    X_red = maybe_reduce_dim(
        X_emb,
        pca_dim=pca_dim,
        random_state=args.random_state,
    )
    print(f"[pca] X_red shape: {X_red.shape}")

    min_samples = None if args.min_samples <= 0 else args.min_samples
    labels = cluster_embeddings(
        X_red,
        method=args.method,
        k=(args.k if args.k == "auto" else int(args.k)),
        random_state=args.random_state,
        hdbscan_min_cluster_size=args.min_cluster_size,
        hdbscan_min_samples=min_samples,
    )

    out = pd.DataFrame(
        {
            "listing_id": listings["listing_id"].astype("string"),
            "segment_id": labels.astype(int),
        }
    )

    counts = out["segment_id"].value_counts(dropna=False).sort_index()
    print("[segments] counts:")
    print(counts.to_string())
    if (out["segment_id"] == -1).any():
        print(
            "[segments] HDBSCAN noise fraction:",
            float((out["segment_id"] == -1).mean()),
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(f"[saved] {args.out} rows={len(out)}")


if __name__ == "__main__":
    main()
