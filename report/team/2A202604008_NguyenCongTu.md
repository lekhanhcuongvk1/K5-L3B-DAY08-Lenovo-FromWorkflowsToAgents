# Báo cáo cá nhân — 2A202604008_NguyenCongTu

## 1. Thông tin thành viên

- Họ tên: Nguyễn Công Tú
- MSSV: 2A202604008
- Email: nguyencongtu5050@gmail.com
- GitHub: nguyencongtu4800

## 2. Phần việc phụ trách

 **CP3 — Handoff, ledger, crash**: làm cho bước ghi tiền an toàn khi một claim được gọi lại hoặc khi tiến trình crash giữa chừng, và bảo đảm handoff sang investigator không mang secret qua ranh giới.

Phạm vi cụ thể:

- **Module:** các dòng `TODO CP3` trong cả ba shape nhóm viết: `src/lab8/shapes/workflow.py`, `src/lab8/shapes/single.py`, `src/lab8/shapes/orchestrator.py`.
- **Ledger và crash/resume (cả ba shape):** truyền `crash_at` vào `durability.issue_refund` để host có thể tiêm lỗi đúng điểm, và không nuốt `InjectedCrash`. Khi crash, shape ghi sự kiện `crash` vào trace, ghi trace ra file rồi ném lại exception. Lần resume dựa vào dòng ledger có idempotency key `refund:{claim_id}` nên chỉ replay, không tạo refund thứ hai.
- **Handoff an toàn (orchestrator):** handoff dựng bằng `lab8.handoff.make_handoff`, tức allowlist trong code chứ không dùng LLM tóm tắt. `facts={}` để không có parent context nào đi qua ranh giới, investigator chỉ có tool đọc, và trace chỉ ghi handoff đã sanitize chứ không ghi claim row thô.


## 3. Đóng góp cụ thể

**Commit chính:** `f794be2` (add checkpoint 3), sửa 3 file `workflow.py`, `single.py`, `orchestrator.py`

**Test:** không thêm hay sửa test. Mình dùng các test có sẵn trong `src/tests/test_public_matrix.py`:

- `test_t11_retry_keeps_one_refund[workflow|single|orchestrator]`: gọi lại cùng claim vẫn chỉ có một dòng ledger.
- `test_t12_crash_before_checkpoint_does_not_double_pay[workflow|single|orchestrator]`: crash rồi resume vẫn chỉ một refund.

Kết quả chạy lại ngày 2026-11-17: `python -m pytest -q -m student -o addopts= -k "T11 or T12"` cho **8 passed** (3 shape nhóm viết + swarm, mỗi shape 2 test)
## 4. Bằng chứng

**Commit:** [`f794be2` — add checkpoint 3](https://github.com/lekhanhcuongvk1/K5-L3B-DAY08-Lenovo-FromWorkflowsToAgents/commit/f794be2466e4af7419285d9ce30894ee5a83c31f)

**Test (chạy lại ngày 2026-11-17):**

```text
$ python -m pytest -q -m student -o addopts= -k "T11 or T12"
test_t11_retry_keeps_one_refund[workflow|single|orchestrator|swarm]
test_t12_crash_before_checkpoint_does_not_double_pay[workflow|single|orchestrator|swarm]
8 passed, 296 deselected
```


## 5. Công cụ AI đã dùng

| Công cụ | Dùng vào việc gì | Cách tự kiểm tra |
|---|---|---|
| Claude Code (Claude Opus 5.5, trong VS Code) | Soạn nháp phần 2–6 của báo cáo cá nhân này (phần 6 viết theo yêu cầu của mình, chỉ dựa trên dữ kiện kiểm chứng được, mình đã đọc lại và chịu trách nhiệm nội dung) từ diff commit `f794be2`, `CHECKPOINTS.md` và `RUBRIC.md`; chạy lại test và đọc `crash.json`, trace để lấy số liệu cho phần 4 | Đối chiếu từng ý với diff thật của commit; số liệu test (8 passed, 304 passed), 

## 6. Tự đánh giá

**Kết quả đạt được so với yêu cầu CP3:** T11, T12 xanh trên cả ba shape; cổng host 304 passed; crash suite 20/20.

**Điểm làm tốt:** Phần việc hoàn thành đúng phạm vi CP3: , giống nhau ở cả ba shape nên dễ review, và không đụng các file bị cấm sửa (`durability.py`, `metrics.py`…). Mình hiểu được vì sao an toàn khi ghi tiền nằm ở ledger của host chứ không nằm ở checkpoint trong shape, và vì sao handoff phải dùng allowlist.

**Điểm còn hạn chế:**

- Phần CP3 chủ yếu nối đúng vào cơ chế host đã có sẵn (`issue_refund`, `make_handoff`), nên phần thiết kế mình tự làm không nhiều.
- Mình không viết thêm test nào, chỉ dựa vào T11/T12 có sẵn.




