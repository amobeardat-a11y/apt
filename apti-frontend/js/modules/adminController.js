/**
 * APTI Admin Control Hub Controller
 * Quản trị toàn diện: Ngân hàng câu hỏi (1,000+), Đề thi thử (Exams), Lộ trình (Roadmaps), và Banners.
 */

import { api } from '../services/apiClient.js';
import { toast } from './toastManager.js';
import { sound } from './soundEffects.js';
import { escapeHtml } from '../utils/sanitize.js';

export class AdminController {
  constructor() {
    this.modal = null;
    this.currentTab = 'questions'; // 'questions', 'exams', 'roadmaps', 'banners'
    this.qPage = 1;
    this.qPageSize = 15;
    this.qCategory = 'all';
    this.qLevel = 'all';
    this.qSearch = '';

    this.initEventListeners();
  }

  initEventListeners() {
    // Lắng nghe sự kiện click mở Admin Hub từ header hoặc profile
    document.addEventListener('click', (e) => {
      const target = e.target.closest('#header-admin-btn, #profile-open-admin-btn');
      if (target) {
        sound.playPop();
        this.openAdminHub();
      }
    });
  }

  async openAdminHub() {
    const user = api.getCurrentUser();
    if (!user || user.role !== 'ADMIN') {
      toast.error('Từ chối truy cập: Bạn cần có quyền Quản trị viên (ADMIN).');
      return;
    }

    if (!this.modal) {
      this.createAdminModal();
    }

    this.modal.classList.add('on');
    document.body.style.overflow = 'hidden';
    await this.loadStats();
    await this.switchTab(this.currentTab);
  }

  closeAdminHub() {
    if (this.modal) {
      this.modal.classList.remove('on');
      document.body.style.overflow = '';
    }
  }

