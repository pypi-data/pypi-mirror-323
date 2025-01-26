from typing import Optional
from datetime import datetime
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder, FastembedDocumentEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.dataclasses import Document
from haystack.utils import Secret
from ..birbtalk import BirbTalk, BirbTool

class BirbTalkWithQdrantMemory(BirbTalk):
    def __init__(self, *args, 
                 qdrant_url: Optional[str] = None, 
                 qdrant_key: Optional[str] = None,
                 collection_name: str = "memories",
                 embedding_model: str = "BAAI/bge-small-en-v1.5",
                 embedding_cache_dir: Optional[str] = None,
                 embedding_local_only: bool = False,
                 embedding_dim: int = 384,
                 n_memories: int = 10,
                 **kwargs):
        self.n_memories = n_memories
        # Define tools
        new_tools = [
            BirbTool(
                name = "save_memory",
                description = "Save short facts about user in memory.",
                function = self.save_memory,
                arguments = {
                    "fact": {
                        "type": "string",
                        "description": "Fact about user such as their preferences, hobbies, life conditions and etc. Should be short and informative. Only use English."
                    }
                },
                required = ["fact"]
            ),
            BirbTool(
                name = "search_memory",
                description = "Search for facts about user such as their preferences, hobbies or life conditions in memory.",
                function = self.load_memory, 
                arguments = {
                    "query": {
                        "type": "string",
                        "description": "Query for performing search in vector database. Should be specific and contain as much keywords as possible. Only use English."
                }
                },
                required = ["query"]
            ),
        ]
        ''' # TODO:
            BirbTool(
                name = "delete_memory",
                description = "Delete fact about user from memory if it is no longer relevant",
                function = lambda : "",
                arguments = {
                    "fact": {
                        "type": "string",
                        "description": "Fact about user to be removed from memory. Should be very specific, otherwise may lead to a data loss"
                    }
                },
                required = ["fact"]
            )

        '''
        # Add tools to init kwargs
        if "tools" in kwargs: kwargs["tools"] = new_tools + kwargs["tools"]
        else: kwargs["tools"] = new_tools
        # Initilize parent class
        super(BirbTalkWithQdrantMemory, self).__init__(*args, **kwargs)
        # Define component erguments
        embedder_kwargs = {
            "model": embedding_model,
            "cache_dir": embedding_cache_dir,
            "local_files_only": embedding_local_only
        }
        qdrant_kwargs = {
            "index": collection_name,
            "wait_result_from_api": True,
            "embedding_dim": embedding_dim,
            "hnsw_config": {
                "payload_m": 16,
                "m": 0
            },
            "payload_fields_to_index": [{
                "field_name": "meta.chat_id",
                "field_schema": {"type": "keyword", "is_tenant": True}
            }]
        }
        qdrant_args = []
        if qdrant_url: qdrant_kwargs["url"] = qdrant_url
        else: qdrant_args.append(":memory:")
        if qdrant_key: qdrant_kwargs["api_key"] = Secret.from_token(qdrant_key)
        chat_id = kwargs["chat_id"] if "chat_id" in kwargs else None
        if chat_id:
            filters = {"field": "meta.chat_id", "operator": "==", "value": chat_id}
        else: filters = None
        # Initilize components
        self.text_embedder = FastembedTextEmbedder(**embedder_kwargs)
        self.doc_embedder = FastembedDocumentEmbedder(**embedder_kwargs)
        document_store = QdrantDocumentStore(*qdrant_args, **qdrant_kwargs)
        self.writer = DocumentWriter(document_store=document_store, policy=DuplicatePolicy.NONE)
        self.retriever = QdrantEmbeddingRetriever(
            document_store=document_store,
            filters=filters
        )
        # Load embedders
        self.text_embedder.warm_up()
        self.doc_embedder.warm_up()

    # Save memories
    def save_memory(self, fact: str, chat_id: Optional[int] = None):
        documents = [Document(content=fact, meta={
            "chat_id": chat_id,
            "datetime": datetime.now().isoformat()
        })]
        documents = self.doc_embedder.run(documents=documents)["documents"]
        self.writer.run(documents=documents)
        return "Memory saved!"

    # Load memory
    def load_memory(self, query: str, chat_id: Optional[int] = None):
        query = self.text_embedder.run(text=query)["embedding"]
        documents = self.retriever.run(query_embedding=query)["documents"]
        max_documents = min(len(documents), self.n_memories)
        documents = documents[:max_documents]
        if documents:
            text = [f"- {x.content}" for x in documents]
            text = "\n".join(text)
            text = f"# Memories\n\n{text}"
        else:
            text = "Nothing found!"
        return text
