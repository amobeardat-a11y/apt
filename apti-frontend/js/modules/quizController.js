/**
 * Bộ điều khiển Động cơ Luyện thi Trực tuyến (Quiz Engine) - APTI
 * Xử lý luồng làm bài thi, đếm ngược thời gian, chấm điểm Server (hoặc Offline), phân tích năng lực
 */

import { QUIZ_QUESTIONS, QUIZ_CATEGORIES } from '../data/quizQuestions.js';
import { MASCOT_QUOTES, INITIAL_TEST_HISTORY } from '../data/appData.js';
import { api } from '../services/apiClient.js';
import { toast } from './toastManager.js';
import { escapeHtml } from '../utils/sanitize.js';

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
    this.historyTableBody = document.getElementById('test-history-tbody');

    this.init();
  }

  async init() {
    this.renderCategoryTabs();
    this.renderHistoryTable();
    this.startQuiz();

    // Event listeners
    if (this.btnPrev) this.btnPrev.addEventListener('click', () => this.prevQuestion());
    if (this.btnNext) this.btnNext.addEventListener('click', () => this.nextQuestion());
    if (this.btnSubmit) this.btnSubmit.addEventListener('click', () => this.submitQuiz());
    if (this.btnHint) this.btnHint.addEventListener('click', () => this.toggleHint());
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
      this.questionCategoryChip.textContent = `${q.categoryName || 'Tổng hợp'} • ${q.level || 'Cơ bản'}`;
    }

    if (this.questionContentText) {
      this.questionContentText.textContent = q.question || q.question_text || '';
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
          <span>${escapeHtml(optText)}</span>
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
    this.mascot.say('Đã ghi nhận câu trả lời. Hãy tự tin tiến lên nhé!');
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
            ${escapeHtml(q.tip || 'Tập trung vào từ khóa và phân tích các dữ liệu đã cho.')}
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

  async submitQuiz(isTimeout = false) {
    clearInterval(this.timerInterval);
    this.isSubmitted = true;
    this.sound.playCelebration();

    const timeSpent = this.totalSeconds - this.remainingSeconds;

    // Check if Backend API is available for Server-side Grading
    let serverGraded = null;
    try {
      if (api.isOnline) {
        const answersList = this.activeQuestions.map(q => ({
          question_id: q.id,
          selected_index: this.userAnswers[q.id] !== undefined ? this.userAnswers[q.id] : -1
        }));
        const res = await api.submitQuiz(answersList, timeSpent, this.currentCategory);
        if (res && res.data) {
          serverGraded = res.data;
        }
      }
    } catch {
      // Fallback to local offline grading
    }

    if (serverGraded) {
      // Dùng kết quả chấm điểm từ Backend
      const totalCorrect = serverGraded.correct_answers;
      const totalQuestions = serverGraded.total_questions;
      const percentOverall = Math.round(serverGraded.score_percentage);

      const record = {
        testName: this.currentCategory === 'all' ? 'Tổng hợp MT Mock Test (Server)' : `Chuyên đề ${this.activeQuestions[0]?.categoryName || ''}`,
        date: new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
        score: `${totalCorrect}/${totalQuestions}`,
        time: `${Math.floor(timeSpent / 60)}:${String(timeSpent % 60).padStart(2, '0')}`,
        status: percentOverall >= 75 ? 'Đạt' : (percentOverall >= 50 ? 'Khá' : 'Luyện thêm'),
        statusClass: percentOverall >= 75 ? 'g' : (percentOverall >= 50 ? '' : 'a')
      };

      this.saveTestHistory(record);
      this.renderHistoryTable();
      this.renderServerResultsDashboard(serverGraded, isTimeout);
      this.mascot.say(serverGraded.mascot_message || MASCOT_QUOTES.goodJob);
    } else {
      // Chấm điểm Offline cục bộ
      this.gradeOffline(isTimeout);
    }
  }

  gradeOffline(isTimeout = false) {
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
    const timeSpent = this.totalSeconds - this.remainingSeconds;

    const record = {
      testName: this.currentCategory === 'all' ? 'Tổng hợp MT Mock Test' : `Chuyên đề ${this.activeQuestions[0]?.categoryName || ''}`,
      date: new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
      score: `${totalCorrect}/${totalQuestions}`,
      time: `${Math.floor(timeSpent / 60)}:${String(timeSpent % 60).padStart(2, '0')}`,
      status: percentOverall >= 75 ? 'Đạt' : (percentOverall >= 50 ? 'Khá' : 'Luyện thêm'),
      statusClass: percentOverall >= 75 ? 'g' : (percentOverall >= 50 ? '' : 'a')
    };

    this.saveTestHistory(record);
    this.renderHistoryTable();
    this.renderResultsDashboard(totalCorrect, totalQuestions, percentOverall, categoryStats, isTimeout);

    if (percentOverall >= 70) {
      this.mascot.say(MASCOT_QUOTES.goodJob);
    } else {
      this.mascot.say(MASCOT_QUOTES.needMorePractice);
    }
  }

  renderServerResultsDashboard(serverGraded, isTimeout) {
    if (this.quizPlayBox) this.quizPlayBox.style.display = 'none';
    if (!this.resultsDashboard) return;

    this.resultsDashboard.classList.add('active');
    this.resultsDashboard.style.display = 'block';
    this.resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const totalCorrect = serverGraded.correct_answers;
    const totalQuestions = serverGraded.total_questions;
    const percentOverall = Math.round(serverGraded.score_percentage);

    const reviews = serverGraded.reviews || [];
    const letters = ['A', 'B', 'C', 'D'];

    const reviewItemsHtml = reviews.map((r, idx) => {
      const isCorrect = r.is_correct;
      const userChoice = r.selected_index;
      const correctChoice = r.correct_index;

      return `
        <div class="card" style="margin-bottom:16px; border-left: 6px solid ${isCorrect ? 'var(--ok)' : 'var(--acc)'};">
          <div class="row" style="justify-content:space-between; margin-bottom:8px;">
            <span class="chip ${isCorrect ? 'g' : 'a'}">Câu ${idx + 1}: ${isCorrect ? 'Đúng' : 'Chưa đúng'}</span>
            <span style="font-size:13px; font-weight:800; color:var(--mut);">${escapeHtml(r.category_id || '')}</span>
          </div>
          <p style="font-weight:800; font-size:16px; margin: 8px 0 12px; color:var(--ink);">${escapeHtml(r.question_text)}</p>
          
          <div style="font-size:14px; margin-bottom:12px;">
            <div><b>Bạn chọn:</b> ${userChoice >= 0 && r.options[userChoice] ? `${letters[userChoice]}. ${escapeHtml(r.options[userChoice])}` : '<span style="color:var(--acc)">Chưa trả lời</span>'}</div>
            <div><b>Đáp án chính xác:</b> <span style="color:var(--ok); font-weight:800;">${letters[correctChoice]}. ${escapeHtml(r.options[correctChoice] || '')}</span></div>
          </div>

          <div class="toast toast-info" style="font-size:13.5px; margin-top:8px;">
            <div>
              <b>Phân tích bản chất:</b> ${escapeHtml(r.explanation)}<br>
              <span style="color:var(--pri); font-weight:700;">${escapeHtml(r.tip || '')}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    this.renderDashboardTemplate(totalCorrect, totalQuestions, percentOverall, reviewItemsHtml, isTimeout);
  }

  renderResultsDashboard(totalCorrect, totalQuestions, percentOverall, categoryStats, isTimeout) {
    if (this.quizPlayBox) this.quizPlayBox.style.display = 'none';
    if (!this.resultsDashboard) return;

    this.resultsDashboard.classList.add('active');
    this.resultsDashboard.style.display = 'block';
    this.resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    const letters = ['A', 'B', 'C', 'D'];
    const reviewItemsHtml = this.activeQuestions.map((q, idx) => {
      const userChoice = this.userAnswers[q.id];
      const isCorrect = userChoice === q.correctIndex;

      return `
        <div class="card" style="margin-bottom:16px; border-left: 6px solid ${isCorrect ? 'var(--ok)' : 'var(--acc)'};">
          <div class="row" style="justify-content:space-between; margin-bottom:8px;">
            <span class="chip ${isCorrect ? 'g' : 'a'}">Câu ${idx + 1}: ${isCorrect ? 'Đúng' : 'Chưa đúng'}</span>
            <span style="font-size:13px; font-weight:800; color:var(--mut);">${escapeHtml(q.categoryName || '')}</span>
          </div>
          <p style="font-weight:800; font-size:16px; margin: 8px 0 12px; color:var(--ink);">${escapeHtml(q.question)}</p>
          
          <div style="font-size:14px; margin-bottom:12px;">
            <div><b>Bạn chọn:</b> ${userChoice !== undefined ? `${letters[userChoice]}. ${escapeHtml(q.options[userChoice])}` : '<span style="color:var(--acc)">Chưa trả lời</span>'}</div>
            <div><b>Đáp án chính xác:</b> <span style="color:var(--ok); font-weight:800;">${letters[q.correctIndex]}. ${escapeHtml(q.options[q.correctIndex])}</span></div>
          </div>

          <div class="toast toast-info" style="font-size:13.5px; margin-top:8px;">
            <div>
              <b>Phân tích bản chất:</b> ${escapeHtml(q.explanation)}<br>
              <span style="color:var(--pri); font-weight:700;">${escapeHtml(q.tip || '')}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    this.renderDashboardTemplate(totalCorrect, totalQuestions, percentOverall, reviewItemsHtml, isTimeout);
  }

  renderDashboardTemplate(totalCorrect, totalQuestions, percentOverall, reviewItemsHtml, isTimeout) {
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

      <!-- Danh sách lời giải chi tiết -->
      <h3 style="font-size:22px; font-weight:900; margin:0 0 16px;">Chi Tiết Từng Câu Hỏi & Lời Giải Bản Chất</h3>
      <div class="review-questions-list">
        ${reviewItemsHtml}
      </div>
    `;

    const restartBtn = document.getElementById('btn-restart-dashboard');
    if (restartBtn) {
      restartBtn.addEventListener('click', () => {
        this.sound.playPop();
        this.startQuiz();
      });
    }
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
        <td><b>${escapeHtml(item.testName)}</b></td>
        <td>${escapeHtml(item.date)}</td>
        <td><span style="font-weight:800; color:var(--pri);">${escapeHtml(item.score)}</span></td>
        <td>${escapeHtml(item.time)}</td>
        <td><span class="chip ${escapeHtml(item.statusClass || '')}">${escapeHtml(item.status)}</span></td>
      </tr>
    `).join('');
  }
}
