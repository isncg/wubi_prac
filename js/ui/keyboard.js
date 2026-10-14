/* ============================================================
 * UI 层：键盘渲染与按键反馈
 * 真实 QWERTY 三行错位布局（含 Z）
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  const KEYBOARD_ROWS = [
    { cls:'r1', keys:['Q','W','E','R','T','Y','U','I','O','P'] },
    { cls:'r2', keys:['A','S','D','F','G','H','J','K','L'] },
    { cls:'r3', keys:['Z','X','C','V','B','N','M'] },
  ];

  /* 构建键盘 DOM；onLetter(letter) 为键帽点击回调 */
  W.ui.buildKeyboard = function (onLetter) {
    const el = W.ui.el;
    el.keyboard.innerHTML = '';

    KEYBOARD_ROWS.forEach(rowDef => {
      const row = document.createElement('div');
      row.className = 'kb-row ' + rowDef.cls;

      rowDef.keys.forEach(k => {
        const btn = document.createElement('button');
        btn.className = 'key';
        btn.dataset.k = k;

        const info = W.data.keyInfo(k);

        if (info) {
          btn.dataset.zone = W.data.ZONE_OF[k] || 0;
          btn.title = `${k} 键 · ${W.data.posLabel(k)} · 键名「${info.name}」`;
          btn.innerHTML = `<span class="k-letter">${k}</span>
                           <span class="k-code">${W.data.ZONE_OF[k]}${W.data.POS_OF[k]}</span>`;
          btn.addEventListener('click', () => onLetter(k));
        } else {
          btn.classList.add('key-unused');
          btn.dataset.zone = '0';
          btn.title = `${k} 键 · 五笔中未使用`;
          btn.setAttribute('aria-disabled', 'true');
          btn.innerHTML = `<span class="k-letter">${k}</span>
                           <span class="k-code">—</span>`;
        }

        row.appendChild(btn);
      });

      el.keyboard.appendChild(row);
    });
  };

  /* 键帽闪烁：ok / bad / hint */
  W.ui.flashKey = function (letter, type) {
    const el = W.ui.el;
    const node = el.keyboard.querySelector(`.key[data-k="${letter}"]`);
    if (!node) return;
    const cls = type === 'ok' ? 'flash-ok' : type === 'bad' ? 'flash-bad' : 'flash-hint';
    node.classList.add(cls);
    setTimeout(() => node.classList.remove(cls), type === 'hint' ? 1300 : 450);
  };
})(window.Wubi = window.Wubi || {});
