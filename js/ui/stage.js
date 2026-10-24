/* ============================================================
 * UI 层：题目区渲染（大字 + 编码槽位 + 文章行）与面板反馈
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  /* 文章模式：单行文章内容——以当前字为中心开窗，两侧越界截断渐隐 */
  function renderTicker() {
    const state = W.core.state;
    const el = W.ui.el;
    const text = state.text;
    const pos  = state.textPos;

    if (!text) { el.textTicker.innerHTML = ''; return; }

    const HALF = 7;
    const start = Math.max(0, pos - HALF);
    const end   = Math.min(text.length, pos + HALF + 1);

    let html = start > 0 ? '<span class="tk-etc">…</span>' : '';
    for (let i = start; i < end; i++) {
      let cls = 'tk';
      if (!W.data.entryFor(text[i])) cls += ' skip';   /* 标点等无编码字符：淡化，自动跳过 */
      else if (i < pos) cls += ' done';
      else if (i === pos) cls += state.badChar ? ' cur bad' : ' cur';
      html += `<span class="${cls}">${text[i]}</span>`;
    }
    if (end < text.length) html += '<span class="tk-etc">…</span>';
    el.textTicker.innerHTML = html;
  }

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

    if (!state.current) {
      el.charDisplay.textContent = '—';
      el.slots.innerHTML = '';
      if (state.mode === 'text') el.textTicker.innerHTML = '';
      return;
    }
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
      } else if (state.mode === 'text' && i === state.typed.length && state.badChar) {
        /* 文章模式：错字母标红占位，下一键取代；不揭示后续编码 */
        d.textContent = state.badChar;
        d.classList.add('bad');
      } else if (i === state.typed.length && !state.locked) {
        d.classList.add('next');
      }
      el.slots.appendChild(d);
    }

    if (state.mode === 'text') renderTicker();
  };

  /* 面板抖动（答错反馈） */
  W.ui.shakePanel = function () {
    const el = W.ui.el;
    el.panel.classList.remove('shake');
    void el.panel.offsetWidth;
    el.panel.classList.add('shake');
  };
})(window.Wubi = window.Wubi || {});
