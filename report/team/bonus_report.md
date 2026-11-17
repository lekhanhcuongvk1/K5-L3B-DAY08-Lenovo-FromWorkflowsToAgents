# Bonus report: B4

- Topic + nguồn (tên, năm, slide): B4 — Baseline công bằng, ablation và thống kê. Zhang và cộng sự, *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026, slide 44/59; [nguồn sơ cấp](https://aclanthology.org/2026.emnlp-main.798/). Tham khảo thêm AgentArch, AACL 2026, slide 43: https://arxiv.org/abs/2509.10769v2.
- CLAIM của nguồn (1 câu): Mức cải thiện được báo cáo có thể phụ thuộc thiết lập đánh giá, khi baseline đơn giản hoặc pruning ngẫu nhiên đã giữ được hiệu năng; vì vậy cần cố định model, registry và runtime khi so sánh.
- BOUNDARY (model / dataset / setup): Nguồn nghiên cứu các cấu trúc MAS trong benchmark riêng; phép thử LogiX dưới đây chỉ kiểm tra nhận định đó trên dữ liệu giả lập và MockLLM, không tái lập toàn bộ nghiên cứu.
- HYPOTHESIS trên LogiX: Rules-only giữ độ đúng của workflow; pruning peer/parse giảm chi phí nhưng có thể giữ lỗi tin ticket; bỏ kiểm tra thiếu order_id làm sai trạng thái cần bổ sung thông tin. Giả thuyết được đặt sau khi đã xem benchmark CP5.
- Biến cố định / biến thay đổi: Cùng 14 claim, năm seed 11/22/33/44/55, as_of 2026-11-15, backend, pricing, tool registry và evaluator; mỗi trial dùng DB mới. Rules-only là bản tái hiện workflow không gọi model, không phải một hệ thống độc lập. Swarm pruned giữ mỗi peer/parse call với xác suất thiết kế 50%, quyết định bằng SHA-256 của seed/claim/purpose; bỏ parse đồng thời bỏ việc đọc số ngày trong ticket. Ablation workflow chỉ bỏ nhánh trả needs_info khi thiếu order_id. Các cổng host không đổi.
- Lệnh tái lập (copy-paste được): Trong `src/`, chạy `python -m bonus.run_b4 --out reports/bonus_ablation.json`. Kiểm thử: `python -m pytest -q tests/test_bonus_b4.py`.
- File report + run id: `src/reports/bonus_ablation.json` gồm 490 trial và safety scan từng trial. Ví dụ: `R-rules_only-C-001-s11`, `R-swarm_pruned-C-002-s55`, `R-workflow_no_order_check-C-004-s11`. Runner đăng ký ba variant bằng `register_extra_shapes`, cùng cơ chế với cờ `--extra-shape`.

## Kết quả

Số liệu dưới đây lấy từ `by_shape`, `statistics`, `paired_comparisons` và `safety` trong report. CI 95% dùng 10.000 lần bootstrap theo claim, giữ cả năm seed trong mỗi cụm; seed thống kê là 20261117.

| Shape | Pass rate | Pass^5 | Variance | CI 95% pass rate | Cost/success (VND mô phỏng) |
| --- | ---: | ---: | ---: | --- | ---: |
| workflow | 1.0000 | 1.0000 | 0 | [1.0000; 1.0000] | 27.86 |
| single | 1.0000 | 1.0000 | 0 | [1.0000; 1.0000] | 28.78 |
| orchestrator | 1.0000 | 1.0000 | 0 | [1.0000; 1.0000] | 46.43 |
| swarm | 0.9857 | 0.9286 | 0.000816 | [0.9571; 1.0000] | 49.57 |
| rules_only | 1.0000 | 1.0000 | 0 | [1.0000; 1.0000] | 27.86 |
| swarm_pruned | 0.9857 | 0.9286 | 0.000816 | [0.9571; 1.0000] | 48.84 |
| workflow_no_order_check | 0.9286 | 0.9286 | 0 | [0.7857; 1.0000] | 30.77 |

| Cặp so sánh | Cặp chỉ bên trái/phải pass | p McNemar exact | p sign test theo claim |
| --- | --- | ---: | ---: |
| workflow / swarm | 1 / 0 | 1.0000 | 1.0000 |
| swarm / swarm_pruned | 0 / 0 | 1.0000 | 1.0000 |
| workflow / rules_only | 0 / 0 | 1.0000 | 1.0000 |
| workflow / workflow_no_order_check | 5 / 0 | 0.0625 | 1.0000 |

Cả bảy cấu hình đều được quét đủ 70/70 trial, không ghi nhận secret leak, PII leak, approval bypass, trace sai hoặc ledger ngoài phạm vi. Đây là số đếm public của scanner bổ sung, không thay số đo hidden chính thức. Test kiểm scanner có phát hiện leak/bypass được chủ động tạo; các variant còn được kiểm crash/resume tại ba điểm và retry không ghi trùng.

## Kết luận

Kết quả ủng hộ việc giữ baseline đơn giản: rules-only có cùng độ đúng và chi phí với workflow. Pruning giảm model calls trung bình từ 3 xuống 1.93, nhưng chỉ giảm cost/success 1.46% vì tool calls chiếm phần lớn chi phí. Độ đúng không đổi, kể cả lỗi C-002 ở seed 55: mask đã cố định vẫn giữ parse ở trial này. Nhóm không chọn lại mask để làm kết quả đẹp hơn.

Workflow vốn không có model call hay investigator để cắt giảm. Bỏ nhánh kiểm thiếu order_id làm C-004 chuyển từ needs_info sang escalated ở cả năm seed và phát sinh một lần lookup thừa. Thành phần này cần giữ. Ngược lại, các peer/parse call bị pruning chưa làm thay đổi pass rate trong mẫu đang xét; điều đó chưa chứng minh chúng luôn vô ích.

Ở mức 0.05, chưa có bằng chứng thống kê cho chênh lệch độ đúng workflow–swarm. Năm lỗi của ablation cùng thuộc một claim; sign test theo claim cho thấy không nên xem đó là năm bằng chứng độc lập. Nhóm giữ workflow vì chi phí và kết quả quan sát được, không tuyên bố đã chứng minh nó vượt trội trên mọi tác vụ. Quyết định có thể đổi khi bộ claim rộng hơn cho thấy lợi ích ổn định từ suy luận hoặc phối hợp agent.

## Giới hạn

Tự kiểm bổ sung trên 40 claim không nhãn, năm seed và năm cấu hình được lưu tại `src/reports/bonus_hidden_selfcheck.json`: mỗi cấu hình chạy đủ 200 trial, không có lỗi chạy, lỗi contract trace hoặc leak suspect. Vì không có nhãn, kết quả này chưa xác nhận pass rate hay safety counts chính thức trên hidden.

MockLLM không phải model thật; latency là `unavailable`, cost là mô phỏng. Dữ liệu public đã dùng để phát triển code, chỉ có 14 claim và một mask pruning cố định. CI [1;1] xuất hiện vì mẫu bootstrap không có lỗi, không bảo đảm đúng tuyệt đối ngoài mẫu. Trace của swarm pruned có thêm event ghi mask nên steps tăng không đồng nghĩa xử lý nhiều hơn. Bonus vẫn chờ xác nhận gate hidden ≥ 0.80, safety và crash của shape chọn từ quy trình chấm chính thức.
