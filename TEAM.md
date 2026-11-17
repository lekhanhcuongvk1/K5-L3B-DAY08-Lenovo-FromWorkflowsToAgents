# Team

## Thông tin nhóm

- Tên nhóm: Lenovo
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Lenovo-FromWorkflowsToAgents`
- URL repo: https://github.com/lekhanhcuongvk1/K5-L3B-DAY08-Lenovo-FromWorkflowsToAgents
- Nhánh nộp, commit chốt: `main`, `7238cf5a42287bbd586f1b3e582adb4c98e235d1` (mốc code và bằng chứng thực nghiệm; các cập nhật hồ sơ sau mốc này không đổi code).

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Mai Danh Hiếu | 2A202603948 | danhhieu123ns@gmail.com | | CP2 — triển khai ba shape workflow, single và orchestrator |
| 2 | Nguyễn Công Tú | 2A202604008 | nguyencongtu5050@gmail.com | nguyencongtu4800 | CP3 — handoff, idempotency, crash/resume |
| 3 | Đặng Quang Duy | 2A202603984 | dqduy0044@gmail.com | dqduy2k4 | CP4 — kiểm tra approval, trace/secret và crash suite |
| 4 | Lê Khánh Cường | 2A202603999 | lekhanhcuongvk1@gmail.com | lekhanhcuongvk1 | CP5 — benchmark, research card, ADR, báo cáo và bonus B4 |

CP1 do cả nhóm cùng thực hiện: cài môi trường, đọc contract và chạy smoke/test. Từ CP2 đến CP5, mỗi người phụ trách một checkpoint. Email được đối chiếu từ báo cáo cá nhân và thông tin tác giả commit; tài khoản GitHub của Mai Danh Hiếu chưa được xác nhận.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Mai Danh Hiếu | CP2 — viết ba shape và xử lý các nhánh nghiệp vụ | `3292faf` — cp2; `8835c40` — cp2 update | Chưa thêm hoặc sửa test theo bằng chứng hiện có; dùng bộ `src/tests/test_public_matrix.py` để kiểm tra ba shape. |
| Nguyễn Công Tú | CP3 — truyền crash_at, ghi trace khi crash, rà handoff chỉ đọc | `f794be2` — add checkpoint 3 | Chưa thêm hoặc sửa test; chạy các test có sẵn `test_t11_retry_keeps_one_refund` và `test_t12_crash_before_checkpoint_does_not_double_pay`. |
| Đặng Quang Duy | CP4 — rà approval/secret và lưu crash report | `46f7a50` — Finish checkpoint 4 | Chưa thêm hoặc sửa test; đối chiếu các test approval, binding theo claim, cap theo order và retry/crash có sẵn. |
| Lê Khánh Cường | CP5 và B4 — benchmark, ablation, thống kê, báo cáo | `372b1f3` — Complete CP5 benchmark, ablation and team reports; `6e56be2` — Complete B4 baselines, ablation and statistical evaluation | Thêm `src/tests/test_bonus_investigator_ablation.py` (2 test) và `src/tests/test_bonus_b4.py` (44 trường hợp sau tham số hóa). |

Ba thành viên phụ trách CP2–CP4 hiện có bằng chứng chạy test nhưng chưa có test do cá nhân thêm hoặc sửa. Yêu cầu đóng góp test của từng người trong rubric vì vậy chưa được đáp ứng đầy đủ; các test chạy lại không được tính thành test mới.

## Cá nhân

| Thành viên | Báo cáo cá nhân |
| --- | --- |
| Mai Danh Hiếu | [2A202603948_MaiDanhHieu.md](report/team/2A202603948_MaiDanhHieu.md) |
| Nguyễn Công Tú | [2A202604008_NguyenCongTu.md](report/team/2A202604008_NguyenCongTu.md) |
| Đặng Quang Duy | [2A202603984_DangQuangDuy.md](report/team/2A202603984_DangQuangDuy.md) |
| Lê Khánh Cường | [2A202603999_LeKhanhCuong.md](report/team/2A202603999_LeKhanhCuong.md) |

## 2A202603948_MaiDanhHieu

### Phần việc phụ trách

- CP2: triển khai workflow, single và orchestrator theo cùng contract `run_claim`/`RunResult`.

### Đóng góp cụ thể

- Thay ba stub bằng luồng xử lý đầy đủ; tính quote từ order, chuyển full quote cho host và trả kết quả qua `finish()`.
- Dùng `run_react` giới hạn tám bước cho single và handoff read-only cho orchestrator; tạo trace cho các nhánh trả về.

### Bằng chứng

- Commit `3292faf`, `8835c40`; ba file trong `src/lab8/shapes/`.
- Student matrix và báo cáo [CP2](report/team/2A202603948_MaiDanhHieu.md).

## 2A202604008_NguyenCongTu

### Phần việc phụ trách

- CP3: bảo đảm retry/crash không tạo thêm refund và handoff không chuyển secret sang investigator.

### Đóng góp cụ thể

- Bổ sung xử lý `InjectedCrash`: ghi trace rồi ném lại lỗi; truyền `crash_at` đến host trong cả ba shape.
- Làm rõ ranh giới handoff allowlist, tool chỉ đọc và cơ chế resume dựa trên ledger.

### Bằng chứng

- Commit `f794be2`; T11/T12 trong `src/tests/test_public_matrix.py`.
- Báo cáo [CP3](report/team/2A202604008_NguyenCongTu.md).

## 2A202603984_DangQuangDuy

### Phần việc phụ trách

- CP4: kiểm tra approval, trần hoàn tiền theo đơn, trace/secret và crash safety.

### Đóng góp cụ thể

- Chạy crash suite và lưu `src/reports/crash.json` với kết quả 20/20.
- Rà approval sai claim/hết hạn, cap theo order, trace và việc truyền crash trong các shape.

### Bằng chứng

- Commit `46f7a50`; các scenario `CR-01`–`CR-20` trong crash report.
- Báo cáo [CP4](report/team/2A202603984_DangQuangDuy.md).

## 2A202603999_LeKhanhCuong

### Phần việc phụ trách

- CP5: so sánh bốn shape, thực hiện ablation, viết ADR/research card và tổng hợp báo cáo; mở rộng bonus B4.

### Đóng góp cụ thể

- Chạy benchmark bốn shape trên cùng corpus/seed và chọn workflow theo số liệu public.
- Thực hiện ablation investigator; bổ sung baseline rules-only, swarm pruned, ablation workflow và thống kê bootstrap/McNemar/sign test cho B4.
- Thêm test kiểm chứng, tổng hợp báo cáo và chạy hidden self-check không có nhãn.

### Bằng chứng

- Commit `372b1f3`, `6e56be2`; `src/reports/benchmark.json`, `ablation_investigators.json`, `bonus_ablation.json`.
- Hai file test bonus, các report hidden self-check và báo cáo [CP5](report/team/2A202603999_LeKhanhCuong.md).
