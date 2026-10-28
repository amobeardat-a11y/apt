/**
 * APTI Frontend Entry Point
 * Khởi tạo toàn bộ các hệ thống thành phần (Components & Services)
 */

import { ThemeManager } from './modules/themeManager.js';
import { MascotInteractive } from './modules/mascotInteractive.js';
import { SoundEffects } from './modules/soundEffects.js';
import { QuizController } from './modules/quizController.js';
import { UIInteractions } from './modules/uiInteractions.js';

document.addEventListener('DOMContentLoaded', () => {
  // 1. Audio Sound FX
  const soundEffects = new SoundEffects();

  // 2. Mascot Em Tee Controller
  const mascot = new MascotInteractive();

  // 3. Theme Manager (Dark / Light)
  const themeManager = new ThemeManager((msg) => mascot.say(msg));

  // 4. Interactive Quiz Studio Controller
  const quizController = new QuizController(mascot, soundEffects);

  // 5. General UI Interactions (FAQ, Modals, Menus)
  const uiInteractions = new UIInteractions(mascot, soundEffects);

  // Global sound effect on generic buttons
  document.querySelectorAll('button:not([data-nosound]), .btn').forEach(btn => {
    btn.addEventListener('click', () => {
      soundEffects.playPop();
    });
  });

  console.log('APTI Frontend App initialized successfully.');
});
