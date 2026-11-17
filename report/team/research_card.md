# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 — Architecture choices; ablation bật/tắt một lượt investigator read-only thứ hai trong cùng orchestrator. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Bogavelli, Sharma và Subramani, *AgentArch: A Comprehensive Benchmark to Evaluate Agent Architectures in Enterprise*, bản arXiv v2 (2026; bản đầu 2025), https://arxiv.org/abs/2509.10769v2. Loại bằng chứng: benchmark thực nghiệm; sử dụng abstract của nguồn sơ cấp để xác định claim và phạm vi. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | AgentArch khảo sát 18 cấu hình và nhận thấy lựa chọn kiến trúc phụ thuộc model; kết quả không ủng hộ một cấu hình phù hợp cho mọi trường hợp. Giả thuyết về lượt investigator lặp dưới đây là suy luận của nhóm, không phải kết quả được paper chứng minh. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn khảo sát các model và tác vụ doanh nghiệp trong benchmark riêng, xét orchestration, ReAct/function calling, memory và thinking tool. Không coi kết quả đó là bằng chứng trực tiếp cho LogiX-VN hay MockLLM. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Bật investigator thứ hai chạy cùng read tools trên cùng snapshot sẽ không đổi pass rate/pass^5 (chênh 0 điểm phần trăm), variance vẫn 0; cost/success dự kiến tăng khoảng 70–90% do lặp đọc. Đây là giả thuyết khám phá sau khi đã xem benchmark bốn shape; không phải dự đoán đăng ký trước. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định orchestrator, tool registry và thứ tự tool của mỗi investigator, logic quote/approval/ledger, backend MockLLM (cả hai cấu hình thực tế có 0 model call), 14 claim public, seed 11/22/33/44/55, as_of 2026-11-15, pricing và evaluator chính thức; mỗi trial có SQLite mới. Biến duy nhất: bật/tắt lượt investigator thứ hai, chạy tuần tự cùng handoff, cùng tool và cùng quyền read-only trước khi host ghi tiền. Variant trong src/bonus/investigator_ablation.py dùng lại orchestrator chính thức, kiểm hai kết quả đọc bằng nhau và tính đủ Budget của cả hai lượt. Scoped patch chỉ dùng trong benchmark tuần tự và được khôi phục cả khi crash. Không thay policy, dữ liệu hay thước đo. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: đọc trùng làm tăng tool calls và cost mà không cải thiện độ đúng. Đo pass rate, pass^5, seed min–max/variance, cost/success, mean tool calls và mean/p95 trace events bằng lab8.benchmark. trial_pass kiểm ledger/audit/trace và chuỗi cấm. Hai test trong src/tests/test_bonus_investigator_ablation.py kiểm thêm chi phí tăng đúng, quyết định không đổi, retry không ghi trùng, crash được truyền tiếp và runner được khôi phục. Không suy ra chỉ số hidden từ phép thử này. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): chạy trong `src/`: `python -m lab8.benchmark --shapes orchestrator,orchestrator_two --extra-shape orchestrator_two=bonus.investigator_ablation:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_investigators.json`. Kiểm thử: `python -m pytest -q tests/test_bonus_investigator_ablation.py` (2 passed).
- Run id / file report: `src/reports/ablation_investigators.json`, gồm 140 trial (70 mỗi cấu hình). Một cặp cùng claim/seed là `R-orchestrator-C-001-s11` và `R-orchestrator_two-C-001-s11`; run_id của các trial còn lại nằm trong report. Phép so sánh workflow/orchestrator ở `src/reports/ablation_topology.json` được dùng để tham khảo vì hai shape khác cả số lần đọc và cách ghi trace.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: phù hợp hypothesis trong setup public này. Cả hai cấu hình đạt 70/70, pass rate = 1.0, pass^5 = 1.0, seed min–max = 1.0–1.0, variance = 0. Cost/success tăng từ 46.428571 lên 82.857143 VND mô phỏng (+36.428572 VND, +78.46%); tổng cost từ 3250 lên 5800 VND; mean tool calls từ 4.642857 lên 8.285714. Mean trace events đều 3.714286, p95 đều 4: tracer hiện tại ghi một event kết quả investigator, không ghi từng tool call, nên metric steps không biểu diễn đầy đủ phần đọc tăng thêm. Chưa thấy lợi ích độ đúng từ lượt đọc lặp trên corpus này; không kết luận multi-agent nói chung kém hiệu quả.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Hai cấu hình trong phép thử đều không gọi model, nên kết quả chỉ phản ánh chi phí của việc đọc lặp. Investigator thứ hai làm lại cùng công việc theo thứ tự tuần tự; phép thử chưa khảo sát xử lý song song hoặc chuyên môn hóa. Bộ public chỉ có 14 claim và cấu hình gốc đã đạt 100%; năm seed không tạo khác biệt cho luồng đọc cố định. Kết quả chưa được kiểm chứng trên hidden hoặc môi trường thực tế. Số event trace không đại diện cho toàn bộ thao tác, còn chi phí VND là giá mô phỏng.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
