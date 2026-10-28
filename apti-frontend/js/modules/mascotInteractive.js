/**
 * Quản lý tương tác Linh vật Em Tee (3D Star Mascot)
 * Thân thiện, Khích lệ, Không áp lực
 */

import { MASCOT_QUOTES } from '../data/appData.js';

export class MascotInteractive {
  constructor() {
    this.speechHero = document.getElementById('mascot-speech-hero');
    this.speechQuiz = document.getElementById('mascot-speech-quiz');
    this.heroMascotImg = document.getElementById('hero-mascot-img');
    this.quizMascotImg = document.getElementById('quiz-mascot-img');
    this.audioPop = null;

    this.init();
  }

  init() {
    // Say initial welcome
    this.say(MASCOT_QUOTES.welcome);

    // Click on hero mascot triggers fun speech
    if (this.heroMascotImg) {
      this.heroMascotImg.addEventListener('click', () => {
        const funQuotes = [
          'Bạn bấm vào mình kìa! Hôm nay cùng giải một vài bài logic nhé.',
          'Mỗi ngày luyện 15 phút, kỳ thi Management Trainee sẽ bớt bỡ ngỡ hơn.',
          'Nhớ đọc kỹ từ khóa trong đề Verbal nhé, bẫy thường giấu ở đó.',
          'Cứ làm từ tốn, hiểu bản chất mới là chìa khóa bứt phá.'
        ];
        const randomQuote = funQuotes[Math.floor(Math.random() * funQuotes.length)];
        this.say(randomQuote);
      });
    }

    if (this.quizMascotImg) {
      this.quizMascotImg.addEventListener('click', () => {
        this.say('Em Tee đang theo dõi sát bài làm của bạn đây, cố lên nhé.');
      });
    }
  }

  say(message) {
    [this.speechHero, this.speechQuiz].forEach(el => {
      if (el) {
        el.textContent = message;
        el.classList.remove('bubble-pop');
        // Force reflow
        void el.offsetWidth;
        el.classList.add('bubble-pop');
      }
    });
  }
}
