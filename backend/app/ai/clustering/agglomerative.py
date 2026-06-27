from collections import defaultdict
from typing import List

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import normalize

from app.ai.interfaces import (
    ClusteringInterface,
    DiarizationSegment,
    SpeakerCluster,
    SpeakerEmbedding,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

SPEAKER_COLORS = [
    "#06D6CF",
    "#3B82F6",
    "#7C3AED",
    "#F59E0B",
    "#EC4899",
    "#10B981",
    "#F97316",
    "#6366F1",
]


class AgglomerativeClusteringService(ClusteringInterface):
    def __init__(self, distance_threshold: float = 0.65) -> None:
        self._distance_threshold = distance_threshold

    def cluster(self, embeddings: List[SpeakerEmbedding]) -> List[SpeakerCluster]:
        if not embeddings:
            return []

        if len(embeddings) == 1:
            emb = embeddings[0]
            return [
                SpeakerCluster(
                    cluster_id="speaker_0",
                    color=SPEAKER_COLORS[0],
                    embedding=emb.embedding,
                    segments=emb.segments,
                )
            ]

        embedding_matrix = np.stack([e.embedding for e in embeddings], axis=0)
        embedding_matrix = normalize(embedding_matrix, norm="l2")

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=self._distance_threshold,
            metric="cosine",
            linkage="average",
        )
        labels = clustering.fit_predict(embedding_matrix)

        cluster_map: dict[int, list[SpeakerEmbedding]] = defaultdict(list)
        for idx, label in enumerate(labels):
            cluster_map[int(label)].append(embeddings[idx])

        clusters: List[SpeakerCluster] = []
        for cluster_idx, (cluster_label, members) in enumerate(sorted(cluster_map.items())):
            mean_embedding = np.mean([m.embedding for m in members], axis=0)
            all_segments: List[DiarizationSegment] = []
            for m in members:
                all_segments.extend(m.segments)
            all_segments.sort(key=lambda s: s.start)

            clusters.append(
                SpeakerCluster(
                    cluster_id=f"speaker_{cluster_idx}",
                    color=SPEAKER_COLORS[cluster_idx % len(SPEAKER_COLORS)],
                    embedding=mean_embedding,
                    segments=all_segments,
                )
            )

        logger.info(
            "clustering_complete",
            input_speakers=len(embeddings),
            output_clusters=len(clusters),
        )
        return clusters
