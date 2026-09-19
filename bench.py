"""
Benchmark Evaluation Script for Lab 7 — K4-L3A
Role 4: Report & Demo Lead

Runs the 5 agreed-upon benchmark queries on data/vinuni-course-registration/
using the student's chosen chunking strategy (RecursiveChunker).
Outputs results to terminal and saves to ket_qua_benchmark.txt.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from dotenv import load_dotenv

from src.chunking import RecursiveChunker
from src.embeddings import LocalEmbedder, MockEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Cổng đăng ký SIS kỳ Spring 2026 mở lúc nào?",
        "gold_answer": "Cổng đăng ký SIS mở lúc 14:00 ngày 18/12/2025.",
        "gold_file": "lich-dang-ky-spring-2026",
        "filter": None,
    },
    {
        "id": 2,
        "query": "Đăng ký học phần trên SIS gồm những bước nào? Trạng thái nào mới là đăng ký thành công?",
        "gold_answer": "Đăng nhập SIS → Academics → Course Registration → chọn học kỳ → Register khi Open → Add rồi Register. Trạng thái phải là Registered (Selected = chưa thành công).",
        "gold_file": "huong-dan-dang-ky-hoc-phan",
        "filter": None,
    },
    {
        "id": 3,
        "query": "Nếu môn trùng giờ hoặc chưa đủ điều kiện tiên quyết thì SIS xử lý thế nào?",
        "gold_answer": "SIS không cho đăng ký môn trùng giờ và tự động chặn khi chưa đạt tiên quyết. Nếu bị chặn dù nghĩ đủ điều kiện → liên hệ Phòng Quản lý Đào tạo.",
        "gold_file": "huong-dan-dang-ky-hoc-phan",
        "filter": None,
    },
    {
        "id": 4,
        "query": "Sinh viên được rút (withdraw) tối đa bao nhiêu tín chỉ trong cả chương trình? Sau khi đạt giới hạn thì sao?",
        "gold_answer": "Rút tối đa 18 tín chỉ trong toàn chương trình. Khi đạt giới hạn phải tiếp tục học và nhận điểm cho môn đã đăng ký.",
        "gold_file": "sinh-vien-add-drop-withdraw-spring-2026",
        "filter": None,
    },
    {
        "id": 5,
        "query": "Trước ngày bắt đầu giảng dạy Spring 2026, tôi cần kiểm tra những gì?",
        "gold_answer": "Sinh viên phải xác nhận thời gian, địa điểm học và kiểm tra các môn đã đăng ký trên SIS được đồng bộ, hiển thị đúng trên Canvas. Nếu môn có trên SIS nhưng không xuất hiện trên Canvas thì báo Phòng Quản lý Đào tạo.",
        "gold_file": "sinh-vien-add-drop-withdraw-spring-2026",
        "filter": {"audience": "student"},
    },
]


def load_corpus(data_dir: Path, chunker: RecursiveChunker) -> list[Document]:
    chunk_docs: list[Document] = []
    md_files = sorted(data_dir.glob("*.md"))

    for p in md_files:
        raw_text = p.read_text(encoding="utf-8")
        parts = raw_text.split("---")
        if len(parts) > 2:
            fm_text = parts[1]
            body_text = "---".join(parts[2:]).strip()
            fm = dict(re.findall(r"^(\w+):\s*(.+)$", fm_text, re.M))
            fm = {k: v.strip("\"'") for k, v in fm.items()}
        else:
            fm = {}
            body_text = raw_text.strip()

        fm["doc_id"] = p.stem
        fm["source_file"] = p.name

        chunks = chunker.chunk(body_text)
        for i, chunk in enumerate(chunks):
            chunk_docs.append(
                Document(
                    id=f"{p.stem}#{i}",
                    content=chunk,
                    metadata=dict(fm),
                )
            )
    return chunk_docs


def run_benchmark() -> str:
    load_dotenv()
    output_lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        output_lines.append(msg)

    log("=" * 70)
    log("BENCHMARK RETRIEVAL REPORT — VINUNI COURSE REGISTRATION")
    log("Strategy: RecursiveChunker (chunk_size=300)")
    log("=" * 70)

    # Choose embedder
    try:
        embedder = LocalEmbedder()
        log(f"Embedder backend: {embedder._backend_name}")
    except Exception as e:
        log(f"LocalEmbedder fallback to mock: {e}")
        embedder = _mock_embed

    chunker = RecursiveChunker(chunk_size=300)
    corpus_dir = Path("data/vinuni-course-registration")
    chunk_docs = load_corpus(corpus_dir, chunker)
    log(f"Loaded {len(chunk_docs)} chunks from {corpus_dir}")

    store = EmbeddingStore(collection_name="vinuni_bench", embedding_fn=embedder)
    store.add_documents(chunk_docs)
    log(f"Indexed in EmbeddingStore: {store.get_collection_size()} records\n")

    # Run each benchmark query
    total_relevant = 0
    for item in BENCHMARK_QUERIES:
        qid = item["id"]
        q = item["query"]
        gold_ans = item["gold_answer"]
        gold_file = item["gold_file"]
        flt = item["filter"]

        log(f"--- Câu hỏi {qid} ---")
        log(f"Query: {q}")
        log(f"Gold Answer: {gold_ans}")
        log(f"Target file: {gold_file}.md")
        if flt:
            log(f"Filter áp dụng: {flt}")
            results = store.search_with_filter(q, top_k=3, metadata_filter=flt)
        else:
            log("Filter áp dụng: Không")
            results = store.search(q, top_k=3)

        found_in_top3 = False
        for rank, r in enumerate(results, 1):
            source = r["metadata"].get("source_file", r["metadata"].get("doc_id", "unknown"))
            doc_id = r["metadata"].get("doc_id", "")
            score = r["score"]
            preview = r["content"][:100].replace("\n", " ")
            is_gold = doc_id == gold_file
            if is_gold:
                found_in_top3 = True
            log(f"  [{rank}] score={score:.4f} doc={source} {'(GOLD)' if is_gold else ''}")
            log(f"      preview: {preview}...")

        if found_in_top3:
            total_relevant += 1
            log("=> Kết quả: CO CHUNK LIEN QUAN TRONG TOP-3 (PASS)\n")
        else:
            log("=> Kết quả: CHUA CO CHUNK LIEN QUAN TRONG TOP-3\n")

    # A/B Testing for Question 5 (with vs without filter)
    log("=" * 70)
    log("A/B TEST CHO CÂU HỎI 5 (KIỂM CHỨNG TÁC DỤNG CỦA METADATA FILTER)")
    log("=" * 70)
    q5 = BENCHMARK_QUERIES[4]["query"]
    log(f"Query: {q5}\n")

    log("1) Chạy KHÔNG có metadata_filter:")
    res_nofilter = store.search(q5, top_k=3)
    for rank, r in enumerate(res_nofilter, 1):
        source = r["metadata"].get("source_file", "")
        aud = r["metadata"].get("audience", "")
        log(f"  [{rank}] score={r['score']:.4f} doc={source} (audience: {aud})")
        log(f"      preview: {r['content'][:90].replace(chr(10), ' ')}...")

    log("\n2) Chạy CÓ metadata_filter={'audience': 'student'}:")
    res_filtered = store.search_with_filter(q5, top_k=3, metadata_filter={"audience": "student"})
    for rank, r in enumerate(res_filtered, 1):
        source = r["metadata"].get("source_file", "")
        aud = r["metadata"].get("audience", "")
        log(f"  [{rank}] score={r['score']:.4f} doc={source} (audience: {aud})")
        log(f"      preview: {r['content'][:90].replace(chr(10), ' ')}...")

    log(f"\nTổng kết: {total_relevant}/5 câu hỏi có chunk liên quan trong top-3.")
    
    # Save to file
    content = "\n".join(output_lines)
    Path("ket_qua_benchmark.txt").write_text(content, encoding="utf-8")
    log("=> Đã lưu toàn bộ kết quả vào: ket_qua_benchmark.txt")
    return content


if __name__ == "__main__":
    run_benchmark()
