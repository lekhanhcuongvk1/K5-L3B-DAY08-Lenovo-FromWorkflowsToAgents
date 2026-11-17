# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash:
- Run id dẫn chứng: R-workflow-C-001-s11; đối chiếu R-single-C-001-s11, R-orchestrator-C-001-s11 và trial lỗi R-swarm-C-002-s55 trong src/reports/benchmark.json. Ablation: R-orchestrator-C-001-s11 và R-orchestrator_two-C-001-s11 trong src/reports/ablation_investigators.json.
- Pass rate / pass^5 / seed min-max / variance: workflow = 1.0 / 1.0 / 1.0–1.0 / 0.0; 70/70 trial trên 14 claim public × seed 11,22,33,44,55 (src/reports/benchmark.json).
- Cost per success (mô phỏng, VND): workflow = 27.857143; single = 28.780000; orchestrator = 46.428571; swarm = 49.566957 (src/reports/benchmark.json).
- Crash safety: 20/20 (src/reports/crash.json, suite của host và swarm tham chiếu); workflow qua thêm T11 retry và T12 crash/resume trong student matrix.
- Secret leak / approval bypass: chưa thấy vi phạm trên các trial workflow public được trial_pass chấm đạt và các test host/student đã chạy; chưa có chỉ số secret_leak_count hoặc approval_bypass_count chính thức trên hidden, chờ grader giảng viên xác nhận.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm chọn workflow cho bài toán hiện tại. Trên cùng 14 claim public và năm seed, workflow, single và orchestrator đều đạt 70/70 trial, pass^5 bằng 1.0 và variance bằng 0. Điểm khác biệt nằm ở chi phí: workflow tốn khoảng 27.86 VND mô phỏng cho một lần thành công, thấp hơn single (28.78) và orchestrator (46.43). Swarm đạt 69/70 trial, với một quyết định hoàn tiền sai ở C-002, seed 55. Với một quy trình có luật tính tiền rõ và nguồn dữ liệu có cấu trúc, nhóm chưa thấy lý do để thêm quyền tự chủ khi luồng Python cố định đã xử lý đúng các trường hợp public. Workflow hiện không cần gọi model; phần approval, trần tiền và ghi ledger vẫn đi qua host. Lựa chọn này dựa trên benchmark chung trong `src/reports/benchmark.json`, không dựa vào một claim chạy riêng.

## Có đáng đổi lấy multi-agent không

Ở kết quả hiện tại, nhóm giữ workflow. Orchestrator chưa cải thiện độ đúng trên public nhưng cost/success cao hơn workflow khoảng 66.67%. Phép thử thêm một lượt investigator giống hệt trong `src/reports/ablation_investigators.json` cũng cho cùng 70/70 trial pass, trong khi cost/success tăng từ 46.43 lên 82.86 VND mô phỏng (+78.46%). Kết quả này cho thấy đọc lặp cùng dữ liệu chưa mang lại lợi ích trong setup đang dùng; nó không chứng minh mọi cách phối hợp nhiều agent đều không có ích.

Nhóm sẽ cân nhắc đổi nếu xuất hiện tác vụ cần chuyên môn khác nhau hoặc nguồn thông tin độc lập mà workflow xử lý kém, và phép đo trên cùng corpus/seed cho thấy kiến trúc mới cải thiện độ đúng ổn định, với chi phí chấp nhận được. Trước khi đổi vẫn phải qua các cổng approval, secret và crash. Nếu chênh lệch chỉ xuất hiện ở một vài trial, nhóm cần xem lỗi cụ thể và mở rộng bộ đánh giá trước khi kết luận.

## Trace và bằng chứng

Trong workflow, trace ghi kết quả `lookup_order` ở mức quyền truy cập (`visible`, `reason`), `quote`, quyết định cuối (`status`, `proposal_amount`, `reason`) và điểm crash khi được chủ động inject. Nhánh thiếu thông tin hoặc claim không tồn tại cũng đi qua `finish()` để có trace mới. `finish()` lấy refund effect và số audit committed từ ledger, thay vì để shape tự khai. Orchestrator có thêm handoff đã qua allowlist và kết quả investigator từ các read tool.

Nhóm cố ý không ghi nguyên claim row, ticket, `parent_secret`, raw headers, số điện thoại, địa chỉ, tên hàng hoặc ghi chú nội bộ. Các dữ liệu đó không cần để giải thích quyết định tiền và có thể làm lộ thông tin khi trace được chia sẻ. Claim và order được đọc qua view/tool có giới hạn; handoff dùng `make_handoff`, không dùng lời tóm tắt của model để thay cho lọc field.

Trace nằm trong thư mục `traces/`, có tên theo run_id và được `RunResult.trace_path` trỏ tới. Scanner của evaluator kiểm tra trace cùng các file có tiền tố run_id trong cùng thư mục. Chưa có bằng chứng để khẳng định mọi log ở ngoài phạm vi đó đều sạch; nếu phát sinh file debug hoặc stdout mới, nhóm phải rà riêng và đưa output về phạm vi có thể kiểm tra. Trace và SQLite không được commit. Số bước trong benchmark là số event trace: workflow có mean 2.785714, p95 3; đây không phải thời gian chạy. Trong ablation, số event không tăng dù tool calls tăng vì tracer ghi kết quả investigator ở mức tổng hợp, nên nhóm dùng thêm Budget/tool calls để giải thích chi phí.

## Giới hạn

Kết quả mới bao phủ 14 claim public và năm seed, chưa chứng minh workflow đạt ngưỡng hidden 0.75 trên 200 trial. Các case public đã có nhãn nên nhóm cũng không xem chúng như một tập đánh giá hoàn toàn mới. Workflow và orchestrator trong bản triển khai này không gọi model; variance bằng 0 chủ yếu phản ánh luồng deterministic, không phải độ ổn định của model thật.

MockLLM không phải model sản xuất; latency giữ là `unavailable`. Chi phí VND trong báo cáo là giá mô phỏng, không phải hóa đơn API. Ablation chạy hai lượt investigator tuần tự trên cùng dữ liệu, chưa khảo sát chuyên môn hóa, nguồn thông tin độc lập hoặc thực thi song song. Kết luận hiện chỉ dựa trên kết quả public và chưa được đối chiếu với số đo hidden chính thức.
