/**
 * Quản lý Trạng thái Xác thực & Modal Đăng nhập / Đăng ký - APTI
 */

import { api } from '../services/apiClient.js';
import { toast } from './toastManager.js';
import { escapeHtml } from '../utils/sanitize.js';

export class AuthController {
  constructor(mascot, sound, openModalFn, closeModalFn) {
    this.mascot = mascot;
    this.sound = sound;
    this.openModal = openModalFn;
    this.closeModal = closeModalFn;

    this.headerAuthContainer = document.getElementById('nav-auth-container');
    this.init();
  }

  init() {
    api.onAuthStateChange((user) => {
      this.renderHeaderAuth(user);
    });

    // Check current user from backend
    api.getMe().catch(() => {});
  }

  renderHeaderAuth(user) {
    if (!this.headerAuthContainer) return;
    this.headerAuthContainer.innerHTML = '';

    if (user) {
      // Đã đăng nhập
      const tierBadge = user.subscription_tier === 'MASTER_30D'
        ? '<span class="chip a" style="font-size:11px; padding:2px 8px;">MT Master</span>'
        : (user.subscription_tier === 'STARTER_7D'
          ? '<span class="chip" style="font-size:11px; padding:2px 8px;">Gói 7 Ngày</span>'
          : '<span class="chip g" style="font-size:11px; padding:2px 8px;">Free</span>');

      const userBtn = document.createElement('button');
      userBtn.className = 'btn b-soft b-sm nav-user-btn';
      userBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span class="user-name-text">${escapeHtml(user.full_name || user.email)}</span>
        ${tierBadge}
      `;
      userBtn.addEventListener('click', () => {
        this.sound.playPop();
        this.openProfileModal(user);
      });

      this.headerAuthContainer.appendChild(userBtn);
    } else {
      // Chưa đăng nhập (Guest)
      const loginBtn = document.createElement('button');
      loginBtn.className = 'btn b-out b-sm';
      loginBtn.innerHTML = `<span>Đăng nhập</span>`;
      loginBtn.addEventListener('click', () => {
        this.sound.playPop();
        this.openAuthModal('login');
      });

      this.headerAuthContainer.appendChild(loginBtn);
    }
  }

  openAuthModal(initialTab = 'login') {
    const modalHtml = `
      <div class="auth-modal-wrapper">
        <div class="tabs" style="justify-content:center; margin-bottom:20px;" id="auth-tab-switch">
          <button class="${initialTab === 'login' ? 'on' : ''}" id="tab-btn-login">Đăng nhập</button>
          <button class="${initialTab === 'register' ? 'on' : ''}" id="tab-btn-register">Đăng ký mới</button>
        </div>

        <!-- FORM ĐĂNG NHẬP -->
        <div id="auth-view-login" style="display:${initialTab === 'login' ? 'block' : 'none'};">
          <div style="text-align:center; margin-bottom:16px;">
            <h3 style="font-size:24px; font-weight:900; margin:0 0 6px; color:var(--ink);">Chào mừng bạn trở lại!</h3>
            <p style="color:var(--mut); font-size:14px; margin:0;">Tiếp tục hành trình rèn luyện Aptitude Test cùng APTI</p>
          </div>

          <form id="form-login" onsubmit="return false;">
            <div style="margin-bottom:14px;">
              <label>Email tài khoản</label>
              <input class="inp" type="email" id="login-email" placeholder="example@apti.vn" required autocomplete="username">
            </div>

            <div style="margin-bottom:18px;">
              <label>Mật khẩu</label>
              <input class="inp" type="password" id="login-password" placeholder="••••••••" required autocomplete="current-password">
            </div>

            <button type="submit" class="btn b-pri b-lg" style="width:100%; margin-bottom:16px;" id="btn-submit-login">
              <span>Đăng nhập ngay</span>
            </button>
          </form>

          <!-- TÀI KHOẢN MẪU ĐỂ TEST NHANH -->
          <div class="card" style="background:var(--pri-soft); border:1px dashed var(--pri); padding:12px; font-size:13px;">
            <div style="font-weight:800; color:var(--pri); margin-bottom:6px;">⚡ Tài khoản mẫu có sẵn (1-Click điền):</div>
            <div class="row" style="gap:8px; flex-wrap:wrap;">
              <button class="chip g" type="button" id="fill-student-btn" style="cursor:pointer;">
                👤 Học viên: student@apti.vn
              </button>
              <button class="chip a" type="button" id="fill-admin-btn" style="cursor:pointer;">
                🛡️ Admin: admin@apti.vn
              </button>
            </div>
          </div>
        </div>

        <!-- FORM ĐĂNG KÝ -->
        <div id="auth-view-register" style="display:${initialTab === 'register' ? 'block' : 'none'};">
          <div style="text-align:center; margin-bottom:16px;">
            <h3 style="font-size:24px; font-weight:900; margin:0 0 6px; color:var(--ink);">Tạo tài khoản học viên APTI</h3>
            <p style="color:var(--mut); font-size:14px; margin:0;">Bắt đầu từ con số 0 với trọn bộ bài tập & lời giải tiếng Việt</p>
          </div>

          <form id="form-register" onsubmit="return false;">
            <div style="margin-bottom:12px;">
              <label>Họ và tên của bạn</label>
              <input class="inp" id="reg-fullname" placeholder="Ví dụ: Nguyễn Văn An" required>
            </div>

            <div style="margin-bottom:12px;">
              <label>Email của bạn</label>
              <input class="inp" type="email" id="reg-email" placeholder="an.nguyen@gmail.com" required>
            </div>

            <div style="margin-bottom:12px;">
              <label>Mật khẩu</label>
              <input class="inp" type="password" id="reg-password" placeholder="Tối thiểu 8 ký tự, có hoa, số, ký tự đặc biệt" required>
            </div>

            <div id="reg-pwd-checklist" style="font-size:12px; margin-bottom:14px; padding:10px; background:var(--pri-soft); border-radius:var(--radius-md);">
              <div id="pwd-chk-len">⚪ Tối thiểu 8 ký tự</div>
              <div id="pwd-chk-case">⚪ Có chữ hoa (A-Z) và chữ thường (a-z)</div>
              <div id="pwd-chk-num">⚪ Có ít nhất một chữ số (0-9)</div>
              <div id="pwd-chk-spec">⚪ Có ký tự đặc biệt (!@#$%^&*...)</div>
            </div>

            <button type="submit" class="btn b-acc b-lg" style="width:100%; margin-bottom:12px;" id="btn-submit-register">
              <span>Tạo tài khoản miễn phí</span>
            </button>
          </form>
        </div>
      </div>
    `;

    this.openModal(modalHtml);
    this.setupAuthModalEvents();
  }

  setupAuthModalEvents() {
    const tabLogin = document.getElementById('tab-btn-login');
    const tabRegister = document.getElementById('tab-btn-register');
    const viewLogin = document.getElementById('auth-view-login');
    const viewRegister = document.getElementById('auth-view-register');

    if (tabLogin && tabRegister) {
      tabLogin.addEventListener('click', () => {
        this.sound.playPop();
        tabLogin.classList.add('on');
        tabRegister.classList.remove('on');
        viewLogin.style.display = 'block';
        viewRegister.style.display = 'none';
      });

      tabRegister.addEventListener('click', () => {
        this.sound.playPop();
        tabRegister.classList.add('on');
        tabLogin.classList.remove('on');
        viewRegister.style.display = 'block';
        viewLogin.style.display = 'none';
      });
    }

    // Nút điền nhanh tài khoản mẫu
    const fillStudent = document.getElementById('fill-student-btn');
    const fillAdmin = document.getElementById('fill-admin-btn');
    const loginEmailInp = document.getElementById('login-email');
    const loginPwdInp = document.getElementById('login-password');

    if (fillStudent) {
      fillStudent.addEventListener('click', () => {
        this.sound.playPop();
        if (loginEmailInp) loginEmailInp.value = 'student@apti.vn';
        if (loginPwdInp) loginPwdInp.value = 'Student@2026!';
        toast.info('Đã điền tài khoản Học viên mẫu.');
      });
    }

    if (fillAdmin) {
      fillAdmin.addEventListener('click', () => {
        this.sound.playPop();
        if (loginEmailInp) loginEmailInp.value = 'admin@apti.vn';
        if (loginPwdInp) loginPwdInp.value = 'Apti@2026Admin!';
        toast.info('Đã điền tài khoản Quản trị viên (Admin).');
      });
    }

    // Password strength check
    const regPwdInp = document.getElementById('reg-password');
    if (regPwdInp) {
      regPwdInp.addEventListener('input', () => {
        const val = regPwdInp.value;
        const hasLen = val.length >= 8;
        const hasCase = /[A-Z]/.test(val) && /[a-z]/.test(val);
        const hasNum = /\d/.test(val);
        const hasSpec = /[!@#$%^&*(),.?":{}|<>\-_]/.test(val);

        const updateItem = (id, valid) => {
          const el = document.getElementById(id);
          if (el) {
            el.innerHTML = valid ? `🟢 ${el.innerText.slice(2)}` : `⚪ ${el.innerText.slice(2)}`;
            el.style.color = valid ? 'var(--ok)' : 'var(--mut)';
          }
        };

        updateItem('pwd-chk-len', hasLen);
        updateItem('pwd-chk-case', hasCase);
        updateItem('pwd-chk-num', hasNum);
        updateItem('pwd-chk-spec', hasSpec);
      });
    }

    // Submit Login
    const formLogin = document.getElementById('form-login');
    if (formLogin) {
      formLogin.addEventListener('submit', async () => {
        const email = loginEmailInp?.value || '';
        const pwd = loginPwdInp?.value || '';
        if (!email || !pwd) {
          toast.warning('Vui lòng nhập đầy đủ Email và Mật khẩu.');
          return;
        }

        const btn = document.getElementById('btn-submit-login');
        if (btn) btn.disabled = true;

        try {
          await api.login(email, pwd);
          this.sound.playCelebration();
          toast.success('Đăng nhập thành công! Chào mừng bạn trở lại.');
          this.closeModal();
          this.mascot.say(`Chào bạn! Bạn đã đăng nhập thành công.`);
        } catch (err) {
          this.sound.playPop();
          toast.error(err.message || 'Đăng nhập không thành công.');
        } finally {
          if (btn) btn.disabled = false;
        }
      });
    }

    // Submit Register
    const formRegister = document.getElementById('form-register');
    if (formRegister) {
      formRegister.addEventListener('submit', async () => {
        const name = document.getElementById('reg-fullname')?.value || '';
        const email = document.getElementById('reg-email')?.value || '';
        const pwd = regPwdInp?.value || '';

        if (!name || !email || !pwd) {
          toast.warning('Vui lòng điền đầy đủ các thông tin đăng ký.');
          return;
        }

        const btn = document.getElementById('btn-submit-register');
        if (btn) btn.disabled = true;

        try {
          await api.register(email, name, pwd);
          // Tự động đăng nhập luôn sau khi đăng ký
          await api.login(email, pwd);
          this.sound.playCelebration();
          toast.success('Đăng ký tài khoản thành công! Bắt đầu học ngay.');
          this.closeModal();
          this.mascot.say(`Chào mừng ${name} đến với APTI!`);
        } catch (err) {
          this.sound.playPop();
          toast.error(err.message || 'Đăng ký không thành công.');
        } finally {
          if (btn) btn.disabled = false;
        }
      });
    }
  }

  openProfileModal(user) {
    const tierName = user.subscription_tier === 'MASTER_30D'
      ? 'Gói 30 Ngày (Chinh phục MT)'
      : (user.subscription_tier === 'STARTER_7D'
        ? 'Gói 7 Ngày (Khởi động)'
        : 'Tài khoản Miễn phí (Free)');

    const expiryText = user.subscription_expires_at
      ? new Date(user.subscription_expires_at).toLocaleDateString('vi-VN')
      : 'Không giới hạn bài mẫu';

    const modalHtml = `
      <div style="text-align:left;">
        <div class="row" style="gap:16px; margin-bottom:20px; align-items:center;">
          <div style="width:60px; height:60px; border-radius:50%; background:var(--pri); display:flex; align-items:center; justify-content:center; color:#fff; font-size:24px; font-weight:900;">
            ${escapeHtml(user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U')}
          </div>
          <div>
            <h3 style="font-size:22px; font-weight:900; margin:0 0 4px; color:var(--ink);">${escapeHtml(user.full_name)}</h3>
            <p style="color:var(--mut); margin:0; font-size:14px;">${escapeHtml(user.email)}</p>
          </div>
        </div>

        <div class="card" style="background:var(--pri-soft); border:1px solid rgba(83,72,205,0.2); margin-bottom:20px;">
          <div class="row" style="justify-content:space-between; margin-bottom:8px;">
            <span style="font-weight:800; font-size:13.5px; color:var(--pri);">Gói học hiện tại:</span>
            <span class="chip ${user.has_active_subscription ? 'a' : 'g'}">${escapeHtml(tierName)}</span>
          </div>
          <div class="row" style="justify-content:space-between; font-size:13px; color:var(--mut); font-weight:700;">
            <span>Thời hạn sử dụng:</span>
            <span>${escapeHtml(expiryText)}</span>
          </div>
        </div>

        <div class="row" style="justify-content:space-between; gap:12px;">
          ${!user.has_active_subscription ? `
            <a href="#goi-luyen-tap" class="btn b-acc" onclick="document.getElementById('modal-close-btn').click()">
              Nâng cấp gói ngay
            </a>
          ` : `
            <a href="#phong-luyen-tap" class="btn b-pri" onclick="document.getElementById('modal-close-btn').click()">
              Vào phòng luyện thi
            </a>
          `}
          
          <button class="btn b-out" id="btn-profile-logout" style="color:var(--acc); border-color:var(--acc);">
            Đăng xuất
          </button>
        </div>
      </div>
    `;

    this.openModal(modalHtml);

    setTimeout(() => {
      const logoutBtn = document.getElementById('btn-profile-logout');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
          this.sound.playPop();
          await api.logout();
          this.closeModal();
          toast.info('Bạn đã đăng xuất an toàn.');
          this.mascot.say('Hẹn gặp lại bạn sớm nhé.');
        });
      }
    }, 50);
  }
}

