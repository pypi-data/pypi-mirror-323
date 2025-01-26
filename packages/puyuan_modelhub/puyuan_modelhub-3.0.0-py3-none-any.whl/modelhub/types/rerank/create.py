from typing import List

from typing_extensions import NotRequired, TypedDict


class RerankParams(TypedDict, total=False):
    sentences: List[List[str]]
    model: str
    apply_softmax: NotRequired[bool]
