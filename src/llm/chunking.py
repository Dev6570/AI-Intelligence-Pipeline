import re
def split_text(text, max_chars=12000, overlap=500):
    """
    Split long text into manageable chunks.
    max_chars: Maximum characters per chunk.
    overlap: Number of characters carried forward.
    """
    if not text:
        return []
    paragraphs = re.split(r"\n\s*\n", text.strip())
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            for sentence in sentences:
                if len(sentence) > max_chars:
                    for start in range(0, len(sentence), max_chars):
                        chunks.append(
                            sentence[start:start + max_chars]
                        )
                    continue
                if (
                    current_chunk
                    and len(current_chunk) + len(sentence) + 1
                    > max_chars
                ):
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    current_chunk = (
                        current_chunk + " " + sentence
                    ).strip()
            continue
        if (
            current_chunk
            and len(current_chunk) + len(paragraph) + 2
            > max_chars
        ):
            chunks.append(current_chunk)
            current_chunk = (
                current_chunk[-overlap:] + "\n\n" + paragraph
                if overlap
                else paragraph
            )
        else:
            current_chunk = (
                current_chunk + "\n\n" + paragraph
            ).strip()
    if current_chunk:
        chunks.append(current_chunk)
    return chunks