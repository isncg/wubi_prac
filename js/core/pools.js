/* ============================================================
 * 核心层：题池构建
 * ============================================================ */
(function (W) {
  'use strict';

  W.core = W.core || {};

  /* Fisher–Yates 洗牌（不改动原数组） */
  W.core.shuffle = function (arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };

  /* 字根题池：当前版本全部键位 × 全部字根 */
  W.core.buildRootPool = function () {
    const pool = [];
    W.data.keys().forEach(k => k.roots.forEach(r => pool.push({
      root: r, key: k.k, name: k.name, mn: k.mn
    })));
    return W.core.shuffle(pool);
  };

  /* 单字题池（当前版本） */
  W.core.buildCharPool = function () {
    return W.core.shuffle(W.data.chars());
  };
})(window.Wubi = window.Wubi || {});
