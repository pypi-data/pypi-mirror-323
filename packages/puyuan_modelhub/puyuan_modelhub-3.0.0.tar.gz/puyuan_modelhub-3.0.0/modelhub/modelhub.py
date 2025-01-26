from modelhub._async_mh import AsyncModelhub
from modelhub._sync_mh import SyncModelhub


class Modelhub:
    def __init__(self, *args, **kwargs):
        _sync = SyncModelhub(*args, **kwargs)
        _async = AsyncModelhub(*args, **kwargs)
        self.generate = _sync.generate
        self.embedding = _sync.embedding
        self.embedding_dim = _sync.embedding_dim
        self.stream = _sync.stream
        self.rerank = _sync.rerank
        self.tokenize = _sync.tokenize
        self.transcribe = _sync.transcribe
        self.health = _sync.health
        self.supported_models = _sync.supported_models

        self.agenerate = _async.generate
        self.aembedding = _async.embedding
        self.aembedding_dim = _async.embedding_dim
        self.astream = _async.stream
        self.arerank = _async.rerank
        self.atokenize = _async.tokenize
        self.atranscribe = _async.transcribe
        self.ahealth = _async.health
