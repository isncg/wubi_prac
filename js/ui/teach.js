/* ============================================================
 * UI 层：教学卡片（答错后的键位 / 编码详解）
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  W.ui.hideTeach = function () {
    const el = W.ui.el;
    el.teach.classList.remove('show');
    el.teach.innerHTML = '';
  };

  /* 字根模式：按错键后的详解 */
  W.ui.showRootTeach = function (typedLetter) {
    const state = W.core.state;
    const el = W.ui.el;
    const cur = state.current;
    const ans = cur.key;
    const info = W.data.keyInfo(ans);

    const rootsHtml = info.roots.map(r =>
      `<em class="${r === cur.root ? 'hi' : ''}">${r}</em>`
    ).join('');

    el.teach.innerHTML = `
      <div class="t-title">
        <span>✗ 按错了</span>
        <span class="t-char">${cur.root}</span>
        <span>应敲</span>
        <span class="kbd-badge">${ans}</span>
        <span>键</span>
      </div>
      <div class="t-grid">
        <div class="t-row">
          <span class="t-label">你按了</span>
          <span class="t-val"><span class="kbd-badge bad">${typedLetter}</span></span>
        </div>
        <div class="t-row">
          <span class="t-label">键位</span>
          <span class="t-val">${ans} 键 · ${W.data.posLabel(ans)}</span>
        </div>
        <div class="t-row">
          <span class="t-label">键名字</span>
          <span class="t-val">${info.name}</span>
        </div>
        <div class="t-row">
          <span class="t-label">助记口诀</span>
          <span class="t-val">${info.mn}</span>
        </div>
        <div class="t-row">
          <span class="t-label">该键字根</span>
          <span class="t-val roots-line">${rootsHtml}</span>
        </div>
      </div>
      <div class="cont-hint">按 <kbd>空格</kbd> / <kbd>回车</kbd>，或点按继续下一题</div>
    `;
    el.teach.classList.add('show');
  };

  /* 单字模式：编码错误后的逐码详解 */
  W.ui.showCharTeach = function (typedStr) {
    const state = W.core.state;
    const el = W.ui.el;
    const cur = state.current;
    const code = cur.code;

    const items = [...code].map((ch, i) => {
      const info = W.data.keyInfo(ch);
      if (!info) return '';
      const isWrong = typedStr[i] !== undefined && typedStr[i] !== ch;
      const z = W.data.ZONE_OF[ch], p = W.data.POS_OF[ch], n = W.data.ZONE_NAME_OF[ch];
      const posTxt = z ? `　[${z}${p} ${n}区]` : '';
      return `
        <div class="code-item ${isWrong ? 'wrong' : ''}">
          <span class="ci-idx">第${i + 1}码</span>
          <span class="ci-letter">${ch}</span>
          <span class="ci-body">
            <span class="ci-name">${info.name} 键${posTxt} · ${info.mn}</span>
            <div class="ci-roots">该键字根：${info.roots.join('　')}</div>
          </span>
        </div>`;
    }).join('');

    const simpleTip = code.length === 1
      ? `<div class="tip-note">💡 这是一级简码字，只需敲击一码即可上屏。</div>`
      : '';

    el.teach.innerHTML = `
      <div class="t-title">
        <span>✗ 编码错误</span>
        <span class="t-char">${cur.c}</span>
        <span>你敲了</span>
        <span class="kbd-badge bad">${typedStr || '—'}</span>
        <span>正确应为</span>
        <span class="kbd-badge">${code}</span>
      </div>
      ${simpleTip}
      <div class="code-list">${items}</div>
      <div class="cont-hint">按 <kbd>空格</kbd> / <kbd>回车</kbd>，或点按继续下一题</div>
    `;
    el.teach.classList.add('show');
  };
})(window.Wubi = window.Wubi || {});
