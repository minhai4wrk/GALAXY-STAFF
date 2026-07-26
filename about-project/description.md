# 1\. Thông tin tổng quan

* Tên hệ thống: Galaxy Staff  
* Mô tả ngắn (1–2 câu): Hệ thống quản lý nhân sự rạp chiếu phim, gồm web và app  
* Vấn đề hệ thống giải quyết:  
- sắp xếp lịch thủ công trên google sheet, publish lịch làm qua nhóm face, trao đổi ca/xin nghỉ qua nhóm mess,... không đồng bộ hệ thống  
- cuối tháng xác nhận công cũng rời rạc tại nhiều hệ thống

# 2\. Vai trò (Roles)

## 2.1. Quản lí \- manager:

- tạo ca làm dựa trên lịch đăng kí làm việc của nhân viên, công bố ca và quản lí lịch làm  
- duyệt các yêu cầu trao đổi ca, nghỉ phép  
- thông báo các thông tin quan trọng khác: đăng thông tin CTKM, lịch phim tuần, lịch họp,....

## 2.2. Nhân viên- staff:

- Đăng kí lịch làm theo tuần  
- Xem lịch làm với chế độ cá nhân, theo ngày (hiển thị các nhân viên khác làm cùng ca)  
- Gửi yêu cầu pass ca hoặc nhận ca tại chức năng Trao đổi ca.  
- Nhận thông báo từ quản lý

# 3\. Chức năng chính (Core Features)

## 3.1. Feature 1: ‘availability’ \- đăng kí lịch làm (manager & staff)

- giao diện Grid tương tự như when2meet, đăng ký lịch rảnh kiểu kéo-thả  
- trang chính sẽ hiển thị lịch rảnh của toàn bộ nhân viên theo hình thức hiển thị chồng lớp (Overlap) trong 1 grid, khung giờ nào có màu xanh càng đậm thì chứng tỏ khung giờ đó càng có nhiều người rảnh. Khi di chuột hoặc bấm vào một ô thời gian cụ thể, sẽ hiện ra danh sách ai rảnh ai bận.  
- Khi bấm vào ô “Edit availability”, sẽ hiển thị 1 bảng trống, nhấn giữ và kéo chuột qua các ô thời gian để "tô màu" lịch rảnh. chỉ cần kéo chuột qua ô đó một lần nữa để xóa.  
- phạm vi đăng kí là từ 8h sáng đến ‘closed’(tương tự 2 giờ sáng), mỗi ô 30p  
- hiển thị template-shitf: ca sáng: 8-13, ca chiều 13-18, ca tối 18-closed, cả ngày full. khi lựa chọn kéo thả vào ngày nào thì tự động fill vòa khoảng thời gian đó.  
- ngoài ra có thể tick vào dấu (+) để tạo các shift nếu k muốn drag.  
- Bấm “save availability” để lưu lên hệ thống  
- thời gian đăng kí theo tuần, bắt đầu từ thứ 6 đến thứ 5 tuần sau  
- Deadline đăng ký lịch làm trước 18h Thứ 7 hàng tuần trước tuần đăng ký. Lịch sẽ khóa khi đến deadline và mở lịch đăng ký mới cho tuần tiếp theo.  
- Đăng ký lịch làm tối thiểu 5 ngày/ tuần. Nếu đăng ký lịch làm ít hơn số buổi quy định phải xin phép trước với quản lý và được phê duyệt về vấn đề này.  
- Sau khi lịch đăng kí khóa, quản lí sẽ bắt đầu sắp xếp lịch làm.

## 3.2. Feature 2: ‘roster’ \- Lịch làm việc

