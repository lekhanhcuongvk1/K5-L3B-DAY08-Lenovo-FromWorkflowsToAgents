# Báo cáo cá nhân — Mai Danh Hiếu

## 1. Thông tin thành viên

- Họ tên: Mai Danh Hiếu
- MSSV: 2A202603948
- Email: 
- GitHub: 

## 2. Phần việc phụ trách

CP2 — triển khai ba shape `workflow`, `single` và `orchestrator` cho luồng xử lý claim, cùng chữ ký `run_claim` và kiểu kết quả `RunResult`. Phạm vi này gồm quyết định trạng thái, tính quote từ dữ liệu đơn hàng, gọi host để ghi refund và tạo trace cho mọi nhánh trả về.

## 3. Đóng góp cụ thể

- Commit [`3292faf`](https://github.com/lekhanhcuongvk1/K5-L3B-DAY08-Lenovo-FromWorkflowsToAgents/commit/3292faf224da5a6a9d528efd585ecc94c0d9e8cd) (`cp2`, tác giả Mai Danh Hieu) thay các stub trong cả ba file shape.
- `workflow.py`: xử lý theo thứ tự cố định: đọc claim, kiểm tra `order_id`, tra cứu đơn hàng theo quyền truy cập, tính quote bằng `compute_compensation`, rồi gọi `issue_refund` khi quote dương.
- `single.py`: dùng `run_react` với giới hạn 8 bước; agent chọn các công cụ đọc và trả quote, còn việc ghi refund nằm ngoài vòng lặp tại host. Các lần quyết định được tính vào `Budget`.
- `orchestrator.py`: tạo handoff bằng `make_handoff` với danh sách công cụ chỉ đọc, chạy investigator, rồi orchestrator dùng kết quả để quyết định và gọi host. Trace ghi handoff đã qua `safe_dump`.
- Cả ba shape trả kết quả qua `finish()`, ghi sự kiện `decision` trước mỗi lần return, xử lý `needs_info`, `escalated`, `denied`, `failed`, `resolved`; truyền quote đầy đủ cho host để host kiểm tra approval và trần refund theo đơn.
- Commit này không thêm hoặc sửa test. Việc xác nhận dùng bộ test student có sẵn trong `src/tests/`.

## 4. Bằng chứng

- Mã nguồn: [`workflow.py`](../../src/lab8/shapes/workflow.py), [`single.py`](../../src/lab8/shapes/single.py), [`orchestrator.py`](../../src/lab8/shapes/orchestrator.py).
- Chạy tại `src/`: `python -m pytest -q -m student -o addopts=` → **248 passed, 54 deselected**. Bộ student gồm 62 ca cho mỗi shape; như vậy ba shape phụ trách đều đạt 62/62 ca public.
- Các test liên quan nằm trong `src/tests/test_public_matrix.py`, `src/tests/test_trace_contract.py`, `src/tests/test_order_cap_and_approval_binding.py` và `src/tests/test_authorization.py`.

## 5. Công cụ AI đã dùng

- Codex hỗ trợ đọc mã nguồn, đối chiếu commit với yêu cầu CP2, chạy lại bộ test và soạn báo cáo này. Tôi kiểm tra kết quả bằng `git show 3292faf`, đọc ba file shape và chạy lệnh pytest nêu trên. Repo không ghi nhận liệu AI có được dùng khi viết commit CP2 hay không.

## 6. Tự đánh giá

Phần CP2 đã có đủ ba shape chạy được và qua toàn bộ 62 test student cho mỗi shape. Bằng chứng hiện có là bộ public; báo cáo này không khẳng định kết quả trên hidden grader. Chưa có test mới do cá nhân thêm trong commit CP2.
