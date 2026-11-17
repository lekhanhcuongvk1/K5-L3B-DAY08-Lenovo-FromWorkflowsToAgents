# Báo cáo cá nhân — Lê Khánh Cường

## 1. Thông tin thành viên

- Họ tên: Lê Khánh Cường
- MSSV: 2A202603999
- Email: lekhanhcuongvk1@gmail.com
- GitHub: lekhanhcuongvk1

## 2. Phần việc phụ trách

Tôi phụ trách CP5: chạy benchmark, tổng hợp số liệu, hoàn thiện research card, ADR và báo cáo nhóm. Sau khi nhóm hoàn thành CP2–CP4, tôi dùng cùng bộ claim và seed để so sánh bốn kiến trúc, thay vì chọn theo số lượng agent hoặc mức độ phức tạp của code. Tôi cũng phụ trách phần mở rộng B4 về baseline, ablation và thống kê, cùng việc tự kiểm trên dữ liệu hidden không có nhãn.

CP1 là phần chung của cả nhóm. Ba thành viên còn lại lần lượt phụ trách CP2, CP3 và CP4. Tôi tiếp nhận kết quả từ các checkpoint này để đánh giá, so sánh và tổng hợp báo cáo.

## 3. Đóng góp cụ thể

Trong commit `372b1f3`, tôi tổng hợp benchmark bốn shape trên 14 claim public và năm seed, hoàn thiện nội dung ADR, research card và báo cáo nhóm. Phần nghiên cứu dùng phép bật/tắt một lượt investigator thứ hai để xem việc đọc lại cùng dữ liệu có làm tăng độ đúng hay chỉ tăng chi phí. Hai cấu hình đều đạt 70/70 trial, nhưng cost/success tăng từ 46.43 lên 82.86 VND mô phỏng. Tôi dùng kết quả này để bổ sung lập luận cho lựa chọn workflow, đồng thời giữ giới hạn rằng hai lượt investigator chạy tuần tự và không gọi model.

Tôi bổ sung hai test trong `src/tests/test_bonus_investigator_ablation.py`: kiểm tra lượt investigator thứ hai không đổi quyết định và không gây ghi trùng khi retry; kiểm tra variant vẫn truyền crash và khôi phục runner sau khi lỗi. Các thay đổi code và test này có sử dụng Codex hỗ trợ, được trình bày ở mục 5.

Trong commit `6e56be2`, tôi bổ sung bonus B4: baseline rules-only, swarm pruned theo seed, ablation bỏ bước kiểm thiếu mã đơn và script tái lập kết quả. Phần thống kê dùng bootstrap 10.000 lần theo claim, McNemar exact trên cặp claim/seed và sign test theo claim để đối chiếu ảnh hưởng của các seed phụ thuộc nhau. Các variant vẫn dùng cổng approval và durability của host.

File `src/tests/test_bonus_b4.py` có 44 trường hợp kiểm thử sau khi tham số hóa. Các nhóm test kiểm công thức thống kê bằng đáp án biết trước, đối chiếu baseline với shape gốc, xác nhận bỏ parse thực sự bỏ cả hành vi đọc số ngày, kiểm crash/resume và thử khả năng phát hiện leak/bypass của scanner. Tôi giữ mask pruning đã chọn thay vì đổi seed để loại riêng trial swarm đang sai.

Tôi cũng chạy hidden self-check cho ba shape chính. Khi chạy lệnh ban đầu, chương trình báo thiếu `student_drop/hidden_world_state.json`; sau khi đặt đúng hai file dành cho học viên vào `src/student_drop/`, lệnh chạy hoàn tất. Phần tự kiểm bonus được chạy riêng để theo dõi các variant, không dùng kết quả đó thay cho điểm hidden chính thức.

## 4. Bằng chứng

