/* ============================================================
 * UI 层：结果反馈文案
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  W.ui.setFeedback = function (ok, msg) {
    const el = W.ui.el;
    el.feedback.className = 'feedback ' + (ok ? 'ok' : 'bad');
    el.feedback.textContent = msg;
  };

  W.ui.clearFeedback = function () {
    const el = W.ui.el;
    el.feedback.className = 'feedback';
    el.feedback.textContent = '';
  };
})(window.Wubi = window.Wubi || {});
