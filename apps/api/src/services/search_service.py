from elasticsearch import Elasticsearch
import os
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """
    Search service using Elasticsearch for high-performance syllabus indexing and searching.
    Integrates Vector Search (Semantic Search) using SentenceTransformers.
    """
    def __init__(self, es_url=None):
        self.es_url = es_url or os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
        self._model = None
        self.es = None
        self._init_done = False

    def _lazy_init(self):
        """Initialize heavy dependencies only when needed."""
        if self._init_done:
            return
            
        # 1. Load AI Model
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model (this may take a while on first run)...")
            self._model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("SentenceTransformer model loaded successfully.")
        except ImportError:
            logger.warning("sentence-transformers not installed. Semantic search will be disabled.")
        except Exception as e:
            logger.error(f"Error loading SentenceTransformer: {e}")

        # 2. Connect to ES
        try:
            # Use short timeout for startup ping to avoid blocking
            self.es = Elasticsearch([self.es_url], request_timeout=2)
            if not self.es.ping():
                logger.warning("Elasticsearch is not reachable. Search will be limited.")
                self.es = None
            else:
                self._ensure_index_exists()
        except Exception as e:
            logger.error(f"Search Service ES init error: {e}")
            self.es = None
            
        self._init_done = True

    @property
    def model(self):
        if not self._init_done:
            self._lazy_init()
        return self._model

    def _ensure_index_exists(self):
        """Ensure the 'syllabuses' index exists with the correct mapping for vector search."""
        if not self.es:
            return
        
        index_name = "syllabuses"
        if not self.es.indices.exists(index=index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "subject_code": {"type": "keyword"},
                        "subject_name_vi": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text"},
                        "content": {"type": "text"},
                        "version": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "program_name": {"type": "keyword"},
                        "academic_year": {"type": "keyword"},
                        "content_vector": {
                            "type": "dense_vector",
                            "dims": 384,
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            }
            try:
                self.es.indices.create(index=index_name, body=mapping)
                logger.info(f"Created index '{index_name}' with vector mapping.")
            except Exception as e:
                logger.error(f"Error creating index: {e}")

    def index_syllabus(self, syllabus_id, content_dict):
        """Index a syllabus into Elasticsearch with generate embeddings."""
        if not self.es:
            return False
        
        try:
            # Generate embedding if model is available
            if self.model:
                # Combine relevant fields for semantic meaning
                text_to_embed = f"{content_dict.get('subject_name_vi', '')} {content_dict.get('description', '')} {content_dict.get('content', '')}"
                if text_to_embed.strip():
                    embedding = self.model.encode(text_to_embed).tolist()
                    content_dict["content_vector"] = embedding

            res = self.es.index(index="syllabuses", id=syllabus_id, document=content_dict)
            return res['result'] in ['created', 'updated']
        except Exception as e:
            logger.error(f"Indexing error for syllabus {syllabus_id}: {e}")
            return False

    def search_syllabuses(self, query_text, search_type="hybrid", filters: dict = None):
        """
        Perform search with optional filters for program_name (Major) and academic_year (Semester context).
        """
        if not self.es:
            return []
            
        try:
            # Build filters
            es_filters = []
            if filters:
                if filters.get("program"):
                    es_filters.append({"term": {"program_name": filters["program"]}})
                if filters.get("academic_year"):
                    es_filters.append({"term": {"academic_year": filters["academic_year"]}})

            if search_type == "text" or not self.model:
                body = {
                    "query": {
                        "bool": {
                            "must": {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": ["subject_name_vi^3", "subject_code^5", "description", "content"],
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    }
                }
                if es_filters:
                    body["query"]["bool"]["filter"] = es_filters
                    
            elif search_type == "semantic":
                query_vector = self.model.encode(query_text).tolist()
                body = {
                    "knn": {
                        "field": "content_vector",
                        "query_vector": query_vector,
                        "k": 10,
                        "num_candidates": 100
                    }
                }
                if es_filters:
                    body["knn"]["filter"] = {"bool": {"filter": es_filters}}
                    
            else: # Hybrid
                query_vector = self.model.encode(query_text).tolist()
                body = {
                    "query": {
                        "bool": {
                            "must": {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": ["subject_name_vi^3", "subject_code^5", "description", "content"],
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    },
                    "knn": {
                        "field": "content_vector",
                        "query_vector": query_vector,
                        "k": 10,
                        "num_candidates": 100,
                        "boost": 0.5
                    }
                }
                if es_filters:
                    body["query"]["bool"]["filter"] = es_filters
                    body["knn"]["filter"] = {"bool": {"filter": es_filters}}

            body["highlight"] = {
                "fields": {
                    "description": {},
                    "content": {}
                }
            }

            res = self.es.search(index="syllabuses", body=body)
            hits = res['hits']['hits']
            return [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"],
                    "highlight": hit.get("highlight", {})
                }
                for hit in hits
            ]
        except Exception as e:
            logger.error(f"Search error for query '{query_text}': {e}")
            return []


    def delete_index(self, syllabus_id):
        """Remove a syllabus from the search index."""
        if not self.es:
            return False
        try:
            self.es.delete(index="syllabuses", id=syllabus_id)
            return True
        except Exception as e:
            logger.error(f"Delete index error: {e}")
            return False

    def recreate_index(self):
        """Delete and recreate the index with fresh mapping."""
        if not self.es:
            return False
        try:
            if self.es.indices.exists(index="syllabuses"):
                self.es.indices.delete(index="syllabuses")
            self._ensure_index_exists()
            return True
        except Exception as e:
            logger.error(f"Recreate index error: {e}")
            return False
