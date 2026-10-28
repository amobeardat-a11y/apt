/**
 * Ngân hàng câu hỏi Luyện thi Aptitude Test tiếng Việt - APTI
 * Biên soạn chuẩn cấu trúc đề thi Management Trainee & Đánh giá năng lực doanh nghiệp
 */

export const QUIZ_CATEGORIES = [
  { id: 'all', name: 'Tất cả' },
  { id: 'numerical', name: 'Số học' },
  { id: 'logical', name: 'Logic' },
  { id: 'verbal', name: 'Ngôn ngữ' },
  { id: 'abstract', name: 'Hình ảnh' }
];

export const QUIZ_QUESTIONS = [
  {
    id: 1,
    category: 'numerical',
    categoryName: 'Số học',
    level: 'Cơ bản',
    question: 'Năm 2025, doanh thu của công ty APTI đạt 50 tỷ VNĐ. Mục tiêu năm 2026 là tăng trưởng 20%. Doanh thu mục tiêu năm 2026 là bao nhiêu?',
    options: [
      '55 tỷ VNĐ',
      '60 tỷ VNĐ',
      '62.5 tỷ VNĐ',
      '70 tỷ VNĐ'
    ],
    correctIndex: 1,
    explanation: 'Mức tăng thêm là: 50 × 20% = 10 tỷ VNĐ. Doanh thu mới = 50 + 10 = 60 tỷ VNĐ (hoặc tính nhanh: 50 × 1.2 = 60).',
    tip: 'Mẹo MT: Khi nhân với 20%, hãy chia cho 5 rồi cộng vào số gốc để ra kết quả trong 3 giây!'
  },
  {
    id: 2,
    category: 'numerical',
    categoryName: 'Số học',
    level: 'Thực tế',
    question: 'Một sản phẩm có giá vốn 120.000 VNĐ. Công ty muốn đạt tỷ suất lợi nhuận trên giá bán (Gross Margin) là 25%. Giá bán niêm yết của sản phẩm phải là bao nhiêu?',
    options: [
      '150.000 VNĐ',
      '160.000 VNĐ',
      '145.000 VNĐ',
      '175.000 VNĐ'
    ],
    correctIndex: 1,
    explanation: 'Chú ý bẫy tỷ suất lợi nhuận trên GIÁ BÁN: Lợi nhuận = 25% Giá bán ⇒ Giá vốn = 75% Giá bán. Vậy Giá bán = 120.000 / 0.75 = 160.000 VNĐ.',
    tip: 'Bẫy thường gặp: Nhiều bạn lấy 120.000 × 1.25 = 150.000 VNĐ (đây là Markup trên giá vốn, không phải Gross Margin trên doanh số!).'
  },
  {
    id: 3,
    category: 'logical',
    categoryName: 'Logic',
    level: 'Suy luận',
    question: 'Tất cả các thành viên đội ngũ Trainee đều giỏi giải quyết vấn đề. Một số thành viên Trainee biết lập trình Python. Kết luận nào sau đây CHẮC CHẮN ĐÚNG?',
    options: [
      'Tất cả người giỏi giải quyết vấn đề đều biết lập trình Python',
      'Tất cả người biết lập trình Python đều là thành viên Trainee',
      'Ít nhất một người biết lập trình Python giỏi giải quyết vấn đề',
      'Không có ai giỏi giải quyết vấn đề mà không biết lập trình Python'
    ],
    correctIndex: 2,
    explanation: 'Có những thành viên Trainee vừa thuộc tập "giỏi giải quyết vấn đề" vừa thuộc tập "biết Python". Do đó, phần giao nhau giữa 2 tập này chắc chắn không rỗng ⇒ Ít nhất một người biết Python giỏi giải quyết vấn đề.',
    tip: 'Mẹo vẽ biểu đồ Venn: Vẽ vòng tròn Trainee nằm gọn trong vòng tròn Giải Quyết Vấn Đề, sau đó vẽ vòng Python giao một phần.'
  },
  {
    id: 4,
    category: 'logical',
    categoryName: 'Logic',
    level: 'Sắp xếp',
    question: 'Năm ứng viên: An, Bình, Châu, Dũng, Giang xếp hàng phỏng vấn. An đứng trước Bình nhưng đứng sau Châu. Dũng đứng trước Châu. Giang đứng cuối cùng. Người đứng thứ hai trong hàng là ai?',
    options: [
      'An',
      'Châu',
      'Dũng',
      'Bình'
    ],
    correctIndex: 1,
    explanation: 'Từ các điều kiện: Dũng đứng trước Châu (D > C). Châu đứng trước An (C > A). An đứng trước Bình (A > B). Giang đứng cuối cùng. Thứ tự từ đầu đến cuối là: Dũng → Châu → An → Bình → Giang. Người đứng thứ hai là Châu.',
    tip: 'Mẹo MT: Viết ngay chuỗi bất đẳng thức D > C > A > B > G ra nháp để xác định thứ tự trong 10 giây.'
  },
  {
    id: 5,
    category: 'verbal',
    categoryName: 'Ngôn ngữ',
    level: 'Đọc hiểu',
    question: 'Đoạn văn: "Việc chuyển đổi số trong chuỗi cung ứng không chỉ giúp giảm 18% chi phí vận hành kho bãi mà còn rút ngắn thời gian giao hàng chặng cuối. Tuy nhiên, rào cản lớn nhất nằm ở chi phí đầu tư hạ tầng cảm biến IoT ban đầu đối với các doanh nghiệp vừa và nhỏ."\n\nNhận định: "Các doanh nghiệp nhỏ có thể ngay lập tức tiết kiệm chi phí mà không gặp bất kỳ thách thức tài chính nào."',
    options: [
      'Đúng (True)',
      'Sai (False)',
      'Không đủ thông tin để kết luận (Cannot Say)'
    ],
    correctIndex: 1,
    explanation: 'Đoạn trích nêu rõ: "rào cản lớn nhất nằm ở chi phí đầu tư hạ tầng cảm biến IoT ban đầu đối với các doanh nghiệp vừa và nhỏ". Do đó, nhận định cho rằng họ không gặp bất kỳ thách thức tài chính nào là SAI trực diện.',
    tip: 'Quy tắc Verbal MT: Đối chiếu từ khóa khẳng định tuyệt đối như "không gặp bất kỳ thách thức nào" với các từ giới hạn trong bài như "rào cản lớn nhất".'
  },
  {
    id: 6,
    category: 'numerical',
    categoryName: 'Số học',
    level: 'Phân tích bảng',
    question: 'Bộ phận Marketing chi 40 triệu cho Facebook Ads mang về 80 khách hàng, chi 30 triệu cho Google Ads mang về 50 khách hàng. Chi phí trung bình để có một khách hàng mới (CAC) của cả hai kênh là bao nhiêu?',
    options: [
      '500.000 VNĐ',
      '538.461 VNĐ',
      '550.000 VNĐ',
      '600.000 VNĐ'
    ],
    correctIndex: 1,
    explanation: 'Tổng chi phí = 40 + 30 = 70 triệu VNĐ. Tổng số khách hàng = 80 + 50 = 130 khách. Chi phí trung bình CAC = 70.000.000 / 130 ≈ 538.461 VNĐ.',
    tip: 'Bẫy số học: Đừng lấy trung bình cộng của 2 đơn giá CAC! Phải tính Tổng chi phí chia Tổng số lượng (Weighted Average).'
  },
  {
    id: 7,
    category: 'abstract',
    categoryName: 'Hình ảnh',
    level: 'Quy luật',
    question: 'Một kim đồng hồ trong ma trận hình học xoay theo chiều kim đồng hồ lần lượt các góc: 45°, 90°, 135°. Góc xoay ở bước tiếp theo theo quy luật cấp số cộng sẽ là bao nhiêu độ?',
    options: [
      '150°',
      '160°',
      '180°',
      '225°'
    ],
    correctIndex: 2,
    explanation: 'Quy luật tăng dần của góc quay: 45° (+45°) → 90° (+45°) → 135° (+45°) → Bước tiếp theo là 180° (ngược hướng ban đầu).',
    tip: 'Mẹo quy luật: Tìm sự sai khác giữa các bước liên tiếp (delta). Ở đây delta cố định là 45°.'
  },
  {
    id: 8,
    category: 'verbal',
    categoryName: 'Ngôn ngữ',
    level: 'Suy luận ý',
    question: 'Đoạn văn: "Phần lớn các chương trình Management Trainee không tìm kiếm những ứng viên đã thành thạo mọi kỹ năng chuyên môn từ trước. Trọng tâm của họ là năng lực học hỏi nhanh, khả năng tư duy giải quyết vấn đề và sự thích ứng với môi trường làm việc linh hoạt."\n\nThông điệp cốt lõi đoạn văn muốn truyền tải là gì?',
    options: [
      'Kỹ năng chuyên môn hoàn toàn không có giá trị trong phỏng vấn',
      'Tiềm năng phát triển và tư duy linh hoạt quan trọng hơn kiến thức kinh nghiệm có sẵn',
      'Chỉ sinh viên tốt nghiệp loại xuất sắc mới có thể tham gia ứng tuyển MT',
      'Các công ty sẽ tự đào tạo lại toàn bộ từ con số không cho ứng viên'
    ],
    correctIndex: 1,
    explanation: 'Tác giả đối lập giữa "kỹ năng chuyên môn có sẵn" với "năng lực học hỏi nhanh, tư duy giải quyết vấn đề, thích ứng", nhấn mạnh tiềm năng phát triển chính là yếu tố then chốt.',
    tip: 'Phương pháp loại trừ: Loại bỏ các câu chứa từ cực đoan không có trong bài như "hoàn toàn không có giá trị", "chỉ sinh viên xuất sắc".'
  }
];

