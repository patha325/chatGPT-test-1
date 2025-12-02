from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    length_function=len,
)


def chunk_document(doc: Dict) -> List[Dict]:
    chunks = splitter.split_text(doc["content"])
    return [
        {
            "id": f"{doc['id']}::chunk_{i}",
            "content": chunk,
            "metadata": {**doc.get("metadata", {}), "chunk_index": i},
        }
        for i, chunk in enumerate(chunks)
    ]
