/**
 * APTI Frontend Security Utility
 * Triệt tiêu lỗ hổng Cross-Site Scripting (XSS) khi render dữ liệu động vào DOM
 */

export function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function formatVND(amount) {
  if (isNaN(amount)) return '0';
  return Number(amount).toLocaleString('vi-VN');
}

