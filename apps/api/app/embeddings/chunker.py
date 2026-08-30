from dataclasses import dataclass
from typing import List

# Maximum lines per chunk. Kept small enough to stay within embedding model token limits
# (all-MiniLM-L6-v2 has a 256 word-piece limit, ~512 chars is safe).
MAX_LINES_PER_CHUNK = 60
OVERLAP_LINES = 5  # Slide-window overlap to avoid cutting context at boundaries


@dataclass
class CodeChunk:
    """A chunk of source code with its line range for evidence tracking."""
    content: str
    start_line: int
    end_line: int


def chunk_file(content: str) -> List[CodeChunk]:
    """
    Splits raw file content into overlapping line-window chunks.

    Preserves start_line/end_line so that every chunk can be traced back
    to its exact location in the source file—this is the basis for the
    evidence display in the investigation result.

    Args:
        content: The full raw text content of a source file.

    Returns:
        A list of CodeChunk objects with 1-indexed line numbers.
    """
    lines = content.splitlines()
    total_lines = len(lines)

    if total_lines == 0:
        return []

    chunks: List[CodeChunk] = []
    start = 0

    while start < total_lines:
        end = min(start + MAX_LINES_PER_CHUNK, total_lines)
        chunk_lines = lines[start:end]
        chunk_text = "\n".join(chunk_lines).strip()

        if chunk_text:
            chunks.append(
                CodeChunk(
                    content=chunk_text,
                    # Lines are 1-indexed for human-readable evidence
                    start_line=start + 1,
                    end_line=end,
                )
            )

        # Slide forward, but keep OVERLAP_LINES of context.
        # Stop if the next window would start so close to the end that it
        # would produce only overlap content with no new material.
        next_start = end - OVERLAP_LINES
        if next_start <= start or next_start >= total_lines:
            break
        start = next_start

    return chunks
