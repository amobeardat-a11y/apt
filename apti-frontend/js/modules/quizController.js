/**
 * Bộ điều khiển Động cơ Luyện thi Trực tuyến (Quiz Engine)
 * Xử lý luồng làm bài thi, đếm ngược thời gian, chấm điểm và phân tích năng lực
 */

import { QUIZ_QUESTIONS, QUIZ_CATEGORIES } from '../data/quizQuestions.js';
import { MASCOT_QUOTES, INITIAL_TEST_HISTORY } from '../data/appData.js';

export class QuizController {
  constructor(mascot, sound) {
    this.mascot = mascot;
    this.sound = sound;

    this.allQuestions = QUIZ_QUESTIONS;
    this.currentCategory = 'all';
    this.activeQuestions = [...this.allQuestions];
    this.currentIndex = 0;
    this.userAnswers = {}; // { questionId: optionIndex }
    this.isSubmitted = false;
    
    // Timer
    this.totalSeconds = 600; // 10 minutes
    this.remainingSeconds = this.totalSeconds;
    this.timerInterval = null;

    // DOM Elements
    this.quizPlayBox = document.getElementById('quiz-play-box');
    this.resultsDashboard = document.getElementById('results-dashboard');
    this.categoryTabsContainer = document.getElementById('quiz-category-tabs');
    this.questionProgressText = document.getElementById('question-progress-text');
    this.questionCategoryChip = document.getElementById('question-category-chip');
    this.questionContentText = document.getElementById('question-content-text');
    this.questionOptionsList = document.getElementById('question-options-list');
    this.questionStepsMap = document.getElementById('quiz-steps-map');
    this.timerDisplay = document.getElementById('quiz-timer-display');
    this.btnPrev = document.getElementById('btn-quiz-prev');
    this.btnNext = document.getElementById('btn-quiz-next');
    this.btnSubmit = document.getElementById('btn-quiz-submit');
    this.btnHint = document.getElementById('btn-quiz-hint');
    this.hintBox = document.getElementById('quiz-hint-box');
    this.btnRetake = document.getElementById('btn-retake-quiz');
    this.historyTableBody = document.getElementById('test-history-tbody');

    this.init();
  }

  init() {
    this.renderCategoryTabs();
    this.renderHistoryTable();
    this.startQuiz();

    // Event listeners
    if (this.btnPrev) this.btnPrev.addEventListener('click', () => this.prevQuestion());
    if (this.btnNext) this.btnNext.addEventListener('click', () => this.nextQuestion());
    if (this.btnSubmit) this.btnSubmit.addEventListener('click', () => this.submitQuiz());
    if (this.btnHint) this.btnHint.addEventListener('click', () => this.toggleHint());
    if (this.btnRetake) this.btnRetake.addEventListener('click', () => this.retakeQuiz());
  }

  renderCategoryTabs() {
    if (!this.categoryTabsContainer) return;
    this.categoryTabsContainer.innerHTML = '';
    
    QUIZ_CATEGORIES.forEach(cat => {
      const btn = document.createElement('button');
      btn.className = cat.id === this.currentCategory ? 'on' : '';
      btn.textContent = cat.name;
      btn.addEventListener('click', () => {
        this.sound.playPop();
        this.filterCategory(cat.id);
      });
      this.categoryTabsContainer.appendChild(btn);
    });
  }

  filterCategory(catId) {
    this.currentCategory = catId;
    this.renderCategoryTabs();

    if (catId === 'all') {
      this.activeQuestions = [...this.allQuestions];
    } else {
      this.activeQuestions = this.allQuestions.filter(q => q.category === catId);
    }

    this.currentIndex = 0;
    this.userAnswers = {};
    this.isSubmitted = false;
    this.resetTimer();
    this.showQuizPlayBox();
    this.renderQuestion();
  }

  startQuiz() {
    this.currentIndex = 0;
    this.userAnswers = {};
    this.isSubmitted = false;
    this.resetTimer();
    this.startTimer();
    this.showQuizPlayBox();
    this.renderQuestion();
    this.mascot.say(MASCOT_QUOTES.startQuiz);
  }

  resetTimer() {
    clearInterval(this.timerInterval);
    this.remainingSeconds = this.totalSeconds;
    this.updateTimerDisplay();
  }

