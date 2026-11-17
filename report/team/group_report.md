# Báo cáo nhóm — Lab 8 LogiX-VN

Số liệu trong báo cáo được tổng hợp từ các file kết quả trong `src/reports/`.

## 1. Thông tin nhóm

- Tên nhóm: Lenovo
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm xây dựng quy trình xử lý claim hoàn tiền cho LogiX-VN theo ba kiến trúc và so sánh với swarm có sẵn. Mục tiêu là xử lý đúng luật nghiệp vụ, giữ an toàn khi ghi tiền và chọn mức tự chủ phù hợp bằng số liệu. Ticket có thể chứa thông tin sai hoặc yêu cầu bỏ qua policy, nên quyết định tiền phải dựa vào order, policy và approval có cấu trúc.

Nhóm có bốn người, mỗi người chịu trách nhiệm một checkpoint từ CP2 đến CP5. CP1 là phần chung: mọi người tự cài môi trường, chạy smoke và đọc contract. Người phụ trách CP2 triển khai ba shape; CP3 hoàn thiện handoff, retry và crash/resume; CP4 kiểm tra approval, secret và crash suite; CP5 chạy benchmark, làm ablation và tổng hợp báo cáo. Các phần có quan hệ bàn giao: CP3–CP4 kiểm tra trên code CP2, còn số liệu CP5 được lấy sau khi các shape đã qua student matrix. Swarm được giữ làm đối chứng theo đề.

## 3. Giải pháp

Workflow đọc claim qua `get_claim_view`, kiểm tra `order_id`, rồi lấy order trong phạm vi principal được phép truy cập. Thiếu mã đơn thì trả `needs_info`; không thấy đơn hoặc không có quyền thì trả `escalated`. Khi có order hợp lệ, code gọi `compute_compensation`. Quote bằng 0 dẫn tới `denied`; quote dương được chuyển nguyên vẹn cho `issue_refund`. Luồng này không gọi model.

Single dùng `run_react` với giới hạn tám bước. Hàm `decide` gọi MockLLM và ghi nhận usage trong Budget, nhưng thứ tự chọn tool trong bản triển khai hiện tại vẫn được điều khiển bằng biến phase trong Python: đọc order, tính compensation rồi trả quote. Vì vậy đây là vòng ReAct được ràng buộc chặt, chưa phải agent tự lập kế hoạch dựa trên nội dung model trả về. Model không tính tiền, tạo approval hay ghi refund.

Orchestrator tạo handoff qua `make_handoff`, dùng `facts={}` và chỉ cấp `lookup_order`, `lookup_policy`, `compute_compensation`. Investigator đọc dữ liệu rồi trả kết quả; orchestrator lấy quote và gọi host. Handoff được lọc bằng allowlist trong code, không chuyển nguyên parent context và không cấp tool ghi. Trace ghi handoff đã sanitize và order view đã qua read tool.

Cả ba shape đều truyền full quote cho host. Nếu đơn từng được hoàn tiền, host tự tính phần còn được nhận trong transaction; shape không trừ trước để tránh trừ hai lần. Host cũng kiểm approval có thuộc đúng claim hay không, cap số tiền và chống ghi trùng bằng khóa `refund:{claim_id}`. Quote dương bị host từ chối vẫn được giữ trong `proposal_amount`, đồng thời host ghi audit `policy_denied`.

Tham số `crash_at` được chuyển tới host. Shape ghi event crash rồi ném lại `InjectedCrash`, cho phép test xác nhận crash thực sự xảy ra. Khi chạy lại trên cùng DB, ledger quyết định effect đã tồn tại; checkpoint không được dùng như bằng chứng duy nhất để tránh trả hai lần. Kết quả được tạo qua `finish()` để effect và số audit khớp ledger.

Trace ghi quyền truy cập order, quote và quyết định cuối; orchestrator có thêm event handoff/investigator. Các nhánh return sớm cũng tạo trace mới. Nhóm không ghi nguyên claim row, ticket, parent secret, header, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ. Đây là phần dữ liệu không cần cho việc giải thích số tiền và có nguy cơ lộ khi chia sẻ trace.

## 4. Kết quả

Benchmark dùng cùng 14 claim public, seed `11,22,33,44,55`, policy tại `2026-11-15`, bảng giá và evaluator chính thức. Mỗi trial có một SQLite mới. Các giá trị dưới đây lấy từ `src/reports/benchmark.json` (280 trial), được làm tròn khi trình bày.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1.000000 | 1.000000 | 1.000000–1.000000 | 0 | 27.86 | 2.79 / 3 |
| single | 1.000000 | 1.000000 | 1.000000–1.000000 | 0 | 28.78 | 2.79 / 3 |
| orchestrator | 1.000000 | 1.000000 | 1.000000–1.000000 | 0 | 46.43 | 3.71 / 4 |
| swarm | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.000816 | 49.57 | 2.80 / 3 |

Ba shape nhóm viết đều đạt 70/70 trial. Swarm đạt 69/70; trial `R-swarm-C-002-s55` trả `resolved` trong khi nhãn yêu cầu `denied`. Đây là điểm yếu có chủ đích của đối chứng: seed 55 khiến swarm lấy số ngày trong ticket thay cho order. Student matrix kiểm đúng sự khác biệt này, nên 248 test student pass không có nghĩa swarm đạt 100% benchmark.

`src/reports/crash.json` ghi nhận crash safety 20/20. Suite này kiểm host và swarm tham chiếu; retry và crash/resume của ba shape được kiểm thêm qua T11/T12 trong student matrix. Lần kiểm tra gần nhất có 56 host tests pass, gồm hai test mới cho ablation; student matrix trước khi thêm variant có 248 passed. Chưa có kết quả hidden chính thức hoặc self-check trên `student_drop/` để báo cáo.

