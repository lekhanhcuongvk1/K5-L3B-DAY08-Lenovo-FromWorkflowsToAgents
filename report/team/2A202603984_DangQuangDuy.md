# Báo cáo cá nhân — Đặng Quang Duy

## 1. Thông tin thành viên

- Họ tên: Đặng Quang Duy
- MSSV: 2A202603984
- Email: dqduy0044@gmail.com
- GitHub: dqduy2k4

## 2. Phần việc phụ trách

Phụ trách Checkpoint 4: kiểm tra độ bền khi crash, các trường hợp approval không hợp lệ hoặc không thuộc claim, giới hạn hoàn tiền theo đơn, và ranh giới dữ liệu nhạy cảm trong trace/stdout.

## 3. Đóng góp cụ thể

- Chạy crash suite 20 tình huống và lưu kết quả do `lab8.crash_test` sinh tại `src/reports/crash.json`.
- Rà các luồng ghi tiền: approval phải hợp lệ và thuộc đúng claim; khi quote dương bị host từ chối thì không được tạo refund; khoản hoàn trước đó trên cùng order phải được tính vào giới hạn.
- Rà trace của ba shape để tránh ghi nguyên claim row/order row, secret, header, thông tin liên hệ, tên hàng hoặc ghi chú nội bộ. Khi crash, shape ghi event crash rồi để `InjectedCrash` truyền lên để kiểm tra được điểm crash.
- Không thêm hoặc sửa test trong commit CP4; dùng các test hiện có về approval, binding theo claim, T11 retry và T12 crash/resume làm ma trận đối chiếu.
- Quyết định kỹ thuật: ledger và audit của refund phải do host ghi trong transaction; checkpoint chỉ hỗ trợ resume, không thay thế ledger hoặc idempotency.

## 4. Bằng chứng

- Commit CP4: `46f7a50910efa673855c0dcd2c49d067ac057e89` (`Finish checkpoint 4`), tác giả Git `dqduy2k4 <dqduy0044@gmail.com>`.
- `src/reports/crash.json`: 20/20 tình huống đạt, `crash_safety` = `20/20`; gồm crash trước effect, sau effect trước checkpoint, sau checkpoint, retry sai số tiền, thiếu approval và crash/resume của swarm tham chiếu.
- Test đối chiếu có sẵn: `test_missing_or_expired_approval_writes_no_refund`, `test_approval_issued_for_another_claim_is_rejected`, `test_seeded_prior_refund_blocks_t13_and_tops_up_t14`, `test_t11_retry_keeps_one_refund`, `test_t12_crash_before_checkpoint_does_not_double_pay`.
- Không có run ID riêng cho crash suite; bằng chứng là report JSON với các scenario `CR-01`–`CR-20`.

## 5. Công cụ AI đã dùng

Dùng ChatGPT/Codex để rà hướng dẫn CP4, đối chiếu các shape và test hiện có, và hoàn thiện báo cáo cá nhân. Tôi tự đối chiếu kết luận với `src/reports/crash.json`, mã nguồn shape, host authorization/ledger và các test nêu ở mục 4; không tạo số liệu hoặc run ID.

## 6. Tự đánh giá

Checkpoint 4 có bằng chứng crash suite đạt 20/20 và đã rà các ranh giới approval, idempotency và dữ liệu nhạy cảm theo contract. Điểm cần cải thiện là commit CP4 không bổ sung test mới; phần kiểm tra approval và trace dựa trên test có sẵn và việc rà mã. Khi tiếp tục, nên lưu output của các lệnh pytest theo từng checkpoint và bổ sung test hồi quy nếu phát hiện nhánh chưa được bao phủ.
