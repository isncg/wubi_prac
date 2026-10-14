/* ============================================================
 * UI 层：统计面板
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  W.ui.updateStats = function () {
    const state = W.core.state;
    const el = W.ui.el;
    const { right, wrong, streak, best } = state.stats;
    el.statRight.textContent  = right;
    el.statWrong.textContent  = wrong;
    el.statStreak.textContent = streak;
    el.statBest.textContent   = best;
    const total = right + wrong;
    el.statAcc.textContent = total === 0 ? '—' : Math.round(right / total * 100) + '%';
  };
})(window.Wubi = window.Wubi || {});