- Trang chính: hiển thị lịch làm việc, có chế độ xem theo ngày (timeline view), tuần (Daily Card) cho tất cả các nhân viên. cột là các ngày trong tuần, các hàng là các nhân viên, ngoài ra hàng trên cùng sẽ là các lịch rảnh còn trống \- open-shift, nơi chứa các ca làm chưa được phân công.  
- lịch làm của nhân viên sẽ được tô 1 thanh màu để dễ nhận biết cho manager sắp xếp ca  
- Staff: chỉ có thể xem lịch làm của nhân viên, tại hàng open-shift, staff có thể tích nhận ca.  
- Manager: sắp xếp lịch làm cho nhân viên, tại chế độ ngày, xếp lịch kéo-thả tạo 1 khối hộp, có thể bấm vào khối hộp để modify, chế độ tuần sẽ click vào ngày để tạo ra 1 hộp và modify thông tin ca làm; sử dụng tính năng Auto-Scheduling, hệ thống dựa vào lịch rảnh của nhân viên và tự động xếp các ca tại open-shift vào các nhân viên phù hợp; publish các thay đổi lên hệ thống.

## 3.3. Feature 3: ‘shift-exchange’ \- trao đổi ca làm

- Giao diện tương tự như ‘roster’ hiển thị tuần làm việc có các ca làm. tuy nhiên tất cả ca làm không có yêu cầu pass ca sẽ có màu xám và nhạt, chỉ những ca được đăng pass ca sẽ hiện màu lên.  
- 2 hình thức trao đổi: **pass ca** (nhường ca) và **nhận ca**. *(Swap ca — đổi ca 2 chiều — được lên kế hoạch cho Version 2)*  
- khi nhân viên bấm “pass ca” trên ca của mình, có thể nhập kèm **lời nhắn** (vd: lý do bận). Ca chuyển sang highlight trên bảng.  
- khi nhân viên bấm vào ca được đăng pass sẽ có thông tin của ca làm, lời nhắn của người đăng, và nút **nhận ca**.  
- khi bấm nhận ca, hệ thống sẽ gửi request lên quản lí để phê duyệt yêu cầu. **Nếu ca nhận trùng giờ với ca hiện có của mình thì cảnh báo** trước khi gửi.  
- sau khi phê duyệt thành công, card ca làm sẽ di chuyển qua staff nhận ca, có ký hiệu trao đổi ca.  
- Lưu ý trạng thái của ca và trường hợp xung đột, chỉ duy nhất 1 người nhận được ca.

## 3.4. Feature 4: ‘News feed’ \- trang thông tin

- dành cho quản lí đăng các thông tin quan trọng cho toàn bộ nhân viên.

# 4\. Luồng hoạt động (User Flow)

## 4.1. Flow 1: Đăng ký lịch khả dụng hàng tuần (Staff)

*Mục đích: Nhân viên điền lịch rảnh trước deadline để quản lý có cơ sở xếp ca.*

1. **Bắt đầu:** Staff đăng nhập vào hệ thống \-\> Mở tab **Availability**.  
2. **Kiểm tra Deadline:**  
   * *Nếu sau 18h00 Thứ 7:* Hệ thống khóa nút đăng ký, hiển thị thông báo "Đã hết hạn đăng ký". (Kết thúc flow)  
   * *Nếu trước 18h00 Thứ 7:* Hiển thị màn hình Overlap tổng \-\> Staff bấm nút **"Edit availability"**.  
3. **Thao tác điền lịch:** Staff thao tác trên bảng Grid trống của tuần tới bằng nhiều cách:  
   * Nhấn giữ và kéo thả (Drag-drop) qua các ô 30 phút để tô màu xanh.  
   * Hoặc kéo **Template-shift** (Sáng/Chiều/Tối/Full) vào ngày tương ứng để fill tự động.  
   * Hoặc click vào tạo shift, điền thời gian ca làm.  
4. **Kiểm tra điều kiện:** Staff bấm **"Save availability"**.  
   * Hệ thống đếm số ngày đăng ký. *Nếu \< 5 ngày:* Pop-up cảnh báo hiện lên yêu cầu Staff nhập "Lý do xin đăng ký thiếu buổi" (có thể bỏ qua, chỉ hiện cảnh báo) \-\> Bấm gửi.  
   * *Nếu \>= 5 ngày:* Lưu thành công ngay lập tức.  
5. **Kết thúc:** Trở về màn hình Availability Overlap của cả team.

