/* ============================================================
 * 入口：事件绑定与初始化
 * ============================================================ */
(function (W) {
  'use strict';

  const state = W.core.state;

  /* ---------- 键盘事件（捕获阶段拦截，避免页面滚动等默认行为） ---------- */
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;

    const k = e.key;

    if (k === ' ' || k === 'Enter' || k === 'Spacebar') {
      e.preventDefault();
      W.core.continueLocked();
      return;
    }

    if (k.length !== 1 || !/[a-zA-Z]/.test(k)) return;
    e.preventDefault();
    W.core.handleLetter(k.toUpperCase());
  }, { capture: true });

  window.addEventListener('keydown', (e) => {
    if (e.key === ' ') e.preventDefault();
  }, { passive: false });

  /* ---------- 点按题目区继续（触屏 / 鼠标，对应空格 / 回车） ---------- */
  W.ui.el.panelMain.addEventListener('click', () => W.core.continueLocked());

  /* ---------- 讲解卡弹窗（手机 / 触屏）：点按任意处关闭并继续下一题 ---------- */
  W.ui.el.teach.addEventListener('click', () => {
    if (matchMedia('(max-width: 680px), (pointer: coarse)').matches) {
      W.core.continueLocked();
    }
  });

  /* ---------- 模式切换 ---------- */
  document.querySelectorAll('.tab[data-mode]').forEach(tab => {
    tab.addEventListener('click', () => W.core.setMode(tab.dataset.mode));
  });

  /* ---------- 版本切换（86 / 98 / 新世纪） ---------- */
  document.querySelectorAll('.tab[data-ver]').forEach(tab => {
    tab.addEventListener('click', () => W.core.setVersion(tab.dataset.ver));
  });

  /* ---------- 重置统计 ---------- */
  document.getElementById('resetBtn').addEventListener('click', () => {
    W.core.resetStats();
    W.ui.updateStats();
    W.ui.setFeedback(true, '统计已重置');
    setTimeout(W.ui.clearFeedback, 900);
  });

  /* ---------- 初始化 ----------
     先恢复上次使用的版本，再建键盘（键名/提示随版本）与出题 */
  const ver0 = W.data.loadVersion();
  document.querySelectorAll('.tab[data-ver]').forEach(t => {
    t.classList.toggle('active', t.dataset.ver === ver0);
  });
  W.ui.buildKeyboard(W.core.handleLetter);
  W.ui.updateStats();
  W.core.setMode('root');
})(window.Wubi = window.Wubi || {});
