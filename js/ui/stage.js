/* ============================================================
 * UI 层：题目区渲染（大字 + 编码槽位）与面板反馈
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  /* 渲染当前题目 */
  W.ui.renderStage = function () {
    const state = W.core.state;
    const el = W.ui.el;

    if (state.mode === 'root') {
      if (!state.current) { el.rootDisplay.textContent = '—'; return; }
      el.rootDisplay.textContent = state.current.root;
      el.rootDisplay.classList.remove('pop');
      void el.rootDisplay.offsetWidth;
      el.rootDisplay.classList.add('pop');
      return;
    }

    if (!state.current) { el.charDisplay.textContent = '—'; el.slots.innerHTML = ''; return; }
    el.charDisplay.textContent = state.current.c;
    el.charDisplay.classList.remove('pop');
    void el.charDisplay.offsetWidth;
    el.charDisplay.classList.add('pop');

    const code = state.current.code;
    el.slots.innerHTML = '';
    for (let i = 0; i < code.length; i++) {
      const d = document.createElement('div');
      d.className = 'slot';
      const t = state.typed[i];

      if (t !== undefined) {
        d.textContent = t;
        d.classList.add(t === code[i] ? 'ok' : 'bad');
      } else if (state.locked && state.waitingContinue) {
        d.textContent = code[i];
        d.classList.add('reveal');
      } else if (i === state.typed.length && !state.locked) {
        d.classList.add('next');
      }
      el.slots.appendChild(d);
    }
  };

  /* 面板抖动（答错反馈） */
  W.ui.shakePanel = function () {
    const el = W.ui.el;
    el.panel.classList.remove('shake');
    void el.panel.offsetWidth;
    el.panel.classList.add('shake');
  };
})(window.Wubi = window.Wubi || {});
