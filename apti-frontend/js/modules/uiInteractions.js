/**
 * Quản lý các tương tác giao diện người dùng (UI Interactions)
 * FAQ Accordion, Modal Xem trước tài liệu, Toggle nhắc học, Mobile Menu
 */

import { FAQ_ITEMS, DOCUMENT_PACKS, PRICING_PLANS } from '../data/appData.js';

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
  }

  renderFAQ() {
    if (!this.faqContainer) return;
    this.faqContainer.innerHTML = '';

    FAQ_ITEMS.forEach((item, idx) => {
      const acc = document.createElement('div');
      acc.className = `accordion-item ${idx === 0 ? 'active' : ''}`;

      acc.innerHTML = `
        <div class="accordion-header">
          <span>${item.q}</span>
          <span class="accordion-icon">+</span>
        </div>
        <div class="accordion-body">
          <p>${item.a}</p>
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
        this.mascot.say('Đã bật tính năng nhắc luyện mỗi ngày.');
      } else {
        this.mascot.say('Đã tắt tính năng nhắc nhở.');
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
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const packId = btn.getAttribute('data-preview-pack');
        const pack = DOCUMENT_PACKS.find(p => p.id === packId) || DOCUMENT_PACKS[0];

        const previewHtml = `
          <div style="text-align:left;">
            <div class="row" style="justify-content:space-between; margin-bottom:12px;">
              <span class="chip a">${pack.tag}</span>
              <span style="font-size:13px; font-weight:800; color:var(--mut);">${pack.pages}</span>
            </div>
            <h3 style="font-size:24px; font-weight:900; margin:0 0 10px; color:var(--ink);">${pack.title}</h3>
            <p style="color:var(--mut); font-weight:600; line-height:1.6; margin:0 0 20px;">${pack.desc}</p>
            
            <div class="card" style="background:var(--pri-soft); border:1px solid rgba(83,72,205,0.2); margin-bottom:20px;">
              <h4 style="margin:0 0 8px; font-size:16px; font-weight:800; color:var(--pri);">Mục lục trích xuất mẫu:</h4>
              <ul style="margin:0; padding-left:20px; font-weight:700; font-size:14px; color:var(--ink); line-height:1.8;">
                <li>Chương 1: Giải mã bản chất câu hỏi và từ vựng MT cốt lõi</li>
                <li>Chương 2: 8 Mẹo tư duy xử lý số liệu siêu tốc (Mental Math Shortcuts)</li>
                <li>Chương 3: Phân tích 15 đề thi thực tế có giải thích tư duy tiếng Việt</li>
                <li>Chương 4: Bẫy câu hỏi thường gặp và chiến thuật phân bổ thời gian</li>
              </ul>
            </div>

            <div class="row" style="justify-content:flex-end; gap:12px;">
              <button class="btn b-out" onclick="document.getElementById('modal-close-btn').click()">Đóng</button>
              <a href="#goi-luyen-tap" class="btn b-acc" onclick="document.getElementById('modal-close-btn').click()">Khám phá trọn bộ</a>
            </div>
          </div>
        `;

        this.openModal(previewHtml);
      });
    });
  }

  setupPricingButtons() {
    document.querySelectorAll('[data-plan-id]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const planId = btn.getAttribute('data-plan-id');
        const plan = PRICING_PLANS.find(p => p.id === planId);
        if (!plan) return;

        const checkoutHtml = `
          <div style="text-align:center;">
            <div class="brand-icon-box" style="margin:0 auto 16px; width:48px; height:48px;">
              <svg width="24" height="24" style="color:#FFFFFF; flex:none;">
                <use href="#apti-symbol"/>
              </svg>
            </div>
            <span class="chip ${plan.popular ? 'a' : ''}" style="margin-bottom:10px;">${plan.badge}</span>
            <h3 style="font-size:26px; font-weight:900; margin:0 0 8px; color:var(--ink);">${plan.name}</h3>
            <p style="color:var(--mut); font-weight:600; margin:0 0 20px;">${plan.tagline}</p>
            
            <div style="font-size:36px; font-weight:900; color:var(--pri); margin-bottom:20px;">
              ${plan.price} VNĐ <span style="font-size:15px; color:var(--mut); font-weight:700;">/ ${plan.unit}</span>
            </div>

            <div class="card" style="text-align:left; margin-bottom:24px;">
              <label>Họ và tên của bạn</label>
              <input class="inp" placeholder="Ví dụ: Nguyễn Văn An" style="margin-bottom:12px;" id="reg-name">
              <label>Email nhận tài liệu & tài khoản</label>
              <input class="inp" type="email" placeholder="example@email.com" id="reg-email">
            </div>

            <button class="btn b-acc b-lg" style="width:100%; margin-bottom:12px;" id="btn-confirm-reg">
              Xác nhận đăng ký học
            </button>
            <p style="font-size:12.5px; color:var(--mut); margin:0;">
              Cam kết bảo mật thông tin và hoàn tiền nếu không hài lòng theo chính sách APTI.
            </p>
          </div>
        `;

        this.openModal(checkoutHtml);

        setTimeout(() => {
          const confirmBtn = document.getElementById('btn-confirm-reg');
          if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
              const nameInp = document.getElementById('reg-name');
              const name = nameInp?.value || 'Bạn';
              this.sound.playCelebration();
              this.closeModal();
              this.mascot.say(`Chào mừng ${name} đến với APTI.`);
            });
          }
        }, 100);
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

    // Close mobile menu on nav link click
    this.navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          this.navMenu.style.display = 'none';
        }
      });
    });
  }
}
