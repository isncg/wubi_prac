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

    /* 该字是否为成字字根（本身是当前版本某键的字根）：
       成字字根按「报户口 + 首笔 + 次笔(+末笔)」编码，各码取笔画而非字根。
       末码性质优先用数据标志 cur.id（1 = 识别码，由码表拆分精确判定，
       3 码 / 4 码均适用）；旧数据缺标志时退回启发式：非成字字根的 3 码字末码为识别码。 */
    let isRootChar = false;
    W.data.keys().forEach(k => {
      if (k.roots.indexOf(cur.c) !== -1) isRootChar = true;
    });
    const isIdCode = cur.id !== undefined
      ? cur.id === 1
      : (!isRootChar && code.length === 3);

    const items = [...code].map((ch, i) => {
      const info = W.data.keyInfo(ch);
      if (!info) return '';
      const isWrong = typedStr[i] !== undefined && typedStr[i] !== ch;
      const z = W.data.ZONE_OF[ch], p = W.data.POS_OF[ch], n = W.data.ZONE_NAME_OF[ch];
      const isLast = i === code.length - 1;

      /* 末码为识别码：区位号本身就是「末笔画 × 字型」（位 1/2/3 = 左右/上下/杂合） */
      if (isLast && isIdCode) {
        const shape = p === 1 ? '左右型' : p === 2 ? '上下型' : '杂合型';
        return `
        <div class="code-item ${isWrong ? 'wrong' : ''}">
          <span class="ci-idx">第${i + 1}码</span>
          <span class="ci-letter">${ch}</span>
          <span class="ci-body">
            <span class="ci-name">识别码 · 末笔「${n}」× 字型「${shape}」</span>
            <div class="ci-roots">不足四码时补识别码：末笔画定区、字型定位，落在 ${ch}（${z}${p}）键，并非取自该键字根</div>
          </span>
        </div>`;
      }
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

    const rootTip = isRootChar && code.length > 1
      ? `<div class="tip-note">💡 「${cur.c}」是成字字根：按「报户口 + 首笔 + 次笔${code.length === 4 ? ' + 末笔' : ''}」编码，各码取笔画而非字根。</div>`
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
      ${rootTip}
      <div class="code-list">${items}</div>
      <div class="cont-hint">按 <kbd>空格</kbd> / <kbd>回车</kbd>，或点按继续下一题</div>
    `;
    el.teach.classList.add('show');
  };
})(window.Wubi = window.Wubi || {});
