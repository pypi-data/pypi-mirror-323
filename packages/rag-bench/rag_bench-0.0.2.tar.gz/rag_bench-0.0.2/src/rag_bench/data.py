from datasets import load_dataset
from .helper import log


def get_dataset():
    log("Loading dataset")

    # Test dataset
    return load_dataset("averoo/rag-news-test", token="<token>")