  startTimer() {
    clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      if (this.remainingSeconds > 0) {
        this.remainingSeconds--;
        this.updateTimerDisplay();
      } else {
        clearInterval(this.timerInterval);
        this.submitQuiz(true);
      }
    }, 1000);
  }

  updateTimerDisplay() {
    if (!this.timerDisplay) return;
    const mins = Math.floor(this.remainingSeconds / 60);
    const secs = this.remainingSeconds % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    this.timerDisplay.textContent = formatted;

    const parent = this.timerDisplay.parentElement;
    if (this.remainingSeconds <= 60 && parent) {
      parent.classList.add('warning');
    } else if (parent) {
      parent.classList.remove('warning');
    }
  }

  showQuizPlayBox() {
    if (this.quizPlayBox) this.quizPlayBox.style.display = 'block';
    if (this.resultsDashboard) {
      this.resultsDashboard.classList.remove('active');
      this.resultsDashboard.style.display = 'none';
    }
  }

  renderQuestion() {
    const q = this.activeQuestions[this.currentIndex];
    if (!q) return;

    if (this.questionProgressText) {
      this.questionProgressText.textContent = `Câu ${this.currentIndex + 1}/${this.activeQuestions.length}`;
    }

    if (this.questionCategoryChip) {
      this.questionCategoryChip.textContent = `${q.categoryName} • ${q.level}`;
    }

    if (this.questionContentText) {
      this.questionContentText.textContent = q.question;
    }

    // Hide hint box on slide
    if (this.hintBox) {
      this.hintBox.style.display = 'none';
    }

    // Render options
    if (this.questionOptionsList) {
      this.questionOptionsList.innerHTML = '';
      const letters = ['A', 'B', 'C', 'D'];
      const currentSelected = this.userAnswers[q.id];

      q.options.forEach((optText, idx) => {
        const optDiv = document.createElement('div');
        optDiv.className = `opt ${currentSelected === idx ? 'sel' : ''}`;
        
        optDiv.innerHTML = `
          <i>${letters[idx]}</i>
          <span>${optText}</span>
        `;

        optDiv.addEventListener('click', () => {
          this.selectOption(q.id, idx);
        });

        this.questionOptionsList.appendChild(optDiv);
      });
    }

    // Nav button states
    if (this.btnPrev) {
      this.btnPrev.disabled = this.currentIndex === 0;
    }

    if (this.btnNext) {
      this.btnNext.style.display = this.currentIndex === this.activeQuestions.length - 1 ? 'none' : 'inline-flex';
    }

    if (this.btnSubmit) {
      this.btnSubmit.style.display = this.currentIndex === this.activeQuestions.length - 1 ? 'inline-flex' : 'none';
    }

    this.renderStepMap();
  }

  renderStepMap() {
    if (!this.questionStepsMap) return;
    this.questionStepsMap.innerHTML = '';

    this.activeQuestions.forEach((q, idx) => {
      const stepBtn = document.createElement('button');
      stepBtn.className = 'progress-step-btn';
      if (idx === this.currentIndex) stepBtn.classList.add('current');
      if (this.userAnswers[q.id] !== undefined) stepBtn.classList.add('answered');
      
      stepBtn.textContent = idx + 1;
      stepBtn.title = `Chuyển tới câu ${idx + 1}`;
      stepBtn.addEventListener('click', () => {
        this.sound.playPop();
        this.currentIndex = idx;
        this.renderQuestion();
      });

      this.questionStepsMap.appendChild(stepBtn);
    });
  }

  selectOption(questionId, optionIndex) {
    this.sound.playPop();
    this.userAnswers[questionId] = optionIndex;
    
    // Check instant mascot feedback
    const q = this.activeQuestions.find(item => item.id === questionId);
    if (q) {
      if (optionIndex === q.correctIndex) {
        this.mascot.say('Chính xác! Em Tee khen bạn đó.');
      } else {
        this.mascot.say('Đã ghi nhận câu trả lời của bạn.');
      }
    }

    this.renderQuestion();
  }

  toggleHint() {
    this.sound.playPop();
    if (!this.hintBox) return;
    const q = this.activeQuestions[this.currentIndex];
    if (!q) return;

    if (this.hintBox.style.display === 'block') {
      this.hintBox.style.display = 'none';
    } else {
      this.hintBox.style.display = 'block';
      this.hintBox.innerHTML = `
        <div class="toast toast-info" style="margin-top:0">
          <div>
            <b>Gợi ý tư duy:</b><br>
            ${q.tip}
          </div>
        </div>
      `;
      this.mascot.say('Gợi ý tư duy đã được hiển thị bên dưới.');
    }
  }

  prevQuestion() {
    if (this.currentIndex > 0) {
      this.sound.playPop();
      this.currentIndex--;
      this.renderQuestion();
    }
  }

  nextQuestion() {
    if (this.currentIndex < this.activeQuestions.length - 1) {
      this.sound.playPop();
      this.currentIndex++;
      this.renderQuestion();
    }
  }

  submitQuiz(isTimeout = false) {
    clearInterval(this.timerInterval);
    this.isSubmitted = true;
    this.sound.playCelebration();

    // Compute scores
    let totalCorrect = 0;
    const categoryStats = {
      numerical: { total: 0, correct: 0, name: 'Số học' },
      logical: { total: 0, correct: 0, name: 'Logic' },
      verbal: { total: 0, correct: 0, name: 'Ngôn ngữ' },
      abstract: { total: 0, correct: 0, name: 'Hình ảnh' }
    };

    this.activeQuestions.forEach(q => {
      const userChoice = this.userAnswers[q.id];
      const isCorrect = userChoice === q.correctIndex;
      if (isCorrect) totalCorrect++;

      const catKey = q.category;
      if (categoryStats[catKey]) {
        categoryStats[catKey].total++;
        if (isCorrect) categoryStats[catKey].correct++;
      }
    });

    const totalQuestions = this.activeQuestions.length;
    const percentOverall = Math.round((totalCorrect / totalQuestions) * 100);

    // Save history record
    const record = {
      testName: this.currentCategory === 'all' ? 'Tổng hợp MT Mock Test' : `Chuyên đề ${this.activeQuestions[0]?.categoryName || ''}`,
      date: new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
      score: `${totalCorrect}/${totalQuestions}`,
      time: `${Math.floor((this.totalSeconds - this.remainingSeconds) / 60)}:${String((this.totalSeconds - this.remainingSeconds) % 60).padStart(2, '0')}`,
      status: percentOverall >= 75 ? 'Đạt' : (percentOverall >= 50 ? 'Khá' : 'Luyện thêm'),
      statusClass: percentOverall >= 75 ? 'g' : (percentOverall >= 50 ? '' : 'a')
    };

    this.saveTestHistory(record);
    this.renderHistoryTable();

    // Render Dashboard
    this.renderResultsDashboard(totalCorrect, totalQuestions, percentOverall, categoryStats, isTimeout);

    // Mascot celebration
    if (percentOverall >= 70) {
      this.mascot.say(MASCOT_QUOTES.goodJob);
    } else {
      this.mascot.say(MASCOT_QUOTES.needMorePractice);
    }
  }

  renderResultsDashboard(totalCorrect, totalQuestions, percentOverall, categoryStats, isTimeout) {
    if (this.quizPlayBox) this.quizPlayBox.style.display = 'none';
    if (!this.resultsDashboard) return;

    this.resultsDashboard.classList.add('active');
    this.resultsDashboard.style.display = 'block';

    // Scroll to dashboard smoothly
    this.resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Compute rings %
    const numPercent = categoryStats.numerical.total > 0 
      ? Math.round((categoryStats.numerical.correct / categoryStats.numerical.total) * 100) 
      : 82; // Fallback demo
    const logPercent = categoryStats.logical.total > 0 
      ? Math.round((categoryStats.logical.correct / categoryStats.logical.total) * 100) 
      : 64;
    const verPercent = categoryStats.verbal.total > 0 
      ? Math.round((categoryStats.verbal.correct / categoryStats.verbal.total) * 100) 
      : 41;

    // Badges based on score
    const numStatus = numPercent >= 75 ? 'Rất tốt' : (numPercent >= 50 ? 'Khá' : 'Cần luyện thêm');
    const logStatus = logPercent >= 75 ? 'Rất tốt' : (logPercent >= 50 ? 'Khá' : 'Cần luyện thêm');
    const verStatus = verPercent >= 75 ? 'Rất tốt' : (verPercent >= 50 ? 'Khá' : 'Cần luyện thêm');

    const numColor = numPercent >= 75 ? 'var(--ok)' : (numPercent >= 50 ? 'var(--pri)' : 'var(--acc)');
    const logColor = logPercent >= 75 ? 'var(--ok)' : (logPercent >= 50 ? 'var(--pri)' : 'var(--acc)');
    const verColor = verPercent >= 75 ? 'var(--ok)' : (verPercent >= 50 ? 'var(--pri)' : 'var(--acc)');

    // Build Detailed Review Items
    const reviewItemsHtml = this.activeQuestions.map((q, idx) => {
      const userChoice = this.userAnswers[q.id];
      const isCorrect = userChoice === q.correctIndex;
      const letters = ['A', 'B', 'C', 'D'];

      return `
        <div class="card" style="margin-bottom:16px; border-left: 6px solid ${isCorrect ? 'var(--ok)' : 'var(--acc)'};">
          <div class="row" style="justify-content:space-between; margin-bottom:8px;">
            <span class="chip ${isCorrect ? 'g' : 'a'}">Câu ${idx + 1}: ${isCorrect ? 'Đúng' : 'Chưa đúng'}</span>
            <span style="font-size:13px; font-weight:800; color:var(--mut);">${q.categoryName}</span>
          </div>
          <p style="font-weight:800; font-size:16px; margin: 8px 0 12px; color:var(--ink);">${q.question}</p>
          
          <div style="font-size:14px; margin-bottom:12px;">
            <div><b>Bạn chọn:</b> ${userChoice !== undefined ? `${letters[userChoice]}. ${q.options[userChoice]}` : '<span style="color:var(--acc)">Chưa trả lời</span>'}</div>
            <div><b>Đáp án chính xác:</b> <span style="color:var(--ok); font-weight:800;">${letters[q.correctIndex]}. ${q.options[q.correctIndex]}</span></div>
          </div>

          <div class="toast toast-info" style="font-size:13.5px; margin-top:8px;">
            <div>
              <b>Phân tích bản chất:</b> ${q.explanation}<br>
              <span style="color:var(--pri); font-weight:700;">${q.tip}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    this.resultsDashboard.innerHTML = `
      <div class="results-celebrate-card">
        <span class="chip g" style="font-size:14px; padding:6px 18px; margin-bottom:14px;">
          ${isTimeout ? 'Đã hết thời gian làm bài' : 'Đã hoàn thành bài test'}
        </span>
        <h2 style="font-size:36px; font-weight:900; margin:10px 0 8px; color:var(--ink);">
          Kết Quả: ${totalCorrect}/${totalQuestions} Điểm (${percentOverall}%)
        </h2>
        <p style="color:var(--mut); font-weight:700; max-width:600px; margin:0 auto 20px;">
          ${percentOverall >= 75 
            ? 'Bạn đã thể hiện tư duy xử lý số liệu và suy luận rất nhạy bén! Bạn đã sẵn sàng cho vòng thi Aptitude Test thật!' 
            : 'Khởi đầu rất hứa hẹn! Hãy xem kỹ phần phân tích chi tiết bên dưới để nắm vững phương pháp và tối ưu tốc độ nhé!'}
        </p>

        <div class="row" style="justify-content:center; gap:14px;">
          <button class="btn b-pri" id="btn-restart-dashboard">
            <span>Làm lại bài test</span>
          </button>
          <a href="#tai-lieu" class="btn b-acc">
            <span>Xem bộ tài liệu</span>
          </a>
        </div>
      </div>

      <!-- 3 Vòng tròn kết quả chuẩn Brand Identity -->
      <h3 style="font-size:22px; font-weight:900; margin:0 0 6px; text-align:center;">Phân Tích Năng Lực Theo Từng Nhóm Kỹ Năng</h3>
      <p style="text-align:center; color:var(--mut); font-weight:600; font-size:14px; margin:0 0 24px;">
        Đánh giá trực quan mức độ thuần thục của bạn đối với 3 trụ cột đề thi Management Trainee
      </p>

      <div class="results-grid-summary">
        <div class="card card-hover" style="text-align:center;">
          <div class="ring" style="--p:${numPercent}; --c:${numColor};">
            <span>${numPercent}%</span>
          </div>
          <div class="ctr">
            Số học & Số liệu
            <small style="color:${numColor}; font-weight:800;">${numStatus}</small>
          </div>
        </div>

        <div class="card card-hover" style="text-align:center;">
          <div class="ring" style="--p:${logPercent}; --c:${logColor};">
            <span>${logPercent}%</span>
          </div>
          <div class="ctr">
            Tư duy Suy luận Logic
            <small style="color:${logColor}; font-weight:800;">${logStatus}</small>
          </div>
        </div>

        <div class="card card-hover" style="text-align:center;">
          <div class="ring" style="--p:${verPercent}; --c:${verColor};">
            <span>${verPercent}%</span>
          </div>
          <div class="ctr">
            Đọc hiểu Ngôn ngữ
            <small style="color:${verColor}; font-weight:800;">${verStatus}</small>
          </div>
        </div>
      </div>

      <!-- Biểu đồ & Thanh tiến độ -->
      <div class="grid g-2" style="margin-bottom:32px;">
        <div class="card">
          <div class="row" style="justify-content:space-between; margin-bottom:14px;">
            <b>Xu hướng điểm số theo tuần</b>
            <span class="chip">Tuần 1 - Tuần 5</span>
          </div>
          <svg viewBox="0 0 320 170" width="100%" aria-label="Biểu đồ tiến độ">
            <g stroke="var(--line)">
              <line x1="30" y1="20" x2="310" y2="20" stroke-dasharray="4"/>
              <line x1="30" y1="60" x2="310" y2="60" stroke-dasharray="4"/>
              <line x1="30" y1="100" x2="310" y2="100" stroke-dasharray="4"/>
              <line x1="30" y1="140" x2="310" y2="140"/>
            </g>
            <g fill="var(--mut)" font-size="11" font-family="Nunito">
              <text x="40" y="160">T1</text>
              <text x="100" y="160">T2</text>
              <text x="160" y="160">T3</text>
              <text x="220" y="160">T4</text>
              <text x="280" y="160">T5</text>
            </g>
            <polyline points="48,120 108,100 168,84 228,52 288,36" fill="none" stroke="var(--acc)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <g fill="var(--card)" stroke="var(--acc)" stroke-width="3">
              <circle cx="48" cy="120" r="5"/>
              <circle cx="108" cy="100" r="5"/>
              <circle cx="168" cy="84" r="5"/>
              <circle cx="228" cy="52" r="5"/>
              <circle cx="288" cy="36" r="5"/>
            </g>
          </svg>
        </div>

        <div class="card">
          <div class="row" style="justify-content:space-between; margin-bottom:14px;">
            <b>Phân bổ câu đúng theo dạng bài</b>
            <span class="chip a">Thực chiến</span>
          </div>
          <svg viewBox="0 0 320 170" width="100%" aria-label="Biểu đồ cột">
            <line x1="30" y1="140" x2="310" y2="140" stroke="var(--line)"/>
            <rect x="50" y="${140 - (numPercent * 0.9)}" width="38" height="${numPercent * 0.9}" rx="8" fill="var(--pri)"/>
            <rect x="110" y="${140 - (logPercent * 0.9)}" width="38" height="${logPercent * 0.9}" rx="8" fill="var(--pri)"/>
            <rect x="170" y="${140 - (verPercent * 0.9)}" width="38" height="${verPercent * 0.9}" rx="8" fill="var(--acc)"/>
            <rect x="230" y="60" width="38" height="80" rx="8" fill="var(--pri)"/>
            <g fill="var(--mut)" font-size="11" font-family="Nunito" text-anchor="middle">
              <text x="69" y="158">Số</text>
              <text x="129" y="158">Logic</text>
              <text x="189" y="158">Đọc</text>
              <text x="249" y="158">Hình</text>
            </g>
          </svg>
        </div>
      </div>

      <!-- Danh sách lời giải chi tiết -->
      <h3 style="font-size:22px; font-weight:900; margin:0 0 16px;">Chi Tiết Từng Câu Hỏi & Lời Giải Bản Chất</h3>
      <div class="review-questions-list">
        ${reviewItemsHtml}
      </div>
    `;

    const restartBtn = document.getElementById('btn-restart-dashboard');
    if (restartBtn) {
      restartBtn.addEventListener('click', () => this.retakeQuiz());
    }
  }

  retakeQuiz() {
    this.sound.playPop();
    this.startQuiz();
  }

  saveTestHistory(record) {
    let history = [];
    try {
      const saved = localStorage.getItem('apti_test_history');
      if (saved) history = JSON.parse(saved);
    } catch {
      history = [];
    }
    history.unshift(record);
    if (history.length > 8) history.pop();
    localStorage.setItem('apti_test_history', JSON.stringify(history));
  }

  getTestHistory() {
    try {
      const saved = localStorage.getItem('apti_test_history');
      if (saved) return JSON.parse(saved);
    } catch {
      // Fallback
    }
    return INITIAL_TEST_HISTORY;
  }

  renderHistoryTable() {
    if (!this.historyTableBody) return;
    const history = this.getTestHistory();
    this.historyTableBody.innerHTML = history.map(item => `
      <tr>
        <td><b>${item.testName}</b></td>
        <td>${item.date}</td>
        <td><span style="font-weight:800; color:var(--pri);">${item.score}</span></td>
        <td>${item.time}</td>
        <td><span class="chip ${item.statusClass}">${item.status}</span></td>
      </tr>
    `).join('');
  }
}
