/**
 * APTI Frontend Entry Point
 * Khởi tạo toàn bộ các hệ thống thành phần (Components & Services)
 */

import { ThemeManager } from './modules/themeManager.js';
import { MascotInteractive } from './modules/mascotInteractive.js';
import { SoundEffects } from './modules/soundEffects.js';
import { QuizController } from './modules/quizController.js';
import { UIInteractions } from './modules/uiInteractions.js';
import { AuthController } from './modules/authController.js';
import { adminCtrl } from './modules/adminController.js';
import { toast } from './modules/toastManager.js';
import { api } from './services/apiClient.js';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Audio Sound FX
  const soundEffects = new SoundEffects();

  // 2. Mascot Em Tee Controller
  const mascot = new MascotInteractive();

  // 3. Theme Manager (Dark / Light)
  const themeManager = new ThemeManager((msg) => mascot.say(msg));

  // 4. Interactive Quiz Studio Controller
  const quizController = new QuizController(mascot, soundEffects);

  // 5. General UI Interactions (FAQ, Modals, Menus, VietQR)
  const uiInteractions = new UIInteractions(mascot, soundEffects);

  // 6. User Auth & Profile Controller
  const authController = new AuthController(
    mascot,
    soundEffects,
    (html) => uiInteractions.openModal(html),
    () => uiInteractions.closeModal()
  );
  window.aptiAuthController = authController;
  window.aptiAdminController = adminCtrl;

  // Global sound effect on interactive buttons
  document.querySelectorAll('button:not([data-nosound]), .btn').forEach(btn => {
    btn.addEventListener('click', () => {
      soundEffects.playPop();
    });
  });

  // Check backend health & notify
  api.checkHealth().then(isUp => {
    if (isUp) {
      console.log('APTI Backend API is ONLINE (FastAPI + Neon PostgreSQL).');
    } else {
      console.log('APTI Frontend running in seamless Offline Mode.');
    }
  });

  console.log('APTI Frontend App initialized successfully.');
});
