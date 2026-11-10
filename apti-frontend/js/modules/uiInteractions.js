/**
 * Quản lý các tương tác giao diện người dùng (UI Interactions) - APTI
 * FAQ Accordion, Modal Xem trước tài liệu, Checkout VietQR, Toggle nhắc học, Mobile Menu
 */

import { FAQ_ITEMS, DOCUMENT_PACKS, PRICING_PLANS } from '../data/appData.js';
import { api } from '../services/apiClient.js';
import { toast } from './toastManager.js';
import { escapeHtml, formatVND } from '../utils/sanitize.js';

export class UIInteractions {
  constructor(mascot, sound) {
    this.mascot = mascot;
    this.sound = sound;

    this.faqContainer = document.getElementById('faq-accordion-container');
    this.modalOverlay = document.getElementById('app-modal-overlay');
    this.modalContentBody = document.getElementById('modal-content-body');
    this.modalCloseBtn = document.getElementById('modal-close-btn');
    this.dailyReminderToggle = document.getElementById('daily-reminder-toggle');
    this.mobileMenuBtn = document.getElementById('mobile-menu-btn');
    this.navMenu = document.getElementById('nav-menu');

    this.init();
  }

  init() {
    this.renderFAQ();
    this.setupModal();
    this.setupReminderToggle();
    this.setupMobileMenu();
    this.setupDocumentPreviews();
    this.setupPricingButtons();
    this.setupScrollSpy();
  }

  renderFAQ() {
    if (!this.faqContainer) return;
    this.faqContainer.innerHTML = '';

    FAQ_ITEMS.forEach((item, idx) => {
      const acc = document.createElement('div');
      acc.className = `accordion-item ${idx === 0 ? 'active' : ''}`;

      acc.innerHTML = `
        <div class="accordion-header">
          <span>${escapeHtml(item.q)}</span>
          <span class="accordion-icon">+</span>
        </div>
        <div class="accordion-body">
          <p>${escapeHtml(item.a)}</p>
        </div>
      `;

      acc.querySelector('.accordion-header').addEventListener('click', () => {
        this.sound.playPop();
        const wasActive = acc.classList.contains('active');
        
        // Close all
        this.faqContainer.querySelectorAll('.accordion-item').forEach(i => i.classList.remove('active'));

        if (!wasActive) {
          acc.classList.add('active');
        }
      });

      this.faqContainer.appendChild(acc);
    });
  }

  setupReminderToggle() {
    if (!this.dailyReminderToggle) return;
    const saved = localStorage.getItem('apti_daily_reminder');
    if (saved === 'false') {
      this.dailyReminderToggle.classList.remove('on');
    } else {
      this.dailyReminderToggle.classList.add('on');
    }

    this.dailyReminderToggle.addEventListener('click', () => {
      this.sound.playPop();
      const isOn = this.dailyReminderToggle.classList.toggle('on');
      localStorage.setItem('apti_daily_reminder', isOn ? 'true' : 'false');
      
      if (isOn) {
        toast.success('Đã bật tính năng nhắc luyện mỗi ngày lúc 20:00!');
        this.mascot.say('Đã bật tính năng nhắc luyện mỗi ngày. Em Tee sẽ đồng hành cùng bạn!');
      } else {
        toast.info('Đã tắt nhắc nhở luyện tập.');
        this.mascot.say('Đã tắt nhắc nhở. Nhớ tự giác vào luyện tập nhé!');
      }
    });
  }

  setupModal() {
    if (!this.modalOverlay) return;

    if (this.modalCloseBtn) {
      this.modalCloseBtn.addEventListener('click', () => this.closeModal());
    }

    this.modalOverlay.addEventListener('click', (e) => {
      if (e.target === this.modalOverlay) {
        this.closeModal();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modalOverlay.classList.contains('active')) {
        this.closeModal();
      }
    });
  }

