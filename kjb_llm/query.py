"""Accept a contemporary English question, retrieve relevant KJB verses, and
generate a scripturally grounded answer using OpenAI."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap

import chromadb
from openai import OpenAI

from kjb_llm import config

SYSTEM_PROMPT = textwrap.dedent("""\
    You are a Bible scholar whose knowledge is limited exclusively to the
    King James Bible (KJB).  When the user asks a question you MUST answer
    using ONLY the KJB verses provided below.  Do NOT add information from
    any other source.

    Guidelines:
    - Summarise the answer in clear, contemporary English.
    - After your summary, list the supporting verse references.
    - If the provided verses do not address the question, say so honestly.
    - Never fabricate or paraphrase verses that were not provided.
""")


def _build_context(results: dict) -> str:
    """Format ChromaDB query results into a context block for the LLM."""
    lines: list[str] = []
    docs = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]
    for ref, text in zip(ids, docs):
        lines.append(f"{ref}  {text}")
    return "\n".join(lines)


def ask(question: str) -> dict:
    """Return {"answer": str, "verses": [{"reference": str, "text": str}]}."""
    oai = OpenAI(api_key=config.OPENAI_API_KEY)

    # 1. Retrieve relevant verses
    chroma = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = chroma.get_collection(config.COLLECTION_NAME)

    q_embedding = (
        oai.embeddings.create(input=[question], model=config.EMBEDDING_MODEL)
        .data[0]
        .embedding
    )

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=config.TOP_K,
        include=["documents", "metadatas"],
    )

    context = _build_context(results)

    # 2. Generate answer
    user_msg = (
        f"Relevant KJB verses:\n{context}\n\n"
        f"Question: {question}"
    )

    completion = oai.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
    )

    answer_text = completion.choices[0].message.content

    # 3. Build structured response
    verses = []
    docs = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]
    for ref, text in zip(ids, docs):
        verses.append({"reference": ref, "text": text})

    return {"answer": answer_text, "verses": verses}


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the KJB-LLM")
    parser.add_argument("question", nargs="?", help="Your question in plain English")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    question = args.question
    if not question:
        question = input("Ask the King James Bible: ").strip()
    if not question:
        print("No question provided.", file=sys.stderr)
        sys.exit(1)

    result = ask(question)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nAnswer:\n{result['answer']}\n")
        print("Supporting verses:")
        for v in result["verses"]:
            print(f"  - {v['reference']}  {v['text'][:120]}...")


if __name__ == "__main__":
    main()