## 4.2. Flow 2: Sắp xếp và Công bố lịch làm (Manager)

*Mục đích: Quản lý lên lịch dựa trên dữ liệu rảnh của nhân viên và nhu cầu thực tế của rạp.*

1. **Bắt đầu:** Sau deadline (18h00 Thứ 7), Manager đăng nhập \-\> Mở tab **Roster**.  
2. **Khởi tạo lịch:** Manager chọn tuần làm việc mới. Hàng trên cùng (Open-shift) đang chứa danh sách các ca làm cần thiết của rạp.  
3. **Thao tác xếp ca:** Manager chọn 1 trong 2 cách:  
   * **Cách 1 (Thủ công):** Kéo thả ca từ Open-shift xuống hàng của Staff phù hợp (có thể click vào hộp ca để modify giờ) hoặc trực tiếp kéo thả trong hàng của nhân viên tương ứng để tạo ca.  
   * **Cách 2 (Tự động):** Bấm nút **"Auto-Scheduling"** \-\> Hệ thống thuật toán tự động lấy các ca ở Open-shift nhét vào các thanh thời gian màu xanh (rảnh) của Staff.  
4. **Review:** Manager kiểm tra lại bản nháp, kéo thả để điều chỉnh nếu chưa ưng ý.  
5. **Publish:** Manager bấm nút **"Publish Roster"**.  
6. **Kết thúc:** Lịch được chốt. Hệ thống gửi Noti (thông báo) đến toàn bộ Staff: "Lịch làm việc tuần tới đã được công bố".

## 4.3. Flow 3: Quy trình Pass ca / Nhận ca (Staff A \-\> Staff B \-\> Manager)

*Mục đích: Luồng xử lý khi một nhân viên có việc bận đột xuất và muốn nhường ca cho người khác.*

1. **Staff A (Người pass ca):** Mở tab **Shift-Exchange** \-\> Click vào ca làm việc của mình \-\> Chọn **"Pass ca"** (có thể nhập lời nhắn) \-\> Ca làm chuyển sang màu nổi bật (Highlight).  
2. **Staff B (Người nhận ca):** Lướt tab **Shift-Exchange** \-\> Thấy ca của Staff A đang nổi bật \-\> Click vào ca đó \-\> xem lời nhắn \-\> Bấm **"Nhận ca"**. *Nếu ca này trùng giờ với ca hiện có của B → hệ thống cảnh báo, B xác nhận mới tiếp tục.*  
3. **Khóa ca tạm thời:** Sau khi B nhận, hệ thống đổi trạng thái ca thành *Pending Approval* (Chờ duyệt). Các nhân viên khác không thao tác được nữa để tránh xung đột.  
4. **Manager phê duyệt:**  
   * Manager nhận được Noti yêu cầu pass ca \-\> Mở yêu cầu (xem ca, có cảnh báo trùng giờ nếu có).  
   * *Nếu Reject (Từ chối):* Trạng thái ca quay về bình thường. Bắn thông báo cho A và B.  
   * *Nếu Approve (Đồng ý):* Thẻ ca chuyển từ A sang B. Dán nhãn "Trao đổi ca".  
5. **Kết thúc:** Bắn thông báo xác nhận cho cả Staff A và Staff B.

## 4.4. Flow 4: Pick up Open-shift (Staff \-\> Manager)

*Mục đích: Nhân viên muốn làm thêm giờ bằng cách nhận các ca quản lý chưa tìm được người rảnh.*

1. **Bắt đầu:** Staff xem lịch ở tab **Roster**.  
2. **Tìm ca trống:** Staff thấy trên hàng ngang trên cùng (Open-shift) vẫn còn ca chưa có người làm (do thiếu nhân sự rảnh).  
3. **Đăng ký nhận:** Staff click vào ca Open-shift đó \-\> Bấm **"Apply for shift"** (Đăng ký nhận ca).  
4. **Manager phê duyệt:** Manager nhận thông báo \-\> Vào check xem Staff này có bị quá giờ làm hay không \-\> Bấm **Approve**.  
5. **Kết thúc:** Ca làm di chuyển từ hàng Open-shift xuống hàng của Staff. Roster được cập nhật.