  openModal(htmlContent) {
    if (!this.modalOverlay || !this.modalContentBody) return;
    this.sound.playPop();
    this.modalContentBody.innerHTML = htmlContent;
    this.modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  closeModal() {
    if (!this.modalOverlay) return;
    this.modalOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  setupDocumentPreviews() {
    document.querySelectorAll('[data-preview-pack]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const packId = btn.getAttribute('data-preview-pack');
        const pack = DOCUMENT_PACKS.find(p => p.id === packId) || DOCUMENT_PACKS[0];
        const user = api.getCurrentUser();
        const hasAccess = pack.id === 'pack-foundation' || (user && user.has_active_subscription);

        const previewHtml = `
          <div style="text-align:left;">
            <div class="row" style="justify-content:space-between; margin-bottom:12px;">
              <span class="chip a">${escapeHtml(pack.tag)}</span>
              <span style="font-size:13px; font-weight:800; color:var(--mut);">${escapeHtml(pack.pages)}</span>
            </div>
            <h3 style="font-size:24px; font-weight:900; margin:0 0 10px; color:var(--ink);">${escapeHtml(pack.title)}</h3>
            <p style="color:var(--mut); font-weight:600; line-height:1.6; margin:0 0 20px;">${escapeHtml(pack.desc)}</p>
            
            <div class="card" style="background:var(--pri-soft); border:1px solid rgba(83,72,205,0.2); margin-bottom:20px;">
              <h4 style="margin:0 0 8px; font-size:16px; font-weight:800; color:var(--pri);">Mục lục trích xuất mẫu:</h4>
              <ul style="margin:0; padding-left:20px; font-weight:700; font-size:14px; color:var(--ink); line-height:1.8;">
                <li>Chương 1: Giải mã bản chất câu hỏi và từ vựng MT cốt lõi</li>
                <li>Chương 2: 8 Mẹo tư duy xử lý số liệu siêu tốc (Mental Math Shortcuts)</li>
                <li>Chương 3: Phân tích 15 đề thi thực tế có giải thích tư duy tiếng Việt</li>
                <li>Chương 4: Bẫy câu hỏi thường gặp và chiến thuật phân bổ thời gian</li>
              </ul>
            </div>

            <div class="row" style="justify-content:space-between; align-items:center; gap:12px;">
              <button class="btn b-out" id="modal-btn-dismiss">Đóng</button>
              
              ${hasAccess ? `
                <button class="btn b-pri" id="btn-download-pdf-doc">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  <span>Tải tài liệu PDF ngay</span>
                </button>
              ` : `
                <a href="#goi-luyen-tap" class="btn b-acc" id="modal-btn-unlock-doc">
                  <span>Mở khóa toàn bộ tài liệu</span>
                </a>
              `}
            </div>
          </div>
        `;

        this.openModal(previewHtml);

        setTimeout(() => {
          const dismissBtn = document.getElementById('modal-btn-dismiss');
          if (dismissBtn) dismissBtn.addEventListener('click', () => this.closeModal());

          const unlockBtn = document.getElementById('modal-btn-unlock-doc');
          if (unlockBtn) unlockBtn.addEventListener('click', () => this.closeModal());

          const dlBtn = document.getElementById('btn-download-pdf-doc');
          if (dlBtn) {
            dlBtn.addEventListener('click', () => {
              this.sound.playCelebration();
              toast.success(`Đang tải xuống "${pack.title}"...`);
              this.mascot.say(`Tài liệu "${pack.title}" đã sẵn sàng cho bạn ôn tập!`);
            });
          }
        }, 50);
      });
    });
  }

  setupPricingButtons() {
    document.querySelectorAll('[data-plan-id]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const planId = btn.getAttribute('data-plan-id');
        const plan = PRICING_PLANS.find(p => p.id === planId) || PRICING_PLANS[0];

        // Ensure user is logged in before checkout (or provide instant guest account)
        let currentUser = api.getCurrentUser();
        if (!currentUser) {
          toast.info('Vui lòng đăng nhập hoặc chọn tài khoản học viên để kích hoạt gói.');
          // Mở modal auth
          const authTabBtn = document.getElementById('tab-btn-login');
          if (window.aptiAuthController) {
            window.aptiAuthController.openAuthModal('login');
          }
          return;
        }

        // Tạo mã đơn hàng VietQR
        const priceNum = planId === 'starter-7d' ? 99000 : 249000;
        const randHex = Math.random().toString(16).substring(2, 8).toUpperCase();
        const orderId = `APTI-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${randHex}`;
        const bankName = 'MB Bank (Ngân hàng Quân Đội)';
        const bankAccount = '982601289999';
        const accountHolder = 'CONG TY TNHH APTI VIET NAM';
        const transferSyntax = `APTI ${orderId}`;
        const qrUrl = `https://img.vietqr.io/image/MB-${bankAccount}-compact2.png?amount=${priceNum}&addInfo=${encodeURIComponent(transferSyntax)}&accountName=${encodeURIComponent(accountHolder)}`;

        // Thử tạo đơn qua API nếu backend online
        try {
          if (api.isOnline) {
            const serverOrder = await api.createOrder(planId);
            if (serverOrder && serverOrder.data) {
              // Sử dụng order trả về từ backend
            }
          }
        } catch {
          // Offline mode continues with client order
        }

        const checkoutHtml = `
          <div style="text-align:center;">
            <div class="row" style="justify-content:space-between; align-items:center; margin-bottom:12px;">
              <span class="chip a">${escapeHtml(plan.badge || 'Gói học')}</span>
              <span class="chip" style="font-size:12px;">Mã: ${escapeHtml(orderId)}</span>
            </div>

            <h3 style="font-size:24px; font-weight:900; margin:0 0 4px; color:var(--ink);">
              Kích Hoạt ${escapeHtml(plan.name)}
            </h3>
            <p style="color:var(--mut); font-weight:600; font-size:14px; margin:0 0 16px;">
              Quét mã VietQR Napas 24/7 để mở khóa bài học và tài liệu tức thì
            </p>

            <!-- Card chứa mã QR và thông tin chuyển khoản -->
            <div class="card" style="background:#FFFFFF; border:2px solid var(--pri); padding:16px; margin-bottom:16px; border-radius:var(--radius-lg); box-shadow:0 8px 24px rgba(83,72,205,0.12);">
              <div style="font-size:30px; font-weight:900; color:var(--pri); margin-bottom:12px;">
                ${formatVND(priceNum)} VNĐ
              </div>

              <!-- Ảnh VietQR -->
              <div style="display:inline-block; border-radius:var(--radius-md); overflow:hidden; border:1px solid var(--line); margin-bottom:14px;">
                <img src="${qrUrl}" alt="Mã VietQR Thanh toán" style="max-width:240px; height:auto; display:block;">
              </div>

              <!-- Chi tiết tài khoản -->
              <div style="text-align:left; font-size:13px; line-height:1.7; background:var(--pri-soft); padding:12px 14px; border-radius:var(--radius-md);">
                <div><b>Ngân hàng:</b> ${bankName}</div>
                <div class="row" style="justify-content:space-between; align-items:center;">
                  <span><b>Số tài khoản:</b> <span style="font-family:monospace; font-size:14px; color:var(--pri); font-weight:900;">${bankAccount}</span></span>
                  <button class="chip g" id="btn-copy-acc" style="cursor:pointer; font-size:11px;">Sao chép STK</button>
                </div>
                <div><b>Chủ tài khoản:</b> ${accountHolder}</div>
                <div class="row" style="justify-content:space-between; align-items:center;">
                  <span><b>Nội dung chuyển:</b> <span style="font-family:monospace; font-size:14px; color:var(--acc); font-weight:900;">${transferSyntax}</span></span>
                  <button class="chip a" id="btn-copy-syntax" style="cursor:pointer; font-size:11px;">Sao chép cú pháp</button>
                </div>
              </div>
            </div>

            <!-- Nút Giả lập thanh toán tức thì (Dành cho Dev / Test thử) -->
            <button class="btn b-acc b-lg" style="width:100%; margin-bottom:12px;" id="btn-simulate-payment">
              <span>⚡ Kích hoạt thử nghiệm ngay (Dev Sim)</span>
            </button>

            <p style="font-size:12px; color:var(--mut); margin:0;">
              🔒 Giao dịch được bảo vệ mã hóa. Sau khi chuyển khoản, gói học được kích hoạt tự động sau 1-3 giây.
            </p>
          </div>
        `;

        this.openModal(checkoutHtml);

        setTimeout(() => {
          // Copy STK
          const btnCopyAcc = document.getElementById('btn-copy-acc');
          if (btnCopyAcc) {
            btnCopyAcc.addEventListener('click', () => {
              this.sound.playPop();
              navigator.clipboard.writeText(bankAccount).then(() => {
                toast.success('Đã sao chép số tài khoản MB Bank!');
              });
            });
          }

          // Copy cú pháp
          const btnCopySyntax = document.getElementById('btn-copy-syntax');
          if (btnCopySyntax) {
            btnCopySyntax.addEventListener('click', () => {
              this.sound.playPop();
              navigator.clipboard.writeText(transferSyntax).then(() => {
                toast.success('Đã sao chép nội dung chuyển khoản!');
              });
            });
          }

          // Giả lập thanh toán thành công
          const btnSim = document.getElementById('btn-simulate-payment');
          if (btnSim) {
            btnSim.addEventListener('click', async () => {
              btnSim.disabled = true;
              btnSim.innerHTML = '<span>Đang kích hoạt gói học...</span>';

              try {
                if (api.isOnline) {
                  await api.simulatePaymentSuccess(orderId);
                } else {
                  // Giả lập offline
                  const u = api.getCurrentUser() || {};
                  u.subscription_tier = planId === 'starter-7d' ? 'STARTER_7D' : 'MASTER_30D';
                  u.has_active_subscription = true;
                  const expDate = new Date();
                  expDate.setDate(expDate.getDate() + (planId === 'starter-7d' ? 7 : 30));
                  u.subscription_expires_at = expDate.toISOString();
                  localStorage.setItem('apti_user_profile', JSON.stringify(u));
                  api.notifyAuthChange();
                }

                this.sound.playCelebration();
                toast.success(`Chúc mừng bạn! ${plan.name} đã được kích hoạt thành công.`);
                this.closeModal();
                this.mascot.say(`Tuyệt vời! Bạn đã nâng cấp lên ${plan.name}. Hãy vào làm bài ngay nhé!`);
              } catch (err) {
                toast.error(err.message || 'Lỗi khi kích hoạt.');
              }
            });
          }
        }, 50);
      });
    });
  }

  setupMobileMenu() {
    if (!this.mobileMenuBtn || !this.navMenu) return;

    this.mobileMenuBtn.addEventListener('click', () => {
      this.sound.playPop();
      const isVisible = this.navMenu.style.display === 'flex';
      this.navMenu.style.display = isVisible ? 'none' : 'flex';
      if (!isVisible) {
        this.navMenu.style.flexDirection = 'column';
        this.navMenu.style.position = 'absolute';
        this.navMenu.style.top = 'var(--nav-height)';
        this.navMenu.style.left = '0';
        this.navMenu.style.right = '0';
        this.navMenu.style.background = 'var(--card)';
        this.navMenu.style.padding = '20px';
        this.navMenu.style.boxShadow = '0 12px 28px rgba(0,0,0,0.15)';
        this.navMenu.style.borderBottom = '1px solid var(--line)';
      }
    });

    this.navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          this.navMenu.style.display = 'none';
        }
      });
    });
  }

  setupScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-menu .nav-link');

    window.addEventListener('scroll', () => {
      let current = '';
      const scrollPos = window.scrollY + 120;

      sections.forEach(sec => {
        const top = sec.offsetTop;
        const height = sec.offsetHeight;
        if (scrollPos >= top && scrollPos < top + height) {
          current = sec.getAttribute('id');
        }
      });

      navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
          link.classList.add('active');
        }
      });
    }, { passive: true });
  }
}
