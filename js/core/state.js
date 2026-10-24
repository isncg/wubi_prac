/* ============================================================
 * 核心层：全局练习状态
 * ============================================================ */
(function (W) {
  'use strict';

  W.core = W.core || {};

  const state = {
    mode: 'root',            // 'root' 字根练习 | 'char' 单字练习 | 'text' 文章练习
    current: null,           // 当前题目
    typed: '',               // 单字 / 文章模式已敲入的编码
    locked: false,           // 本题已出结果，等待继续
    waitingContinue: false,  // 答错后等待按空格 / 回车
    timer: null,             // 答对后自动下一题的定时器
    stats: { right: 0, wrong: 0, streak: 0, best: 0 },
    rootPool: [],            // 字根题池（乱序，逐题弹出）
    charPool: [],            // 单字题池
    text: '',                // 文章模式：当前文章内容
    textIndex: -1,           // 文章模式：当前文章在文库中的下标
    textPos: 0,              // 文章模式：当前输入到的字下标
    textPool: [],            // 文章题池（乱序索引，逐篇弹出）
    badChar: '',             // 文章模式：待更正的错字母（下一键取代）
  };
  W.core.state = state;

  /* 清零统计 */
  W.core.resetStats = function () {
    state.stats = { right: 0, wrong: 0, streak: 0, best: 0 };
  };
})(window.Wubi = window.Wubi || {});