## 4..5 Flow 5: Luồng Bảng tin nội bộ (Manager \-\> Staff)

*Mục đích: Đảm bảo thông tin truyền đạt đồng nhất, không bị trôi như trên Messenger.*

1. **Bắt đầu:** Manager đăng nhập \-\> Mở tab **News Feed**.  
2. **Tạo bài viết:** Bấm "Tạo thông báo mới" \-\> Nhập Tiêu đề (VD: Lịch chiếu phim Marvel cuối tuần) \-\> Nhập nội dung / Đính kèm hình ảnh CTKM.  
3. **Publish:** Bấm **"Đăng bài"**.  
4. **Hiển thị:** Bài viết xuất hiện trên đầu trang News Feed. Hệ thống bắn Noti cho toàn bộ Staff: *"Quản lý vừa đăng một thông báo mới"*.  
5. **Staff tương tác:** Staff bấm vào Noti \-\> Đọc bài viết (Hệ thống có thể lưu lại log "Seen" để Manager biết ai đã đọc, ai chưa đọc).

# 5\. Công nghệ (gợi ý)

## 5.1. Frontend (Giao diện người dùng)

* **Web Dashboard:** **React.js** hoặc **Vue.js**.  
* **Mobile App:** **Flutter**.

## 5.2. Backend (Xử lý logic)

* **Ngôn ngữ & Framework:** **Python** với **FastAPI**.

## 5.3. Database (Cơ sở dữ liệu):

- Database chính: PostgreSQL.

## 5.4. Khác

* **Containerization:** **Docker**.  
* **Thông báo (Push Notifications):** **Firebase Cloud Messaging (FCM)**.   
* **Quản lý phiên bản:** **Git**.

# 6\. Yêu cầu hệ thống

## 6.1. Yêu cầu Bảo mật (Security)

* **Xác thực và Phân quyền (Authentication & Authorization):**  
  * Sử dụng JSON Web Token (JWT) để quản lý phiên đăng nhập. Phân quyền Role-based Access Control (RBAC)  
* **Bảo vệ dữ liệu:**  
  * Mật khẩu của người dùng phải được băm (hashing) bằng thuật toán chuẩn (ví dụ: bcrypt) trước khi lưu vào PostgreSQL, tuyệt đối không lưu dạng plain-text.  
  * Các API phải được thiết kế để chống lại các cuộc tấn công SQL Injection (thông qua việc sử dụng ORM như SQLAlchemy) và Cross-Site Scripting (XSS).

## 6.2. Yêu cầu Hiệu năng (Performance)

* **Thời gian phản hồi API (API Response Time):** \* Tận dụng khả năng xử lý bất đồng bộ của FastAPI, 95% các API cơ bản (lấy lịch, xem bảng tin) phải phản hồi dưới 300ms.  
* **Hiệu suất thuật toán Xếp ca tự động (Auto-Scheduling):** \* Engine xử lý ràng buộc (Rules-based engine) phải giải quyết xong bài toán xếp ca cho một cụm rạp (khoảng 50 \- 100 nhân viên, 200 \- 300 ca làm/tuần) và trả về kết quả Draft Roster trong thời gian tối đa **dưới 10 giây**.  
* **Xử lý đồng thời (Concurrency):** \* Hệ thống phải chịu tải tốt vào các "khung giờ vàng" (Peak hours), cụ thể là sát deadline 18h00 Thứ 7 hàng tuần khi hàng loạt Staff đồng loạt truy cập ứng dụng để lưu lịch rảnh (Availability).

## 6.3. Yêu cầu UI/UX (Giao diện và Trải nghiệm người dùng)

* **Đối với Web Manager (Quản lý rạp):**  
  * Giao diện phải hỗ trợ tốt trên màn hình máy tính (Desktop-first) để có không gian rộng rãi.  
  * Yêu cầu bắt buộc thao tác **Kéo \- Thả (Drag & Drop)** mượt mà trên lưới thời gian khi xếp ca hoặc sửa ca.  
  * Sử dụng màu sắc (Color-coding) trực quan: Đỏ cho báo lỗi xung đột lịch, Xanh cho ca đã duyệt, Xám cho ca trống (Open-shift).  