export const STUDY_ROADMAP = [
  {
    step: 1,
    title: 'Khởi động & Giải mã đề thi',
    desc: 'Làm quen các thuật ngữ Numerical, Logical, Verbal bằng tiếng Việt, nắm cấu trúc đề thi MT phổ biến (SHL, Korn Ferry, Saville).',
    duration: 'Ngày 1 - 3',
    badge: 'Cơ bản',
    completed: true
  },
  {
    step: 2,
    title: 'Xử lý Số liệu & Tính toán thần tốc',
    desc: 'Luyện tập kỹ năng tính nhẩm %, đọc biểu đồ kinh doanh, tỷ suất lợi nhuận và tối ưu hóa thời gian với mẹo bấm máy tính.',
    duration: 'Ngày 4 - 10',
    badge: 'Trọng tâm',
    completed: true
  },
  {
    step: 3,
    title: 'Tư duy Logic & Lập luận phản biện',
    desc: 'Phá vỡ các bẫy ngụy biện, thuần thục bài toán Venn, logic điều kiện If-Then và sắp xếp chuỗi suy luận logic.',
    duration: 'Ngày 11 - 18',
    badge: 'Nâng cao',
    completed: false
  },
  {
    step: 4,
    title: 'Đọc hiểu Ngôn ngữ chuẩn bài thi MT',
    desc: 'Chiến thuật True / False / Cannot Say, kỹ thuật Skimming & Scanning văn bản báo cáo kinh tế song ngữ.',
    duration: 'Ngày 19 - 25',
    badge: 'Chuyên sâu',
    completed: false
  },
  {
    step: 5,
    title: 'Thi thử áp lực thời gian (Mock Test)',
    desc: 'Thi thử 20 câu dưới áp lực đồng hồ đếm ngược thực chiến, nhận bảng báo cáo phân tích điểm mạnh yếu để bứt phá.',
    duration: 'Ngày 26 - 30',
    badge: 'Về đích',
    completed: false
  }
];