  createAdminModal() {
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal-backdrop admin-modal-backdrop';
    modalDiv.id = 'admin-hub-modal';

    modalDiv.innerHTML = `
      <div class="modal-card admin-hub-card" style="max-width:1100px; width:95%; max-height:90vh; display:flex; flex-direction:column; padding:0; overflow:hidden;">
        
        <!-- ADMIN HEADER -->
        <div class="admin-header" style="background:var(--ink); color:#fff; padding:18px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:3px solid var(--acc);">
          <div style="display:flex; align-items:center; gap:12px;">
            <div style="width:40px; height:40px; border-radius:12px; background:var(--pri); display:flex; align-items:center; justify-content:center; font-size:22px;">
              🛠️
            </div>
            <div>
              <div style="font-size:20px; font-weight:900; letter-spacing:-0.5px;">APTI Admin Control Hub</div>
              <div style="font-size:12px; opacity:0.8; font-weight:700;">Hệ thống quản trị Ngân hàng câu hỏi • Đề thi • Lộ trình • Banner</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:12px;">
            <span class="chip a" style="font-size:11px; padding:4px 10px;">Role: SUPER ADMIN</span>
            <button class="btn b-ghost b-sm admin-close-btn" style="color:#fff; font-size:20px; line-height:1; padding:6px 10px;" title="Đóng">✕</button>
          </div>
        </div>

        <!-- KPI SUMMARY BAR -->
        <div id="admin-kpi-bar" style="background:var(--mist); padding:12px 24px; display:flex; gap:16px; border-bottom:1px solid var(--card-border); overflow-x:auto;">
          <div class="kpi-mini-card" style="background:#fff; padding:8px 14px; border-radius:10px; border:1px solid var(--card-border); min-width:140px;">
            <div style="font-size:11px; color:var(--mut); font-weight:800;">TỔNG CÂU HỎI</div>
            <div id="kpi-total-questions" style="font-size:18px; font-weight:900; color:var(--pri);">1,050</div>
          </div>
          <div class="kpi-mini-card" style="background:#fff; padding:8px 14px; border-radius:10px; border:1px solid var(--card-border); min-width:140px;">
            <div style="font-size:11px; color:var(--mut); font-weight:800;">ĐỀ THI MOCK TEST</div>
            <div id="kpi-total-exams" style="font-size:18px; font-weight:900; color:var(--mint);">5</div>
          </div>
          <div class="kpi-mini-card" style="background:#fff; padding:8px 14px; border-radius:10px; border:1px solid var(--card-border); min-width:140px;">
            <div style="font-size:11px; color:var(--mut); font-weight:800;">LỘ TRÌNH ÔN TẬP</div>
            <div id="kpi-total-roadmaps" style="font-size:18px; font-weight:900; color:var(--warn);">2</div>
          </div>
          <div class="kpi-mini-card" style="background:#fff; padding:8px 14px; border-radius:10px; border:1px solid var(--card-border); min-width:140px;">
            <div style="font-size:11px; color:var(--mut); font-weight:800;">BANNER QUẢNG BÁ</div>
            <div id="kpi-total-banners" style="font-size:18px; font-weight:900; color:var(--acc);">3</div>
          </div>
        </div>

        <!-- NAVIGATION TABS -->
        <div class="admin-tabs" style="display:flex; border-bottom:2px solid var(--card-border); background:#fff; padding:0 24px;">
          <button class="admin-tab-btn on" data-tab="questions" style="padding:14px 18px; font-weight:800; font-size:14px; border:none; background:none; cursor:pointer; border-bottom:3px solid var(--pri); color:var(--pri);">
            ❓ Ngân hàng Câu hỏi
          </button>
          <button class="admin-tab-btn" data-tab="exams" style="padding:14px 18px; font-weight:800; font-size:14px; border:none; background:none; cursor:pointer; color:var(--mut);">
            📝 Quản lý Đề thi
          </button>
          <button class="admin-tab-btn" data-tab="roadmaps" style="padding:14px 18px; font-weight:800; font-size:14px; border:none; background:none; cursor:pointer; color:var(--mut);">
            🗺️ Lộ trình học
          </button>
          <button class="admin-tab-btn" data-tab="banners" style="padding:14px 18px; font-weight:800; font-size:14px; border:none; background:none; cursor:pointer; color:var(--mut);">
            📢 Banner thông báo
          </button>
        </div>

        <!-- MAIN BODY CONTENT -->
        <div class="admin-tab-content" id="admin-main-view" style="flex:1; overflow-y:auto; padding:20px 24px; background:#fff;">
          <!-- Loaded dynamically -->
        </div>

      </div>
    `;

    document.body.appendChild(modalDiv);
    this.modal = modalDiv;

    // Close handlers
    modalDiv.querySelector('.admin-close-btn').addEventListener('click', () => this.closeAdminHub());
    modalDiv.addEventListener('click', (e) => {
      if (e.target === modalDiv) this.closeAdminHub();
    });

    // Tab buttons
    modalDiv.querySelectorAll('.admin-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        sound.playPop();
        const tab = btn.dataset.tab;
        this.switchTab(tab);
      });
    });
  }

  async loadStats() {
    try {
      const res = await api.adminGetStats();
      if (res && res.data) {
        const d = res.data;
        const qEl = document.getElementById('kpi-total-questions');
        const eEl = document.getElementById('kpi-total-exams');
        const rEl = document.getElementById('kpi-total-roadmaps');
        const bEl = document.getElementById('kpi-total-banners');
        if (qEl) qEl.textContent = (d.total_questions_bank || 1050).toLocaleString('vi-VN');
        if (eEl) eEl.textContent = d.total_exams || 5;
        if (rEl) rEl.textContent = d.total_roadmaps || 2;
        if (bEl) bEl.textContent = d.total_banners || 3;
      }
    } catch (e) {
      console.warn('Không thể tải admin stats:', e);
    }
  }

  async switchTab(tab) {
    this.currentTab = tab;
    if (!this.modal) return;

    // Update tab bar styles
    this.modal.querySelectorAll('.admin-tab-btn').forEach(btn => {
      if (btn.dataset.tab === tab) {
        btn.classList.add('on');
        btn.style.color = 'var(--pri)';
        btn.style.borderBottom = '3px solid var(--pri)';
      } else {
        btn.classList.remove('on');
        btn.style.color = 'var(--mut)';
        btn.style.borderBottom = 'none';
      }
    });

    const view = document.getElementById('admin-main-view');
    view.innerHTML = `<div style="text-align:center; padding:40px;"><div class="spinner"></div><p style="margin-top:12px; color:var(--mut);">Đang tải dữ liệu...</p></div>`;

    if (tab === 'questions') {
      await this.renderQuestionsTab();
    } else if (tab === 'exams') {
      await this.renderExamsTab();
    } else if (tab === 'roadmaps') {
      await this.renderRoadmapsTab();
    } else if (tab === 'banners') {
      await this.renderBannersTab();
    }
  }

  // =========================================================================
  // TAB 1: QUESTIONS MANAGEMENT (1000+ CÂU HỎI)
  // =========================================================================

  async renderQuestionsTab() {
    const view = document.getElementById('admin-main-view');
    try {
      const res = await api.adminGetQuestions(
        this.qPage,
        this.qPageSize,
        this.qCategory,
        this.qLevel,
        this.qSearch
      );

      const data = res?.data || { items: [], total: 0, page: 1, total_pages: 1 };
      const questions = data.items || [];

      view.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- TOOLBAR -->
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <input type="text" id="admin-q-search" class="inp" placeholder="🔍 Tìm câu hỏi hoặc lời giải..." value="${escapeHtml(this.qSearch)}" style="width:240px; padding:8px 12px; font-size:13px;">
              
              <select id="admin-q-cat" class="inp" style="width:140px; padding:8px; font-size:13px;">
                <option value="all" ${this.qCategory === 'all' ? 'selected' : ''}>Tất cả danh mục</option>
                <option value="numerical" ${this.qCategory === 'numerical' ? 'selected' : ''}>Số học</option>
                <option value="logical" ${this.qCategory === 'logical' ? 'selected' : ''}>Logic</option>
                <option value="verbal" ${this.qCategory === 'verbal' ? 'selected' : ''}>Ngôn ngữ</option>
                <option value="abstract" ${this.qCategory === 'abstract' ? 'selected' : ''}>Hình ảnh</option>
              </select>

              <select id="admin-q-lvl" class="inp" style="width:130px; padding:8px; font-size:13px;">
                <option value="all" ${this.qLevel === 'all' ? 'selected' : ''}>Tất cả độ khó</option>
                <option value="Cơ bản" ${this.qLevel === 'Cơ bản' ? 'selected' : ''}>Cơ bản</option>
                <option value="Thực tế" ${this.qLevel === 'Thực tế' ? 'selected' : ''}>Thực tế</option>
                <option value="Suy luận" ${this.qLevel === 'Suy luận' ? 'selected' : ''}>Suy luận</option>
                <option value="Nâng cao" ${this.qLevel === 'Nâng cao' ? 'selected' : ''}>Nâng cao</option>
              </select>

              <button class="btn b-sec b-sm" id="admin-q-filter-btn" style="padding:8px 14px;">Lọc</button>
            </div>

            <button class="btn b-pri b-sm" id="admin-btn-add-question" style="display:flex; align-items:center; gap:6px;">
              <span>+ Thêm câu hỏi mới</span>
            </button>
          </div>

          <!-- QUESTIONS TABLE -->
          <div style="overflow-x:auto; border:1px solid var(--card-border); border-radius:12px;">
            <table style="width:100%; border-collapse:collapse; font-size:13px; text-align:left;">
              <thead style="background:var(--mist); color:var(--ink); font-weight:800; border-bottom:1px solid var(--card-border);">
                <tr>
                  <th style="padding:10px 12px; width:50px;">ID</th>
                  <th style="padding:10px 12px; width:90px;">Danh mục</th>
                  <th style="padding:10px 12px; width:80px;">Mức độ</th>
                  <th style="padding:10px 12px;">Nội dung câu hỏi</th>
                  <th style="padding:10px 12px; width:130px;">Đáp án đúng</th>
                  <th style="padding:10px 12px; width:70px;">Gói</th>
                  <th style="padding:10px 12px; width:100px; text-align:center;">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                ${questions.length === 0 ? `<tr><td colspan="7" style="padding:30px; text-align:center; color:var(--mut);">Không tìm thấy câu hỏi phù hợp.</td></tr>` : ''}
                ${questions.map(q => {
                  const correctText = q.options && q.options[q.correct_index] ? q.options[q.correct_index] : `Phương án ${q.correct_index + 1}`;
                  return `
                    <tr style="border-bottom:1px solid var(--card-border);">
                      <td style="padding:10px 12px; font-weight:800; color:var(--mut);">#${q.id}</td>
                      <td style="padding:10px 12px;"><span class="chip" style="font-size:10.5px; padding:2px 6px;">${escapeHtml(q.category_id)}</span></td>
                      <td style="padding:10px 12px;"><span class="chip g" style="font-size:10.5px; padding:2px 6px;">${escapeHtml(q.level)}</span></td>
                      <td style="padding:10px 12px; max-width:380px;">
                        <div style="font-weight:700; color:var(--ink); line-height:1.35; max-height:40px; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(q.question_text)}</div>
                      </td>
                      <td style="padding:10px 12px; font-weight:800; color:var(--mint);">${escapeHtml(correctText)}</td>
                      <td style="padding:10px 12px;">
                        ${q.is_premium ? '<span class="chip a" style="font-size:10px;">Pro</span>' : '<span style="color:var(--mut); font-size:11px;">Free</span>'}
                      </td>
                      <td style="padding:10px 12px; text-align:center;">
                        <div style="display:flex; justify-content:center; gap:6px;">
                          <button class="btn b-out b-sm btn-edit-q" data-id="${q.id}" style="padding:4px 8px; font-size:11px;" title="Chỉnh sửa">Sửa</button>
                          <button class="btn b-ghost b-sm btn-del-q" data-id="${q.id}" style="padding:4px 8px; font-size:11px; color:#e53e3e;" title="Xóa">Xóa</button>
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <!-- PAGINATION -->
          <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 0;">
            <div style="font-size:12.5px; color:var(--mut); font-weight:700;">
              Hiển thị ${(data.page - 1) * this.qPageSize + 1} - ${Math.min(data.page * this.qPageSize, data.total)} trong tổng số <strong>${data.total.toLocaleString('vi-VN')}</strong> câu hỏi
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
              <button class="btn b-out b-sm" id="admin-q-prev-btn" ${data.page <= 1 ? 'disabled' : ''} style="padding:4px 10px;">◀ Trước</button>
              <span style="font-size:13px; font-weight:800; padding:0 6px;">Trang ${data.page} / ${data.total_pages || 1}</span>
              <button class="btn b-out b-sm" id="admin-q-next-btn" ${data.page >= data.total_pages ? 'disabled' : ''} style="padding:4px 10px;">Sau ▶</button>
            </div>
          </div>
        </div>
      `;

      // Filter events
      const searchInp = document.getElementById('admin-q-search');
      const catSelect = document.getElementById('admin-q-cat');
      const lvlSelect = document.getElementById('admin-q-lvl');
      const filterBtn = document.getElementById('admin-q-filter-btn');

      const applyFilters = () => {
        this.qSearch = searchInp.value.trim();
        this.qCategory = catSelect.value;
        this.qLevel = lvlSelect.value;
        this.qPage = 1;
        this.renderQuestionsTab();
      };

      filterBtn.addEventListener('click', applyFilters);
      searchInp.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') applyFilters();
      });

      // Pagination events
      const prevBtn = document.getElementById('admin-q-prev-btn');
      const nextBtn = document.getElementById('admin-q-next-btn');
      if (prevBtn) {
        prevBtn.addEventListener('click', () => {
          if (this.qPage > 1) {
            this.qPage--;
            this.renderQuestionsTab();
          }
        });
      }
      if (nextBtn) {
        nextBtn.addEventListener('click', () => {
          if (this.qPage < data.total_pages) {
            this.qPage++;
            this.renderQuestionsTab();
          }
        });
      }

      // Add question button
      document.getElementById('admin-btn-add-question').addEventListener('click', () => {
        sound.playPop();
        this.openQuestionFormModal(null);
      });

      // Edit & Delete handlers
      view.querySelectorAll('.btn-edit-q').forEach(btn => {
        btn.addEventListener('click', () => {
          sound.playPop();
          const qId = parseInt(btn.dataset.id);
          const question = questions.find(item => item.id === qId);
          if (question) this.openQuestionFormModal(question);
        });
      });

      view.querySelectorAll('.btn-del-q').forEach(btn => {
        btn.addEventListener('click', async () => {
          sound.playPop();
          const qId = parseInt(btn.dataset.id);
          if (confirm(`Bạn có chắc chắn muốn xóa câu hỏi #${qId}?`)) {
            try {
              await api.adminDeleteQuestion(qId);
              toast.success(`Đã xóa câu hỏi #${qId} thành công!`);
              await this.loadStats();
              await this.renderQuestionsTab();
            } catch (err) {
              toast.error(err.message || 'Lỗi khi xóa câu hỏi');
            }
          }
        });
      });

    } catch (err) {
      view.innerHTML = `<div class="card" style="color:#e53e3e; text-align:center;">Lỗi tải dữ liệu: ${escapeHtml(err.message)}</div>`;
    }
  }

  openQuestionFormModal(existingQuestion = null) {
    const isEdit = !!existingQuestion;
    const formModal = document.createElement('div');
    formModal.className = 'modal-backdrop on';
    formModal.style.zIndex = '10001';

    const opts = existingQuestion?.options || ['', '', '', ''];
    while (opts.length < 4) opts.push('');

    formModal.innerHTML = `
      <div class="modal-card" style="max-width:650px; width:90%; max-height:85vh; overflow-y:auto; padding:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h3 style="margin:0; font-size:18px; font-weight:900;">${isEdit ? `Sửa câu hỏi #${existingQuestion.id}` : 'Thêm câu hỏi mới'}</h3>
          <button class="btn b-ghost b-sm q-form-close" style="font-size:18px; padding:4px 8px;">✕</button>
        </div>

        <form id="admin-q-form" onsubmit="return false;">
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
            <div>
              <label>Danh mục</label>
              <select class="inp" id="form-q-cat" required>
                <option value="numerical" ${existingQuestion?.category_id === 'numerical' ? 'selected' : ''}>Số học (Numerical)</option>
                <option value="logical" ${existingQuestion?.category_id === 'logical' ? 'selected' : ''}>Logic (Logical)</option>
                <option value="verbal" ${existingQuestion?.category_id === 'verbal' ? 'selected' : ''}>Ngôn ngữ (Verbal)</option>
                <option value="abstract" ${existingQuestion?.category_id === 'abstract' ? 'selected' : ''}>Hình ảnh (Abstract)</option>
              </select>
            </div>
            <div>
              <label>Mức độ</label>
              <select class="inp" id="form-q-level" required>
                <option value="Cơ bản" ${existingQuestion?.level === 'Cơ bản' ? 'selected' : ''}>Cơ bản</option>
                <option value="Thực tế" ${existingQuestion?.level === 'Thực tế' ? 'selected' : ''}>Thực tế</option>
                <option value="Suy luận" ${existingQuestion?.level === 'Suy luận' ? 'selected' : ''}>Suy luận</option>
                <option value="Nâng cao" ${existingQuestion?.level === 'Nâng cao' ? 'selected' : ''}>Nâng cao</option>
              </select>
            </div>
          </div>

          <div style="margin-bottom:12px;">
            <label>Nội dung câu hỏi</label>
            <textarea class="inp" id="form-q-text" rows="3" required placeholder="Nhập đề bài câu hỏi trắc nghiệm...">${escapeHtml(existingQuestion?.question_text || '')}</textarea>
          </div>

          <div style="margin-bottom:12px;">
            <label style="display:block; margin-bottom:6px;">4 Phương án lựa chọn (Chọn nút tròn để chỉ định đáp án ĐÚNG):</label>
            <div style="display:flex; flex-direction:column; gap:8px;">
              ${[0, 1, 2, 3].map(i => `
                <div style="display:flex; align-items:center; gap:8px;">
                  <input type="radio" name="form-q-correct" value="${i}" ${existingQuestion ? (existingQuestion.correct_index === i ? 'checked' : '') : (i === 0 ? 'checked' : '')} style="width:18px; height:18px; cursor:pointer;" title="Chọn làm đáp án đúng">
                  <span style="font-weight:800; width:20px;">${String.fromCharCode(65 + i)}:</span>
                  <input type="text" class="inp form-q-opt" value="${escapeHtml(opts[i] || '')}" required placeholder="Phương án ${String.fromCharCode(65 + i)}..." style="flex:1;">
                </div>
              `).join('')}
            </div>
          </div>

          <div style="margin-bottom:12px;">
            <label>Lời giải chi tiết</label>
            <textarea class="inp" id="form-q-expl" rows="3" required placeholder="Phân tích vì sao phương án này là đúng...">${escapeHtml(existingQuestion?.explanation || '')}</textarea>
          </div>

          <div style="margin-bottom:12px;">
            <label>Mẹo làm bài thi nhanh (Tips)</label>
            <input type="text" class="inp" id="form-q-tip" placeholder="Ví dụ: Mẹo MT: Ước lượng hàng đơn vị..." value="${escapeHtml(existingQuestion?.tip || '')}">
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
            <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
              <input type="checkbox" id="form-q-premium" ${existingQuestion?.is_premium ? 'checked' : ''} style="width:16px; height:16px;">
              <span>Câu hỏi chỉ dành cho Hội viên Pro (Premium)</span>
            </label>
            <div style="display:flex; align-items:center; gap:6px;">
              <label>Thời gian (giây):</label>
              <input type="number" id="form-q-time" value="${existingQuestion?.time_limit_seconds || 90}" style="width:70px;" class="inp" min="30" max="300">
            </div>
          </div>

          <div style="display:flex; justify-content:flex-end; gap:10px;">
            <button type="button" class="btn b-out b-sm q-form-close">Hủy</button>
            <button type="submit" class="btn b-pri b-sm"><span>${isEdit ? 'Lưu thay đổi' : 'Tạo câu hỏi'}</span></button>
          </div>
        </form>
      </div>
    `;

    document.body.appendChild(formModal);

    const close = () => formModal.remove();
    formModal.querySelectorAll('.q-form-close').forEach(b => b.addEventListener('click', close));

    formModal.querySelector('#admin-q-form').addEventListener('submit', async () => {
      sound.playPop();
      const cat = formModal.querySelector('#form-q-cat').value;
      const lvl = formModal.querySelector('#form-q-level').value;
      const text = formModal.querySelector('#form-q-text').value.trim();
      const expl = formModal.querySelector('#form-q-expl').value.trim();
      const tip = formModal.querySelector('#form-q-tip').value.trim();
      const isPrem = formModal.querySelector('#form-q-premium').checked;
      const time = parseInt(formModal.querySelector('#form-q-time').value) || 90;

      const optInputs = formModal.querySelectorAll('.form-q-opt');
      const options = Array.from(optInputs).map(inp => inp.value.trim());

      const radio = formModal.querySelector('input[name="form-q-correct"]:checked');
      const correctIdx = radio ? parseInt(radio.value) : 0;

      if (!text || options.some(o => !o) || !expl) {
        toast.error('Vui lòng điền đầy đủ đề bài, 4 đáp án và lời giải!');
        return;
      }

      const payload = {
        category_id: cat,
        level: lvl,
        question_text: text,
        options,
        correct_index: correctIdx,
        explanation: expl,
        tip: tip || null,
        is_premium: isPrem,
        time_limit_seconds: time
      };

      try {
        if (isEdit) {
          await api.adminUpdateQuestion(existingQuestion.id, payload);
          toast.success(`Cập nhật câu hỏi #${existingQuestion.id} thành công!`);
        } else {
          await api.adminCreateQuestion(payload);
          toast.success('Đã thêm câu hỏi mới thành công!');
        }
        close();
        await this.loadStats();
        await this.renderQuestionsTab();
      } catch (err) {
        toast.error(err.message || 'Lỗi khi lưu câu hỏi');
      }
    });
  }

  // =========================================================================
  // TAB 2: EXAMS MANAGEMENT (QUẢN LÝ ĐỀ THI)
  // =========================================================================

  async renderExamsTab() {
    const view = document.getElementById('admin-main-view');
    try {
      const res = await api.adminGetExams();
      const exams = res?.data || [];

      view.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h4 style="margin:0; font-size:16px; font-weight:800;">Danh sách Đề thi thử năng lực (Mock Tests)</h4>
              <p style="margin:4px 0 0; font-size:13px; color:var(--mut);">Mô phỏng áp lực phòng thi Unilever, Nestlé, SHL và Aon</p>
            </div>
            <button class="btn b-pri b-sm" id="admin-btn-add-exam"><span>+ Tạo đề thi mới</span></button>
          </div>

          <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:16px;">
            ${exams.map(e => `
              <div class="card" style="padding:16px; border:1px solid var(--card-border); display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                    <span class="chip" style="font-size:11px;">#${e.id} • ${e.category_id ? escapeHtml(e.category_id) : 'Tổng hợp'}</span>
                    ${e.is_premium ? '<span class="chip a" style="font-size:10px;">VIP</span>' : '<span class="chip g" style="font-size:10px;">Free</span>'}
                  </div>
                  <h5 style="margin:0 0 6px; font-size:15px; font-weight:900; color:var(--ink); line-height:1.3;">${escapeHtml(e.title)}</h5>
                  <p style="font-size:12.5px; color:var(--mut); margin:0 0 12px; line-height:1.4;">${escapeHtml(e.description)}</p>
                </div>
                <div style="border-top:1px dashed var(--card-border); padding-top:10px; display:flex; justify-content:space-between; align-items:center;">
                  <div style="font-size:12px; font-weight:800; color:var(--pri);">
                    ⏱️ ${e.time_limit_minutes} phút • 📊 ${e.questions_count || (e.question_ids ? e.question_ids.length : 0)} câu
                  </div>
                  <button class="btn b-ghost b-sm btn-del-exam" data-id="${e.id}" style="color:#e53e3e; font-size:12px; padding:4px 8px;">Xóa</button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;

      document.getElementById('admin-btn-add-exam').addEventListener('click', () => {
        sound.playPop();
        this.openExamFormModal();
      });

      view.querySelectorAll('.btn-del-exam').forEach(btn => {
        btn.addEventListener('click', async () => {
          sound.playPop();
          const eId = parseInt(btn.dataset.id);
          if (confirm(`Xác nhận xóa đề thi #${eId}?`)) {
            try {
              await api.adminDeleteExam(eId);
              toast.success(`Đã xóa đề thi #${eId}`);
              await this.loadStats();
              await this.renderExamsTab();
            } catch (err) {
              toast.error(err.message || 'Lỗi khi xóa đề thi');
            }
          }
        });
      });

    } catch (err) {
      view.innerHTML = `<div class="card" style="color:#e53e3e;">Lỗi tải đề thi: ${escapeHtml(err.message)}</div>`;
    }
  }

  openExamFormModal() {
    const formModal = document.createElement('div');
    formModal.className = 'modal-backdrop on';
    formModal.style.zIndex = '10001';

    formModal.innerHTML = `
      <div class="modal-card" style="max-width:550px; width:90%; padding:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h3 style="margin:0; font-size:18px; font-weight:900;">Tạo đề thi mới (Mock Exam)</h3>
          <button class="btn b-ghost b-sm exam-form-close">✕</button>
        </div>

        <form id="admin-exam-form" onsubmit="return false;">
          <div style="margin-bottom:12px;">
            <label>Tên đề thi</label>
            <input type="text" class="inp" id="form-e-title" required placeholder="Ví dụ: Đề thi thử SHL Numerical 2026...">
          </div>
          <div style="margin-bottom:12px;">
            <label>Mô tả đề thi</label>
            <textarea class="inp" id="form-e-desc" rows="2" required placeholder="Mô tả các dạng câu hỏi và đối tượng..."></textarea>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
            <div>
              <label>Danh mục</label>
              <select class="inp" id="form-e-cat">
                <option value="">Tổng hợp (Tất cả)</option>
                <option value="numerical">Số học</option>
                <option value="logical">Logic</option>
                <option value="verbal">Ngôn ngữ</option>
                <option value="abstract">Hình ảnh</option>
              </select>
            </div>
            <div>
              <label>Thời gian (phút)</label>
              <input type="number" class="inp" id="form-e-time" value="30" min="5" max="120" required>
            </div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:14px;">
            <div>
              <label>Điểm chuẩn đậu (%)</label>
              <input type="number" class="inp" id="form-e-pass" value="70" min="10" max="100">
            </div>
            <div>
              <label>Số câu bốc ngẫu nhiên từ ngân hàng</label>
              <input type="number" class="inp" id="form-e-count" value="20" min="5" max="50">
            </div>
          </div>

          <div style="margin-bottom:18px;">
            <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
              <input type="checkbox" id="form-e-premium">
              <span>Đề thi dành riêng cho tài khoản MT Master (Pro)</span>
            </label>
          </div>

          <div style="display:flex; justify-content:flex-end; gap:10px;">
            <button type="button" class="btn b-out b-sm exam-form-close">Hủy</button>
            <button type="submit" class="btn b-pri b-sm"><span>Tạo đề thi</span></button>
          </div>
        </form>
      </div>
    `;

    document.body.appendChild(formModal);
    const close = () => formModal.remove();
    formModal.querySelectorAll('.exam-form-close').forEach(b => b.addEventListener('click', close));

    formModal.querySelector('#admin-exam-form').addEventListener('submit', async () => {
      sound.playPop();
      const title = formModal.querySelector('#form-e-title').value.trim();
      const desc = formModal.querySelector('#form-e-desc').value.trim();
      const cat = formModal.querySelector('#form-e-cat').value || null;
      const time = parseInt(formModal.querySelector('#form-e-time').value) || 30;
      const pass = parseFloat(formModal.querySelector('#form-e-pass').value) || 70.0;
      const count = parseInt(formModal.querySelector('#form-e-count').value) || 20;
      const isPrem = formModal.querySelector('#form-e-premium').checked;

      try {
        await api.adminCreateExam({
          title,
          description: desc,
          category_id: cat,
          time_limit_minutes: time,
          passing_score: pass,
          is_premium: isPrem,
          random_count: count
        });
        toast.success('Đã tạo đề thi thử mới thành công!');
        close();
        await this.loadStats();
        await this.renderExamsTab();
      } catch (err) {
        toast.error(err.message || 'Lỗi khi tạo đề thi');
      }
    });
  }

  // =========================================================================
  // TAB 3: ROADMAPS MANAGEMENT (QUẢN LÝ LỘ TRÌNH)
  // =========================================================================

  async renderRoadmapsTab() {
    const view = document.getElementById('admin-main-view');
    try {
      const res = await api.adminGetRoadmaps();
      const roadmaps = res?.data || [];

      view.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h4 style="margin:0; font-size:16px; font-weight:800;">Lộ trình học tập cá nhân hóa (Roadmaps)</h4>
              <p style="margin:4px 0 0; font-size:13px; color:var(--mut);">Kế hoạch chi tiết theo tuần hướng dẫn học viên ôn thi có định hướng</p>
            </div>
            <button class="btn b-pri b-sm" id="admin-btn-add-roadmap"><span>+ Thêm lộ trình</span></button>
          </div>

          <div style="display:flex; flex-direction:column; gap:16px;">
            ${roadmaps.map(r => `
              <div class="card" style="padding:18px; border:1px solid var(--card-border);">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                  <div>
                    <span class="chip" style="font-size:11px; margin-bottom:4px;">ID: ${escapeHtml(r.id)}</span>
                    <h5 style="margin:4px 0; font-size:16px; font-weight:900; color:var(--ink);">${escapeHtml(r.title)}</h5>
                    <p style="margin:0; font-size:13px; color:var(--mut);">${escapeHtml(r.subtitle)}</p>
                  </div>
                  <div style="display:flex; gap:8px;">
                    <span class="chip g" style="font-size:11px;">${r.duration_weeks} Tuần</span>
                    <button class="btn b-ghost b-sm btn-del-roadmap" data-id="${r.id}" style="color:#e53e3e; font-size:12px; padding:4px 8px;">Xóa</button>
                  </div>
                </div>

                <div style="margin-top:12px; display:flex; flex-direction:column; gap:8px;">
                  ${(r.phases || []).map(p => `
                    <div style="background:var(--mist); padding:10px 14px; border-radius:8px; font-size:12.5px;">
                      <div style="font-weight:800; color:var(--pri);">${escapeHtml(p.title || `Tuần ${p.week}`)}</div>
                      <div style="color:var(--ink); margin-top:2px;">${escapeHtml(p.description || '')}</div>
                    </div>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;

      document.getElementById('admin-btn-add-roadmap').addEventListener('click', () => {
        sound.playPop();
        this.openRoadmapFormModal();
      });

      view.querySelectorAll('.btn-del-roadmap').forEach(btn => {
        btn.addEventListener('click', async () => {
          sound.playPop();
          const rId = btn.dataset.id;
          if (confirm(`Xác nhận xóa lộ trình '${rId}'?`)) {
            try {
              await api.adminDeleteRoadmap(rId);
              toast.success(`Đã xóa lộ trình ${rId}`);
              await this.loadStats();
              await this.renderRoadmapsTab();
            } catch (err) {
              toast.error(err.message || 'Lỗi khi xóa lộ trình');
            }
          }
        });
      });

    } catch (err) {
      view.innerHTML = `<div class="card" style="color:#e53e3e;">Lỗi tải lộ trình: ${escapeHtml(err.message)}</div>`;
    }
  }

  openRoadmapFormModal() {
    const formModal = document.createElement('div');
    formModal.className = 'modal-backdrop on';
    formModal.style.zIndex = '10001';

    formModal.innerHTML = `
      <div class="modal-card" style="max-width:550px; width:90%; padding:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h3 style="margin:0; font-size:18px; font-weight:900;">Thêm Lộ trình học tập mới</h3>
          <button class="btn b-ghost b-sm roadmap-form-close">✕</button>
        </div>

        <form id="admin-roadmap-form" onsubmit="return false;">
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
            <div>
              <label>Mã lộ trình (ID không dấu)</label>
              <input type="text" class="inp" id="form-r-id" required placeholder="mt-sprint-2w">
            </div>
            <div>
              <label>Số tuần</label>
              <input type="number" class="inp" id="form-r-weeks" value="4" min="1" max="16" required>
            </div>
          </div>

          <div style="margin-bottom:12px;">
            <label>Tiêu đề lộ trình</label>
            <input type="text" class="inp" id="form-r-title" required placeholder="Lộ trình 2 Tuần Nước Rút Unilever...">
          </div>

          <div style="margin-bottom:14px;">
            <label>Mô tả ngắn</label>
            <textarea class="inp" id="form-r-sub" rows="2" required placeholder="Dành cho ứng viên..."></textarea>
          </div>

          <div style="display:flex; justify-content:flex-end; gap:10px;">
            <button type="button" class="btn b-out b-sm roadmap-form-close">Hủy</button>
            <button type="submit" class="btn b-pri b-sm"><span>Tạo lộ trình</span></button>
          </div>
        </form>
      </div>
    `;

    document.body.appendChild(formModal);
    const close = () => formModal.remove();
    formModal.querySelectorAll('.roadmap-form-close').forEach(b => b.addEventListener('click', close));

    formModal.querySelector('#admin-roadmap-form').addEventListener('submit', async () => {
      sound.playPop();
      const id = formModal.querySelector('#form-r-id').value.trim();
      const weeks = parseInt(formModal.querySelector('#form-r-weeks').value) || 4;
      const title = formModal.querySelector('#form-r-title').value.trim();
      const sub = formModal.querySelector('#form-r-sub').value.trim();

      try {
        await api.adminCreateRoadmap({
          id,
          title,
          subtitle: sub,
          target_role: 'Management Trainee',
          duration_weeks: weeks,
          phases: [
            { week: 1, title: 'Tuần 1: Khởi động nền tảng', description: 'Ôn tập công thức số học và logic cơ bản.' },
            { week: 2, title: 'Tuần 2: Thi thử áp lực', description: 'Luyện đề mock test và tối ưu tốc độ.' }
          ]
        });
        toast.success('Đã thêm lộ trình học tập mới!');
        close();
        await this.loadStats();
        await this.renderRoadmapsTab();
      } catch (err) {
        toast.error(err.message || 'Lỗi khi tạo lộ trình');
      }
    });
  }

  // =========================================================================
  // TAB 4: BANNERS MANAGEMENT (QUẢN LÝ BANNER)
  // =========================================================================

  async renderBannersTab() {
    const view = document.getElementById('admin-main-view');
    try {
      const res = await api.adminGetBanners();
      const banners = res?.data || [];

      view.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h4 style="margin:0; font-size:16px; font-weight:800;">Banner thông báo & Sự kiện tuyển dụng</h4>
              <p style="margin:4px 0 0; font-size:13px; color:var(--mut);">Hiển thị trên trang chủ thông báo các đợt thi thử và ưu đãi</p>
            </div>
            <button class="btn b-pri b-sm" id="admin-btn-add-banner"><span>+ Thêm Banner</span></button>
          </div>

          <div style="display:flex; flex-direction:column; gap:14px;">
            ${banners.map(b => `
              <div class="card" style="padding:16px; border-radius:14px; background:${escapeHtml(b.bg_gradient)}; color:#fff; position:relative; overflow:hidden;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                  <span class="chip" style="background:rgba(255,255,255,0.25); color:#fff; font-size:11px; font-weight:800;">${escapeHtml(b.badge_text)}</span>
                  <button class="btn b-ghost b-sm btn-del-banner" data-id="${b.id}" style="color:#fff; background:rgba(0,0,0,0.2); padding:4px 8px; font-size:12px;">Xóa</button>
                </div>
                <h4 style="margin:8px 0 4px; font-size:18px; font-weight:900;">${escapeHtml(b.title)}</h4>
                <p style="margin:0 0 12px; font-size:13px; opacity:0.9; max-width:650px;">${escapeHtml(b.description)}</p>
                <div>
                  <span class="btn b-out b-sm" style="background:#fff; color:var(--ink); border:none; font-weight:800; font-size:12px; padding:6px 14px;">
                    ${escapeHtml(b.cta_text)} ➔
                  </span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;

      document.getElementById('admin-btn-add-banner').addEventListener('click', () => {
        sound.playPop();
        this.openBannerFormModal();
      });

      view.querySelectorAll('.btn-del-banner').forEach(btn => {
        btn.addEventListener('click', async () => {
          sound.playPop();
          const bId = parseInt(btn.dataset.id);
          if (confirm(`Xác nhận xóa Banner #${bId}?`)) {
            try {
              await api.adminDeleteBanner(bId);
              toast.success(`Đã xóa Banner #${bId}`);
              await this.loadStats();
              await this.renderBannersTab();
            } catch (err) {
              toast.error(err.message || 'Lỗi khi xóa banner');
            }
          }
        });
      });

    } catch (err) {
      view.innerHTML = `<div class="card" style="color:#e53e3e;">Lỗi tải banner: ${escapeHtml(err.message)}</div>`;
    }
  }

  openBannerFormModal() {
    const formModal = document.createElement('div');
    formModal.className = 'modal-backdrop on';
    formModal.style.zIndex = '10001';

    formModal.innerHTML = `
      <div class="modal-card" style="max-width:550px; width:90%; padding:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h3 style="margin:0; font-size:18px; font-weight:900;">Thêm Banner mới</h3>
          <button class="btn b-ghost b-sm banner-form-close">✕</button>
        </div>

        <form id="admin-banner-form" onsubmit="return false;">
          <div style="margin-bottom:12px;">
            <label>Tiêu đề Banner</label>
            <input type="text" class="inp" id="form-b-title" required placeholder="Ví dụ: Kỳ Thi Thử Unilever 2026...">
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
            <div>
              <label>Badge nhãn</label>
              <input type="text" class="inp" id="form-b-badge" value="SỰ KIỆN MỚI" required>
            </div>
            <div>
              <label>Nút kêu gọi (CTA)</label>
              <input type="text" class="inp" id="form-b-cta" value="Tham gia ngay" required>
            </div>
          </div>
          <div style="margin-bottom:12px;">
            <label>Nội dung mô tả</label>
            <textarea class="inp" id="form-b-desc" rows="2" required placeholder="Mô tả sự kiện hoặc ưu đãi..."></textarea>
          </div>
          <div style="margin-bottom:14px;">
            <label>Màu nền Gradient (CSS)</label>
            <select class="inp" id="form-b-gradient">
              <option value="linear-gradient(135deg, #5348CD 0%, #7B68EE 50%, #F54899 100%)">Tím Indigo ➔ Hồng Hot Pink</option>
              <option value="linear-gradient(135deg, #1FA97A 0%, #5348CD 100%)">Xanh Mint ➔ Tím Indigo</option>
              <option value="linear-gradient(135deg, #F54899 0%, #F5A524 100%)">Hồng Hot Pink ➔ Vàng Amber</option>
              <option value="linear-gradient(135deg, #1F2430 0%, #5348CD 100%)">Đen Huyền Bí ➔ Tím</option>
            </select>
          </div>
          <div style="display:flex; justify-content:flex-end; gap:10px;">
            <button type="button" class="btn b-out b-sm banner-form-close">Hủy</button>
            <button type="submit" class="btn b-pri b-sm"><span>Tạo Banner</span></button>
          </div>
        </form>
      </div>
    `;

    document.body.appendChild(formModal);
    const close = () => formModal.remove();
    formModal.querySelectorAll('.banner-form-close').forEach(b => b.addEventListener('click', close));

    formModal.querySelector('#admin-banner-form').addEventListener('submit', async () => {
      sound.playPop();
      const title = formModal.querySelector('#form-b-title').value.trim();
      const badge = formModal.querySelector('#form-b-badge').value.trim();
      const cta = formModal.querySelector('#form-b-cta').value.trim();
      const desc = formModal.querySelector('#form-b-desc').value.trim();
      const gradient = formModal.querySelector('#form-b-gradient').value;

      try {
        await api.adminCreateBanner({
          title,
          badge_text: badge,
          cta_text: cta,
          description: desc,
          bg_gradient: gradient,
          link_url: '#quiz-arena'
        });
        toast.success('Đã thêm Banner mới!');
        close();
        await this.loadStats();
        await this.renderBannersTab();
      } catch (err) {
        toast.error(err.message || 'Lỗi khi tạo banner');
      }
    });
  }
}

// Singleton export
export const adminCtrl = new AdminController();