Ablation R3 bật thêm lượt investigator read-only thứ hai, cùng handoff và cùng tool, chạy tuần tự trước khi ghi tiền. Kết quả trong `src/reports/ablation_investigators.json` cho thấy cả cấu hình gốc và variant đều đạt 70/70. Cost/success tăng từ 46.43 lên 82.86 VND mô phỏng (+78.46%); mean tool calls tăng từ 4.64 lên 8.29. Mean/p95 trace events không đổi vì tracer ghi kết quả investigator ở mức tổng hợp. Vì vậy cần đọc thêm tool calls để thấy công việc tăng lên. Giả thuyết được hình thành sau khi xem benchmark bốn shape, nên đây là phân tích khám phá, không phải dự đoán đăng ký trước.

Nhóm chọn workflow: cùng độ đúng public với single và orchestrator nhưng ít chi phí hơn, đồng thời dễ theo dõi đường đi của quyết định. Ablation chưa cho thấy lợi ích từ việc đọc lặp cùng dữ liệu. Lựa chọn sẽ được xem lại nếu tác vụ mới cần nguồn thông tin độc lập hoặc chuyên môn hóa và phép đo cho thấy lợi ích đủ rõ.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Khi chạy benchmark, terminal đã đứng trong `src/` nhưng tiếp tục chạy `cd src`, dẫn tới lỗi `Cannot find path '...\src\src' because it does not exist`. Cách xử lý là giữ nguyên thư mục hiện tại và chạy trực tiếp `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`. Lệnh hoàn tất và tạo report đúng vị trí.

Khi thiết kế ablation, so sánh workflow với orchestrator chưa đủ để quy mọi chênh lệch cho topology: hai shape khác cả số lần đọc và cách ghi trace. Nhóm vẫn lưu đối chiếu đó ở `src/reports/ablation_topology.json`, nhưng dùng phép bật/tắt lượt investigator thứ hai làm ablation chính. Variant dùng lại orchestrator, tính đầy đủ Budget và khôi phục runner sau khi chạy hoặc crash; hai test bổ sung đều pass.

Một điểm cần chú ý khi đọc kết quả là số bước trong trace không tăng cùng số lần gọi tool. Qua đối chiếu code và Budget, nhóm xác định tracer đang ghi một event tổng hợp cho kết quả investigator. Vì vậy nhóm báo cáo cả số event và số tool calls, tránh diễn giải số bước thành toàn bộ khối lượng xử lý.

## 6. Tổng hợp đóng góp

Nhóm chia công việc theo checkpoint. CP1 do cả bốn người cùng thực hiện; từ CP2 đến CP5, mỗi người phụ trách một phần và bàn giao kết quả cho checkpoint sau.

| Checkpoint | Thành viên phụ trách | Công việc và đầu ra |
| --- | --- | --- |
| CP1 | Cả nhóm | Tự cài môi trường, chạy smoke/test và đọc contract trước khi làm phần riêng. |
| CP2 | | Triển khai workflow, single, orchestrator; bảo đảm RunResult và các nhánh nghiệp vụ đúng contract. |
| CP3 | | Hoàn thiện handoff read-only, truyền crash_at, kiểm retry và crash/resume trên các shape. |
| CP4 | | Rà approval, cap theo order, trace/secret; chạy crash suite và lưu crash.json. |
| CP5 | | Chạy benchmark, thực hiện ablation, thêm test kiểm chứng, tổng hợp research card, ADR và báo cáo nhóm. |

Nguồn đối chiếu đóng góp cá nhân là lịch sử commit, các test đã thêm hoặc sửa và kết quả chạy của từng checkpoint.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable` và cost chỉ là mô phỏng. Workflow cùng orchestrator không gọi model, còn single chọn tool bằng phase cố định. Kết quả hiện tại vì thế phản ánh cách triển khai trong lab, chưa đánh giá đầy đủ khả năng tự lập kế hoạch hoặc phối hợp giữa các model thật.

Public chỉ có 14 claim và đã được dùng để phát triển code. Pass 100% không bảo đảm shape chọn đạt ngưỡng hidden 0.75 trên 200 trial; các chỉ số leak/bypass hidden cũng chưa được xác nhận. Ablation lặp cùng công việc đọc tuần tự, không đo lợi ích từ chuyên môn hóa hay chạy song song. Số steps đếm event trace, không phải toàn bộ tool calls hoặc thời gian chạy.

Để đánh giá chắc chắn hơn, nhóm cần đối chiếu thêm kết quả hidden từ giảng viên. Nếu mở rộng bài toán, hướng thử tiếp theo là bổ sung case ngoài public và cho investigator xử lý các nhiệm vụ hoặc nguồn dữ liệu khác nhau. Nhóm chỉ cân nhắc tăng mức tự chủ khi phép đo cho thấy lợi ích rõ ràng và hệ thống vẫn đáp ứng yêu cầu về approval, bảo mật và crash safety.

## 8. Tài liệu tham khảo

1. Tài liệu lab: `README.md`, `CHECKPOINTS.md`, `RULES.md`, `RUBRIC.md`, `SUBMISSION.md`.
2. Contract và nghiệp vụ: `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
3. Bằng chứng thực nghiệm: `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/ablation_investigators.json`; test trong `src/tests/`.
4. Bogavelli, Sharma và Subramani. *AgentArch: A Comprehensive Benchmark to Evaluate Agent Architectures in Enterprise*. arXiv v2, 2026 (bản đầu 2025). https://arxiv.org/abs/2509.10769v2. Claim và phạm vi sử dụng được nêu trong `research_card.md`; không coi paper là bằng chứng trực tiếp cho kết quả LogiX-VN.
