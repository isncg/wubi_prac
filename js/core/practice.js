/* ============================================================
 * 核心层：练习推进与判题（出题 / 按键处理 / 模式切换）
 * ============================================================ */
(function (W) {
  'use strict';

  W.core = W.core || {};

  const state          = W.core.state;
  const el             = W.ui.el;
  const buildRootPool  = W.core.buildRootPool;
  const buildCharPool  = W.core.buildCharPool;
  const renderStage    = W.ui.renderStage;
  const shakePanel     = W.ui.shakePanel;
  const setFeedback    = W.ui.setFeedback;
  const clearFeedback  = W.ui.clearFeedback;
  const hideTeach      = W.ui.hideTeach;
  const showRootTeach  = W.ui.showRootTeach;
  const showCharTeach  = W.ui.showCharTeach;
  const flashKey       = W.ui.flashKey;
  const updateStats    = W.ui.updateStats;

  /* 触屏设备：反馈文案改用「点按继续」提示（桌面文案保持不变） */
  const TAP = window.matchMedia && matchMedia('(pointer: coarse)').matches;

  /* 取消「答对自动下一题」的定时器 */
  W.core.cancelNextTimer = function () {
    if (state.timer) { clearTimeout(state.timer); state.timer = null; }
  };

  /* 继续：答错后由空格 / 回车 / 点按题目区触发 */
  W.core.continueLocked = function () {
    if (!state.locked) return;
    W.core.cancelNextTimer();
    W.core.nextQuestion();
  };

  /* ---------- 出题 ---------- */
  W.core.nextQuestion = function () {
    state.locked = false;
    state.waitingContinue = false;
    state.typed = '';
    hideTeach();
    clearFeedback();

    if (state.mode === 'root') {
      if (!state.rootPool.length) state.rootPool = buildRootPool();
      state.current = state.rootPool.pop();
    } else {
      if (!state.charPool.length) state.charPool = buildCharPool();
      state.current = state.charPool.pop();
    }
    renderStage();
  };

  /* ---------- 核心：处理字母按键 ---------- */
  W.core.handleLetter = function (letter) {
    if (state.locked || !state.current) return;
    if (letter === 'Z') return;

    /* ---------- 字根模式 ---------- */
    if (state.mode === 'root') {
      const ans = state.current.key;

      if (letter === ans) {
        state.stats.right++;
        state.stats.streak++;
        state.stats.best = Math.max(state.stats.best, state.stats.streak);
        updateStats();
        flashKey(letter, 'ok');
        setFeedback(true, `✓ ${state.current.root} → ${ans} 键　【${state.current.mn}】`);
        state.locked = true;
        state.timer = setTimeout(W.core.nextQuestion, 520);
      } else {
        state.stats.wrong++;
        state.stats.streak = 0;
        updateStats();
        flashKey(letter, 'bad');
        flashKey(ans, 'hint');
        setFeedback(false, TAP ? '✗ 按错了 · 点按此处继续' : '✗ 按错了，请查看右侧详解');
        state.locked = true;
        state.waitingContinue = true;
        shakePanel();
        showRootTeach(letter);
      }
      return;
    }

    /* ---------- 单字模式 ---------- */
    const code = state.current.code;
    const pos  = state.typed.length;
    state.typed += letter;

    if (code[pos] !== letter) {
      state.stats.wrong++;
      state.stats.streak = 0;
      updateStats();
      state.locked = true;
      state.waitingContinue = true;
      renderStage();
      flashKey(letter, 'bad');
      flashKey(code[pos], 'hint');
      setFeedback(false, TAP ? `✗ 第 ${pos + 1} 码敲错了 · 点按此处继续`
                             : `✗ 第 ${pos + 1} 码敲错了，正确答案已标出`);
      shakePanel();
      showCharTeach(state.typed);
      return;
    }

    renderStage();
    flashKey(letter, 'ok');

    if (state.typed === code) {
      state.stats.right++;
      state.stats.streak++;
      state.stats.best = Math.max(state.stats.best, state.stats.streak);
      updateStats();
      setFeedback(true, `✓ ${state.current.c} = ${code}`);
      state.locked = true;
      state.timer = setTimeout(W.core.nextQuestion, 520);
    }
  };

  /* ---------- 模式切换 ---------- */
  W.core.setMode = function (mode) {
    W.core.cancelNextTimer();

    state.mode = mode;
    state.current = null;
    state.typed = '';
    state.locked = false;
    state.waitingContinue = false;

    document.querySelectorAll('.tab[data-mode]').forEach(t => {
      t.classList.toggle('active', t.dataset.mode === mode);
    });

    el.stageRoot.classList.toggle('hidden', mode !== 'root');
    el.stageChar.classList.toggle('hidden', mode !== 'char');

    if (mode === 'root') state.rootPool = [];
    else state.charPool = [];

    W.core.nextQuestion();
  };

  /* ---------- 版本切换（86 / 98 / 新世纪） ----------
     键位字根表与单字编码库随版本变化：
     清空两池、重建键帽（键名/提示随版本更新）并立即出新题 */
  W.core.setVersion = function (ver) {
    if (!W.data.setVersion(ver)) return;

    W.core.cancelNextTimer();

    state.current = null;
    state.typed = '';
    state.locked = false;
    state.waitingContinue = false;
    state.rootPool = [];
    state.charPool = [];

    document.querySelectorAll('.tab[data-ver]').forEach(t => {
      t.classList.toggle('active', t.dataset.ver === W.data.ver);
    });

    W.ui.buildKeyboard(W.core.handleLetter);
    W.core.nextQuestion();
  };
})(window.Wubi = window.Wubi || {});
