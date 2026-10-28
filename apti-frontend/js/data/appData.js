/**
 * Dữ liệu tĩnh ứng dụng APTI: Gói học, Tài liệu, FAQ, Câu thoại Mascot Em Tee
 */

export const PRICING_PLANS = [
  {
    id: 'starter-7d',
    name: 'Gói 7 Ngày',
    tagline: 'Làm quen và khởi động',
    popular: false,
    price: '99.000',
    originalPrice: '149.000',
    unit: 'VNĐ / 7 ngày',
    desc: 'Dành cho bạn mới bắt đầu tìm hiểu aptitude test, thử sức các dạng bài phổ biến và xây dựng thói quen luyện tập.',
    badge: 'Khởi động',
    features: [
      'Trọn bộ tài liệu tiếng Việt giải mã các dạng bài',
      'Luyện tập online hơn 150+ câu hỏi cơ bản',
      'Đáp án & Lời giải chi tiết từng bước',
      'Đồng hồ đếm ngược mô phỏng áp lực thi thực tế',
      'Báo cáo phân tích điểm mạnh yếu sơ bộ',
      'Hỗ trợ giải đáp thắc mắc cùng cộng đồng'
    ],
    ctaText: 'Bắt đầu gói 7 ngày',
    ctaClass: 'b-out'
  },
  {
    id: 'master-30d',
    name: 'Gói 30 Ngày',
    tagline: 'Luyện tập có kế hoạch & Chinh phục MT',
    popular: true,
    price: '249.000',
    originalPrice: '399.000',
    unit: 'VNĐ / 30 ngày',
    desc: 'Dành cho bạn muốn có lộ trình bài bản, củng cố toàn diện Numerical, Logical, Verbal và bứt phá vòng thi test MT.',
    badge: 'Được chọn nhiều nhất',
    features: [
      'Tất cả quyền lợi của Gói 7 ngày',
      'Hơn 600+ câu hỏi phân tầng từ cơ bản đến nâng cao',
      '5 đề thi thử Mock Test chuẩn định dạng SHL/Korn Ferry',
      'Video hướng dẫn mẹo tư duy & bẫy đề thi từ cựu MT',
      'Theo dõi tiến độ học tập chi tiết trên Dashboard',
      'Cập nhật đề thi mới liên tục theo mùa tuyển dụng',
      'Cam kết tự tin làm chủ đề thi sau 30 ngày'
    ],
    ctaText: 'Đăng ký bứt phá ngay',
    ctaClass: 'b-acc'
  }
];

export const DOCUMENT_PACKS = [
  {
    id: 'pack-foundation',
    title: 'Tài liệu Nhập môn Aptitude Test Tiếng Việt',
    desc: 'Giải thích chi tiết các dạng bài Numerical, Logical, Verbal bằng ngôn ngữ thuần Việt, dễ hiểu, không hàn lâm.',
    tag: 'Nhập môn',
    level: 'Dành cho người mới',
    pages: '45 trang PDF + Bài tập'
  },
  {
    id: 'pack-numerical',
    title: 'Cẩm nang Xử lý Số liệu & Tối ưu Tốc độ',
    desc: 'Tổng hợp 12 dạng bảng số liệu kinh doanh thường gặp trong kỳ thi MT kèm mẹo tính nhẩm nhanh không cần máy tính phức tạp.',
    tag: 'Số học',
    level: 'Thực chiến MT',
    pages: '60 trang PDF + Video'
  },
  {
    id: 'pack-logical-verbal',
    title: 'Bộ giải đề Suy luận Logic & Đọc hiểu Verbal',
    desc: 'Phương pháp phân tích lập luận, giải mã bẫy True / False / Cannot Say và kỹ năng Skimming văn bản nhanh.',
    tag: 'Logic & Ngôn ngữ',
    level: 'Nâng cao',
    pages: '50 trang PDF + 100 câu'
  }
];