| Nội dung | Bằng chứng |
| --- | --- |
| Benchmark, research card, ADR và báo cáo CP5 | Commit [372b1f3](https://github.com/lekhanhcuongvk1/K5-L3B-DAY08-Lenovo-FromWorkflowsToAgents/commit/372b1f3); `src/reports/benchmark.json`; `report/team/research_card.md`; `report/team/decision_adr.md` |
| Ablation investigator | `src/reports/ablation_investigators.json`; cặp `R-orchestrator-C-001-s11` / `R-orchestrator_two-C-001-s11`; `test_second_investigator_preserves_decision_and_retry`; `test_variant_propagates_crash_and_restores_runner` |
| Bonus B4 | Commit [6e56be2](https://github.com/lekhanhcuongvk1/K5-L3B-DAY08-Lenovo-FromWorkflowsToAgents/commit/6e56be2); `src/reports/bonus_ablation.json` (490 trial); `report/team/bonus_report.md` |
| Test B4 tiêu biểu | `test_exact_mcnemar_and_cluster_sign_known_answer`; `test_rules_only_matches_official_workflow`; `test_drop_parse_removes_its_behavior_not_only_cost`; `test_variants_resume_once_after_each_crash` trong `src/tests/test_bonus_b4.py` |
| Hidden self-check | `src/reports/hidden_selfcheck.json`: ba shape × 200 trial; `src/reports/bonus_hidden_selfcheck.json`: năm cấu hình × 200 trial. Mỗi cấu hình có 0 lỗi chạy, 0 leak suspect và reasons chỉ gồm unlabeled. |

Lệnh tái lập B4 là `python -m bonus.run_b4 --out reports/bonus_ablation.json`, chạy trong `src/`. Lần kiểm tra cuối đã chạy cho kết quả `100 passed` ở bộ mặc định và `248 passed` ở student matrix.

Trên public, workflow đạt pass rate/pass^5 bằng 1.0, cost/success khoảng 27.86 VND mô phỏng. Swarm pruned giữ pass rate 0.9857 của swarm và giảm cost/success khoảng 1.46%. McNemar giữa workflow và swarm cho p = 1.0, nên tôi không diễn giải chênh lệch một trial thành bằng chứng thống kê rằng workflow luôn tốt hơn. Khi bỏ nhánh kiểm thiếu order_id, pass rate giảm còn 0.9286 vì C-004 bị trả escalated thay cho needs_info ở cả năm seed.

## 5. Công cụ AI đã dùng

Tôi sử dụng Codex để đọc yêu cầu, giải thích lệnh chạy, hỗ trợ xây dựng code/test cho ablation và B4, phân tích output và soạn bản nháp báo cáo theo template. Phần hỗ trợ này bao gồm cả code, test và cách trình bày kết quả. Tôi kiểm tra bằng các lệnh thực nghiệm và kiểm thử nêu trong báo cáo.

Tôi trực tiếp chạy benchmark, hidden self-check và hai bộ pytest trong terminal, đối chiếu output với các file report và kiểm tra lại các lỗi submission còn thiếu. Các số liệu trong báo cáo lấy từ JSON do chương trình sinh ra, không sửa tay để đạt ngưỡng. Những nhận định về thống kê được đối chiếu bằng test có đáp án biết trước và kiểm định theo claim, thay vì chỉ dựa vào lời giải thích của AI.

MockLLM trong chương trình là backend mô phỏng theo seed của lab, khác với Codex dùng để hỗ trợ làm bài. Phần thực nghiệm không gọi model thật hoặc dùng API key.

## 6. Tự đánh giá

Qua CP5, tôi hiểu rõ hơn việc một kiến trúc chạy đúng trên public chưa đủ để kết luận nó phù hợp trong mọi trường hợp. Trong bài này, workflow đã đáp ứng các case công khai với chi phí thấp nhất, còn thêm lượt investigator không mang lại cải thiện độ đúng. Vì vậy tôi ưu tiên giữ luồng đơn giản và giải thích lựa chọn bằng dữ liệu.

Điểm còn hạn chế là tôi sử dụng AI hỗ trợ nhiều cho phần code và thống kê, nên cần tiếp tục tự đọc và thực hành để có thể giải thích từng bước tính mà không phụ thuộc vào gợi ý. Bộ public cũng nhỏ và đã được dùng khi phát triển code. Tôi chưa có cơ sở để khẳng định pass rate hidden hoặc điểm bonus; self-check không có nhãn chỉ xác nhận được lỗi chạy, contract trace và dấu hiệu leak trong phạm vi scanner.

Nếu có thêm thời gian, tôi muốn thử nhiều mask pruning và thêm các claim có cấu trúc khác nhau, đồng thời kiểm tra kỹ trường hợp các seed của cùng một claim cho kết quả giống nhau. Điều tôi rút ra là báo cáo cần nói rõ phép đo thực sự chứng minh được gì, kể cả khi kết quả không cho thấy một cải thiện đáng kể.