* **Đối với Mobile App:**  
  * Giao diện tối ưu hoàn toàn cho thiết bị di động (Mobile-first).  
  * Cấu trúc thông tin dạng **Thẻ (Card View)** tối giản, hiển thị font chữ to, rõ ràng, giúp nhân viên lướt xem ca làm, trạm trực bằng một tay dễ dàng.  
  * Hạn chế tối đa việc bắt người dùng gõ phím. Các thao tác nhận ca, pass ca, xin nghỉ phép chỉ nên gói gọn trong 1-2 cú chạm (Tap) và các nút bấm lớn (Large Touch Targets).

## 6.4. Khả năng mở rộng (Scalability)

* **Kiến trúc Database:** PostgreSQL phải được thiết kế chuẩn hóa (Normalization) để dễ dàng mở rộng thêm các Cụm rạp (Locations) hoặc các Vị trí công việc mới (Roles) trong tương lai mà không làm phá vỡ logic xếp ca cũ.  
* **Đóng gói và Triển khai:** Toàn bộ ứng dụng (Frontend, Backend, Database) phải được đóng gói bằng **Docker**. Điều này giúp hệ thống dễ dàng di chuyển, triển khai trên các máy chủ khác nhau hoặc nâng cấp tài nguyên (Scale-up) khi rạp phim mở rộng thêm chi nhánh hoặc số lượng nhân sự tăng vọt.  
* **Khả năng tích hợp:** Các API thiết kế theo chuẩn RESTful để sau này dễ dàng cắm (plug) thêm các phân hệ khác nếu cần, ví dụ như tích hợp module tính lương (Payroll) hoặc hệ thống máy chấm công vật lý tại rạp.

# 7\. Output mong muốn

## 7.1. Web/App chạy được (Source code & Deployment):

* **Backend API:** Hoàn thiện và chạy ổn định.  
* **Web Dashboard:** Dành cho Manager sử dụng trên máy tính (đáp ứng tốt thao tác kéo-thả xếp ca).  
* **Mobile App (MVP):** Dành cho Staff sử dụng trên điện thoại (đảm bảo luồng đăng ký rảnh, xem ca và pass ca mượt mà).  
* *Khuyến nghị:* Đóng gói hệ thống (Docker) và triển khai lên một server cơ bản (ví dụ: AWS EC2 hoặc Render) để có thể truy cập trực tuyến.

## 7.2. Báo cáo PDF (Project Report):

* Tài liệu đặc tả yêu cầu hệ thống (Requirement Specification).  
* Tài liệu thiết kế kiến trúc phần mềm và cơ sở dữ liệu (Database Schema, ERD).  
* Tài liệu đặc tả API (API Documentation \- có thể xuất từ Swagger của FastAPI).  
* Mô tả chi tiết giải thuật áp dụng cho bộ máy Auto-Scheduling.

## 7.3. Slide trình bày (Presentation):

* Slide tóm tắt các "nỗi đau" (pain points) của việc xếp ca thủ công, giải pháp của Galaxy Staff, kiến trúc công nghệ được sử dụng, và kết quả đạt được.

## 7.4. Demo (Kịch bản chạy thử nghiệm thu):

* Xây dựng sẵn dữ liệu mẫu (Mock data) của một rạp phim gồm 1 Quản lý và khoảng 10-15 Nhân viên.  
* Thực hiện Live Demo nghiệm thu 3 luồng rủi ro cao nhất:  
  * *Test case 1:* Chạy Auto-scheduling xem hệ thống có xếp nhầm người vào giờ họ đã báo bận hay không.  
  * *Test case 2:* Staff A nhượng ca, Staff B nhận ca, Manager duyệt \-\> Ca làm tự động chuyển cho B.  
  * *Test case 3:* Cảnh báo lỗi đỏ khi Manager cố tình xếp một người làm quá số giờ quy định.