export const FAQ_ITEMS = [
  {
    q: 'Aptitude test là gì và tại sao các chương trình MT lại yêu cầu?',
    a: 'Aptitude test là bài kiểm tra năng lực tư duy (số liệu, suy luận logic, đọc hiểu ngôn ngữ và giải quyết vấn đề). Các tập đoàn đa quốc gia và chương trình Management Trainee dùng bài thi này ở vòng đầu để sàng lọc khách quan ứng viên có tiềm năng học hỏi nhanh và xử lý áp lực tốt.'
  },
  {
    q: 'Mình chưa từng làm aptitude test thì có học được không?',
    a: 'Hoàn toàn được! APTI được thiết kế chuyên biệt cho người mới bắt đầu từ con số 0. Mọi kiến thức đều được diễn giải bằng tiếng Việt với các ví dụ thực tế gần gũi, giúp bạn đi từ nhận diện dạng bài cơ bản đến tự tin giải các đề thi tuyển dụng.'
  },
  {
    q: 'Tài liệu của APTI có hoàn toàn bằng tiếng Việt không?',
    a: 'Đúng vậy! Toàn bộ nội dung hướng dẫn, tư duy giải đề và phân tích đáp án được trình bày bằng tiếng Việt 100%. Các thuật ngữ quốc tế (như Margin, Profit, Premise...) được giữ nguyên kèm phần giải thích nghĩa cặn kẽ để bạn vừa hiểu bản chất vừa không bỡ ngỡ khi gặp đề thi thật.'
  },
  {
    q: 'Tài liệu có phù hợp với người đã đi làm không?',
    a: 'Rất phù hợp. Ngoài sinh viên chuẩn bị thi MT, rất nhiều chuyên viên và người đi làm sử dụng APTI để ôn thi vào các tập đoàn công nghệ, ngân hàng hoặc nâng cao tư duy logic và kỹ năng đọc hiểu báo cáo số liệu hàng ngày.'
  },
  {
    q: 'Mua tài liệu rồi có được xem đáp án và lời giải chi tiết không?',
    a: 'Có. Tất cả tài liệu và đề luyện tập trên APTI đều đi kèm lời giải chi tiết từng bước, phân tích rõ vì sao đáp án đó đúng và chỉ ra các bẫy thường gặp chứ không đơn thuần chỉ đưa ra đáp án A, B, C, D.'
  },
  {
    q: 'Mình có thể làm thử bài test trước khi đăng ký gói không?',
    a: 'Chắc chắn rồi! Bạn có thể làm ngay bài test thử miễn phí trên website bất cứ lúc nào để biết năng lực hiện tại của mình mà không cần phải trả bất kỳ khoản phí nào trước.'
  }
];

export const MASCOT_QUOTES = {
  welcome: 'Chào bạn! Mình là Em Tee. Hôm nay mình làm bài logic nhé?',
  startQuiz: 'Đọc kỹ đề và chọn đáp án bạn thấy phù hợp nhất nhé.',
  correct: 'Chính xác! Em Tee khen bạn đó.',
  wrong: 'Chưa đúng, thử xem gợi ý nhé.',
  goodJob: 'Bạn vừa hoàn thành bài test. Kết quả rất tốt!',
  needMorePractice: 'Bạn đã hoàn thành bài test. Xem lại các câu cần lưu ý nhé.',
  themeLight: 'Đã chuyển sang giao diện sáng.',
  themeDark: 'Đã chuyển sang giao diện tối.',
  roadmap: 'Tiến độ ôn tập của bạn đang đi đúng hướng.'
};

export const INITIAL_TEST_HISTORY = [
  { testName: 'Số học cơ bản', date: '20/10', score: '18/20', time: '12:30', status: 'Đạt', statusClass: 'g' },
  { testName: 'Logic suy luận', date: '21/10', score: '12/20', time: '18:05', status: 'Khá', statusClass: '' },
  { testName: 'Đọc hiểu Verbal', date: '22/10', score: '8/20', time: '20:00', status: 'Luyện thêm', statusClass: 'a' }
];
