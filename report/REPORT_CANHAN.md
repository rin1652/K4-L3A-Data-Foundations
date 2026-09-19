# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đình Phúc
**Nhóm:** G13
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 59** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (9).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> _Độ tương tự cosine đo lường góc giữa hai vector nhúng (embedding vectors). Khi góc này nhỏ (gần 0), hai vector hướng về nhau, biểu thị nội dung tương đồng; khi góc lớn (gần 180 độ), chúng trái ngược nhau, biểu thị nội dung khác biệt._

**Ví dụ có độ tương tự CAO:**

- Câu A: "Tôi cần gia hạn thẻ thư viện"
- Câu B: "Tôi muốn gia hạn thẻ mượn sách"
- Tại sao tương đồng:

> _Cả hai câu đều diễn đạt nhu cầu gia hạn thẻ, sử dụng từ khóa "gia hạn", "thẻ thư viện/mượn sách" tương ứng, do đó embedding vectors của chúng có hướng rất gần nhau._

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Lịch học kỳ mới được công bố"
- Câu B: "Thẻ thư viện của tôi sắp hết hạn"
- Tại sao khác:

> _Câu A nói về lịch học, trong khi câu B nói về thẻ thư viện, hai chủ đề hoàn toàn khác biệt nên embedding vectors của chúng có hướng rất khác nhau._

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> _Độ tương tự cosine đo góc giữa hai vector (phản ánh hướng và bản chất ngữ nghĩa) mà không bị phụ thuộc vào độ dài (magnitude) của vector. Trong văn bản, độ dài của vector nhúng thường bị chi phối bởi độ dài câu văn hoặc tần suất lặp lại của từ. Với khoảng cách Euclid, một câu ngắn và một đoạn văn dài dù cùng một ý nghĩa vẫn có thể bị tính là xa nhau do chênh lệch độ dài; trong khi với cosine, hai vector này vẫn cùng hướng và cho điểm tương đồng cao._

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> _Trình bày chi tiết công thức và phép tính:_
>
> 1. **Hiểu về bước nhảy (Stride/Step):**
>    Mỗi chunk có kích thước cố định là `chunk_size = 500`. Tuy nhiên, vì có độ chồng chéo (overlap) là `50`, nên chunk tiếp theo sẽ bắt đầu bằng cách lùi lại 50 ký tự so với điểm kết thúc của chunk trước đó.
>    Do đó, khoảng cách dịch chuyển tịnh tiến thực tế sau mỗi chunk (bước nhảy) là:
>    $S = \text{chunk\_size} - \text{overlap} = 500 - 50 = 450$ ký tự.
> 2. **Phân bổ tài liệu:**
>    - **Chunk 1:** Sẽ luôn bao phủ đúng 500 ký tự đầu tiên (từ vị trí 0 đến 500).
>    - Sau khi cắt Chunk 1, phần văn bản còn lại chưa được bao phủ là:
>      $10{,}000 - 500 = 9{,}500$ ký tự.
> 3. **Tính số lượng chunk tiếp theo:**
>    - Mỗi chunk tiếp theo sẽ tiến tới đúng một bước nhảy $S = 450$ ký tự để phủ dần phần văn bản còn lại.
>    - Số chunk bổ sung cần thiết để phủ hết 9,500 ký tự này là:
>      $\lceil \frac{9{,}500}{450} \rceil = \lceil 21.111... \rceil = 22$ chunks.
>      _(Lưu ý: Dùng hàm trần (ceiling) vì dù phần dư ở cuối cùng chỉ còn vài ký tự thì vẫn cần cấp trọn vẹn 1 chunk để chứa chúng)._
> 4. **Tổng kết:**
>    - Tổng số chunk = 1 (Chunk đầu tiên) + 22 (Các chunk bổ sung) = **23 chunks**.
>    - Cụ thể: Chunk cuối cùng (thứ 23) sẽ không đủ 500 ký tự mới mà nó bao gồm 50 ký tự lẻ còn sót lại cộng với 450 ký tự chồng chéo lấy từ chunk thứ 22.
>
> **Đáp án:** 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> _Sự thay đổi về số lượng chunk:_
>
> - Khi overlap tăng lên 100, bước nhảy sẽ bị thu hẹp lại: $S = 500 - 100 = 400$ ký tự.
> - Số chunk bổ sung cần thiết: $\lceil \frac{10{,}000 - 500}{400} \rceil = \lceil \frac{9{,}500}{400} \rceil = \lceil 23.75 \rceil = 24$ chunks.
> - Tổng số chunk mới: $1 + 24 = 25$ chunks.
>   => Kết luận: Số lượng chunk **tăng thêm 2 chunks** (từ 23 lên 25).
>
> _Tại sao lại muốn độ chồng chéo nhiều hơn (Why larger overlap)?_
>
> - **Bảo toàn ngữ cảnh tại ranh giới:** Việc cắt văn bản theo số ký tự cố định (FixedSize) rất dễ vô tình chém đôi một câu quan trọng, một cái tên riêng, hoặc tách rời chủ ngữ khỏi vị ngữ.
> - **Tránh mất mát thông tin khi truy xuất (Retrieval):** Nếu một khái niệm/từ khóa quan trọng bị cắt đứt làm đôi ở đường mép của chunk, mô hình nhúng (embedding model) sẽ không thể hiểu được ý nghĩa toàn vẹn của nó, dẫn đến điểm vector bị sai lệch. Overlap lớn hơn đóng vai trò như một "chất keo" liên kết, đảm bảo mọi ý tưởng hoặc câu văn đều có cơ hội xuất hiện trọn vẹn trong ít nhất một chunk, qua đó tăng khả năng truy xuất thành công (recall) của hệ thống RAG.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> _Sử dụng biểu thức chính quy (Regex: `r'(?<=[.!?])\s+'`) để tách chuỗi văn bản theo các dấu kết thúc câu (`.`, `!`, `?`) kèm theo khoảng trắng, bảo toàn dấu câu. Để xử lý các ngoại lệ (edge cases), hàm kiểm tra văn bản rỗng, loại bỏ các chuỗi rỗng sau split, sau đó gom tuần tự tối đa `max_sentences_per_chunk` câu vào mỗi chunk nhằm đảm bảo mỗi chunk là một chỉnh thể ngữ pháp hoàn chỉnh._

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> _Áp dụng thuật toán chia đệ quy với danh sách ký tự phân tách phân tầng giảm dần: đoạn văn (`"\n\n"`), xuống dòng (`"\n"`), khoảng trắng từ (`" "`) và ký tự rỗng (`""`). Trường hợp cơ sở (base case) xảy ra khi chuỗi con có độ dài nhỏ hơn hoặc bằng `chunk_size` (giữ nguyên không tách tiếp), hoặc khi danh sách separators đã cạn (cắt cứng cố định theo `chunk_size`). Sau khi chia nhỏ các mảnh, hàm `_merge` gom các mảnh kề nhau lại với nhau sao cho tổng độ dài không vượt quá `chunk_size`._

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> _Các tài liệu `Document` được đưa qua `_make_record`, tính vector nhúng qua hàm `_embedding_fn` và lưu dưới dạng danh sách từ điển trong bộ nhớ (`self._store`). Khi tìm kiếm `search`, hệ thống nhúng câu hỏi người dùng thành vector, tính tích vô hướng (dot product - tương đương cosine similarity vì vector đã được chuẩn hóa L2) giữa vector câu hỏi và từng chunk trong kho lưu trữ, sắp xếp giảm dần theo điểm tương đồng và trả về `top_k` kết quả cao nhất._

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> _Phương thức `search_with_filter` áp dụng cơ chế tiền lọc (pre-filtering): lọc trước danh sách bản ghi thỏa mãn 100% các điều kiện trong `metadata_filter` rồi mới tính điểm tương đồng trên tập đã lọc, tránh việc sau khi lấy top_k mới lọc làm thiếu kết quả. Phương thức `delete_document` duyệt qua kho và loại bỏ mọi chunk có `id == doc_id` hoặc `metadata['doc_id'] == doc_id`, trả về `True` nếu xóa thành công ít nhất một bản ghi._

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> _Tác tử nhận câu hỏi, gọi `store.search(question, top_k=top_k)` để truy xuất các đoạn tài liệu liên quan nhất, sau đó nối các đoạn này thành ngữ cảnh tham chiếu (`context`). Prompt được thiết kế nghiêm ngặt: yêu cầu mô hình LLM chỉ trả lời dựa trên ngữ cảnh được cung cấp, nêu rõ nguồn trích dẫn và không tự suy đoán thông tin ngoài ngữ cảnh. Cuối cùng, hàm gọi `llm_fn(prompt)` để sinh câu trả lời chính xác._

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.03s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                                            | Câu B                                                            | Dự đoán | Điểm thực tế | Đúng? |
| --- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ------- | ------------ | ----- |
| 1   | Cổng đăng ký SIS mở lúc 14:00 ngày 18/12/2025                    | Thời gian bắt đầu mở cổng đăng ký môn học trên hệ thống SIS      | cao     | 0.7236       | Đúng  |
| 2   | Sinh viên được rút tối đa 18 tín chỉ trong toàn chương trình     | Giới hạn số tín chỉ sinh viên có thể xin withdraw trong khóa học | cao     | 0.6980       | Đúng  |
| 3   | Hạn cuối cùng để sinh viên nộp đơn thêm môn học là 06/03/2026    | Menu đồ ăn trưa tại căng tin trường đại học hôm nay              | thấp    | 0.1857       | Đúng  |
| 4   | Quy định xử lý kỷ luật sinh viên vi phạm liêm chính học thuật    | Hướng dẫn giảng viên cập nhật phòng học trên hệ thống            | thấp    | 0.3927       | Đúng  |
| 5   | Sinh viên không được đăng ký môn học nếu chưa đạt môn tiên quyết | Hệ thống tự động chặn đăng ký khi sinh viên thiếu prerequisite   | cao     | 0.5692       | Đúng  |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> _Kết quả ở Cặp 5 rất ấn tượng (đạt điểm 0.5692): dù câu B sử dụng thuật ngữ tiếng Anh ("prerequisite" thay vì "môn tiên quyết"), mô hình đa ngữ vẫn phát hiện sự tương đồng ngữ nghĩa chính xác. Điều này chứng minh embeddings không hoạt động bằng so khớp từ khóa cơ học (lexical matching) mà thực sự hiểu và biểu diễn khái niệm ngữ nghĩa trong không gian đa chiều (semantic representation)._

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src` bằng chiến lược `RecursiveChunker(chunk_size=300)`.

| #   | Câu hỏi (Query)                                                                                             | Top-1 Chunk truy xuất được (tóm tắt)                                                                                                  | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                                                                                 |
| --- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Cổng đăng ký SIS kỳ Spring 2026 mở lúc nào?                                                                 | `lich-dang-ky-spring-2026.md`: Cổng đăng ký SIS mở lúc 14:00 ngày 18/12/2025; lịch học công bố 15-17/12.                              | 0.8788     | Có (Gold Top-1)                | Cổng đăng ký SIS mở lúc 14:00 ngày 18/12/2025.                                                                                  |
| 2   | Đăng ký học phần trên SIS gồm những bước nào? Trạng thái nào mới là đăng ký thành công?                     | `huong-dan-dang-ky-hoc-phan.md`: Lộ trình học phần, chọn học kỳ, Register khi Open, Add rồi Register. Trạng thái Registered.          | 0.7202     | Có (Gold Top-1)                | Đăng nhập SIS → Academics → Course Registration → Register khi Open → Add và Register. Trạng thái Registered mới là thành công. |
| 3   | Nếu môn trùng giờ hoặc chưa đủ điều kiện tiên quyết thì SIS xử lý thế nào?                                  | `huong-dan-dang-ky-hoc-phan.md`: SIS không cho đăng ký trùng giờ và tự động chặn khi chưa đạt tiên quyết.                             | 0.6737     | Có (Gold Top-1)                | SIS tự động chặn đăng ký môn trùng giờ hoặc chưa đạt môn tiên quyết; liên hệ Phòng Đào tạo nếu cần hỗ trợ.                      |
| 4   | Sinh viên được rút (withdraw) tối đa bao nhiêu tín chỉ trong cả chương trình? Sau khi đạt giới hạn thì sao? | `sinh-vien-add-drop-withdraw-spring-2026.md`: Rút tối đa 18 tín chỉ trong toàn chương trình; đạt giới hạn phải học tiếp và nhận điểm. | 0.8197     | Có (Gold Top-1)                | Sinh viên được rút tối đa 18 tín chỉ trong toàn khóa; sau khi đạt giới hạn phải tiếp tục học và nhận điểm.                      |
| 5   | Trước ngày bắt đầu giảng dạy Spring 2026, tôi cần kiểm tra những gì? _(Lọc: `audience: student`)_           | `sinh-vien-add-drop-withdraw-spring-2026.md` _(Hạng 2)_: Xác nhận thời gian, địa điểm học; kiểm tra đồng bộ môn giữa SIS và Canvas.   | 0.6739     | Có (Gold Top-2)                | Sinh viên cần xác nhận lịch học, phòng học và kiểm tra đồng bộ môn đăng ký trên SIS hiển thị đúng trên Canvas.                  |

### Chi tiết Top-3 kết quả truy xuất

**Q1: Cổng đăng ký SIS kỳ Spring 2026 mở lúc nào?**
- Hạng 1: `lich-dang-ky-spring-2026.md` (score=0.8788) - Có chứa thông tin trả lời (2/2)
- Hạng 2: `lich-dang-ky-spring-2026.md` (score=0.7528) - Có chứa thông tin trả lời
- Hạng 3: `giang-vien-kiem-tra-lich-spring-2026.md` (score=0.6019) - Không

**Q2: Đăng ký học phần trên SIS gồm những bước nào? Trạng thái nào mới là đăng ký thành công?**
- Hạng 1: `huong-dan-dang-ky-hoc-phan.md` (score=0.7202) - Có chứa thông tin trả lời (2/2)
- Hạng 2: `huong-dan-dang-ky-hoc-phan.md` (score=0.7029) - Có chứa thông tin trả lời
- Hạng 3: `lich-dang-ky-spring-2026.md` (score=0.6365) - Không

**Q3: Nếu môn trùng giờ hoặc chưa đủ điều kiện tiên quyết thì SIS xử lý thế nào?**
- Hạng 1: `huong-dan-dang-ky-hoc-phan.md` (score=0.6737) - Có chứa thông tin trả lời (2/2)
- Hạng 2: `huong-dan-dang-ky-hoc-phan.md` (score=0.5207) - Có chứa thông tin trả lời
- Hạng 3: `lich-dang-ky-spring-2026.md` (score=0.4648) - Không

**Q4: Sinh viên được rút (withdraw) tối đa bao nhiêu tín chỉ trong cả chương trình? Sau khi đạt giới hạn thì sao?**
- Hạng 1: `sinh-vien-add-drop-withdraw-spring-2026.md` (score=0.8197) - Có chứa thông tin trả lời (2/2)
- Hạng 2: `quy-dinh-hoc-thuat-dai-hoc.md` (score=0.7508) - Không
- Hạng 3: `sinh-vien-add-drop-withdraw-spring-2026.md` (score=0.6828) - Có chứa thông tin trả lời

**Q5: Trước ngày bắt đầu giảng dạy Spring 2026, tôi cần kiểm tra những gì?**
- Hạng 1: `lich-dang-ky-spring-2026.md` (score=0.6837) - Không
- Hạng 2: `sinh-vien-add-drop-withdraw-spring-2026.md` (score=0.6739) - Có chứa thông tin trả lời (1/2)
- Hạng 3: `lich-dang-ky-spring-2026.md` (score=0.6720) - Không

### A/B Metadata Filter

- **Top-3 khi không filter**:
  - Hạng 1: `giang-vien-kiem-tra-lich-spring-2026.md` (score=0.7833)
  - Hạng 2: `giang-vien-kiem-tra-lich-spring-2026.md` (score=0.6876)
  - Hạng 3: `lich-dang-ky-spring-2026.md` (score=0.6837)
- **Top-3 khi dùng `metadata_filter={"audience": "student"}`**:
  - Hạng 1: `lich-dang-ky-spring-2026.md` (score=0.6837)
  - Hạng 2: `sinh-vien-add-drop-withdraw-spring-2026.md` (score=0.6739)
  - Hạng 3: `lich-dang-ky-spring-2026.md` (score=0.6720)

**Kết luận**: Việc sử dụng metadata filter đã giúp loại bỏ các tài liệu không liên quan dành cho giảng viên khỏi kết quả. Nhờ đó, tài liệu chính xác dành cho sinh viên (`sinh-vien-add-drop-withdraw-spring-2026.md`) đã xuất hiện ở hạng 2, cung cấp ngữ cảnh đúng cho mô hình trả lời.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**
**Tổng điểm benchmark:** **9 / 10**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> _Điều tâm đắc nhất là nhận thấy sức mạnh vượt trội của Metadata Pre-filtering khi xử lý ngữ liệu đa đối tượng: nếu không lọc theo `audience: student`, câu hỏi số 5 sẽ bị tài liệu của giảng viên chiếm mất vị trí top-1/top-2 gây trả lời sai lệch. Đồng thời, qua việc so sánh đối chiếu giữa 3 chiến lược, tôi thấy `RecursiveChunker` cân bằng hoàn hảo nhất giữa cấu trúc Markdown và kích thước vector._

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10           |
| **Tổng phần cá nhân**                           | **59 / 60**      |
