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
  const buildTextPool  = W.core.buildTextPool;
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

  /* 继续：答错后由空格 / 回车 / 点按题目区触发下一题。
     文章模式答错不锁定，无需按键继续（下一键直接取代错字母） */
  W.core.continueLocked = function () {
    if (!state.locked) return;
    W.core.cancelNextTimer();
    W.core.nextQuestion();
  };

  /* 文章模式：把 current 定位到 textPos 处的字（跳过标点等无编码字符） */
  function pointCurrentChar() {
    while (state.textPos < state.text.length) {
      const entry = W.data.entryFor(state.text[state.textPos]);
      if (entry) {
        state.current = entry;
        return;
      }
      state.textPos++;
    }
    state.current = null;
  }

  /* 文章模式：装载第 i 篇（并同步下拉列表） */
  function setText(i) {
    state.textIndex = i;
    state.text = W.data.texts()[i].text;
    state.textPos = 0;
    if (el.textSelect) el.textSelect.value = String(i);
  }

  /* ---------- 出题 ---------- */
  W.core.nextQuestion = function () {
    state.locked = false;
    state.waitingContinue = false;
    state.typed = '';
    state.badChar = '';
    hideTeach();
    clearFeedback();

    if (state.mode === 'root') {
      if (!state.rootPool.length) state.rootPool = buildRootPool();
      state.current = state.rootPool.pop();
    } else if (state.mode === 'text') {
      if (!state.text || state.textPos >= state.text.length) {
        /* 进入模式 / 上一篇文章结束：随机抽下一篇（题池逐篇弹出，弹完重洗） */
        if (!state.textPool.length) state.textPool = buildTextPool();
        setText(state.textPool.pop());
      }
      pointCurrentChar();
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

    /* ---------- 文章模式：逐字推进，答错不揭示后续编码，下一键取代错字母 ---------- */
    if (state.mode === 'text') {
      const cur  = state.current;
      const code = cur.code;
      const pos  = state.typed.length;

      if (code[pos] !== letter) {
        /* 错字母留在槽位标红等待取代：不锁定、不提示正确键 / 后续编码 */
        state.stats.wrong++;
        state.stats.streak = 0;
        updateStats();
        state.badChar = letter;
        renderStage();
        flashKey(letter, 'bad');
        setFeedback(false, `✗ 「${cur.c}」第 ${pos + 1} 码敲错了 · 继续输入即可更正`);
        shakePanel();
        return;
      }

      if (state.badChar || pos === 0) clearFeedback();   /* 取代错字 / 新字起手 */
      state.badChar = '';
      state.typed += letter;
      renderStage();
      flashKey(letter, 'ok');

      if (state.typed === code) {
        state.stats.right++;
        state.stats.streak++;
        state.stats.best = Math.max(state.stats.best, state.stats.streak);
        updateStats();
        state.textPos++;
        state.typed = '';
        pointCurrentChar();   /* 立即切到下一字，保持逐字输入节奏 */

        if (!state.current) {   /* 输入完毕（含篇末标点等字库外字符） */
          setFeedback(true, '✓ 文章完成 · 马上开始下一篇');
          state.locked = true;
          state.timer = setTimeout(W.core.nextQuestion, 900);
        } else {
          setFeedback(true, `✓ ${cur.c} = ${code}`);
          renderStage();
        }
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

  /* ---------- 文章选择：下拉列表手动选篇 ---------- */
  W.core.loadTextIndex = function (i) {
    const texts = W.data.texts();
    if (state.mode !== 'text' || i < 0 || i >= texts.length) return;
    W.core.cancelNextTimer();
    state.locked = false;
    state.waitingContinue = false;
    state.typed = '';
    state.badChar = '';
    setText(i);
    pointCurrentChar();
    setFeedback(true, `✓ 已选「${texts[i].name}」· 从头开始`);
    renderStage();
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
    el.stageChar.classList.toggle('hidden', mode === 'root');
    el.textTicker.classList.toggle('hidden', mode !== 'text');
    el.textPicker.classList.toggle('hidden', mode !== 'text');
    el.charPrompt.textContent = mode === 'text'
      ? '文章练习 · 逐字敲出文中高亮字的编码'
      : '请敲出这个字的五笔编码';

    if (mode === 'root') state.rootPool = [];
    else if (mode === 'char') state.charPool = [];
    else { state.text = ''; state.textIndex = -1; state.textPos = 0; state.textPool = []; state.badChar = ''; }

    W.core.nextQuestion();
  };

  /* ---------- 版本切换（86 / 98 / 新世纪） ----------
     键位字根表与单字编码库随版本变化：
     清空各题池与文章进度、重建键帽（键名/提示随版本更新）并立即出新题 */
  W.core.setVersion = function (ver) {
    if (!W.data.setVersion(ver)) return;

    W.core.cancelNextTimer();

    state.current = null;
    state.typed = '';
    state.locked = false;
    state.waitingContinue = false;
    state.rootPool = [];
    state.charPool = [];
    state.text = '';
    state.textIndex = -1;
    state.textPos = 0;
    state.textPool = [];
    state.badChar = '';

    document.querySelectorAll('.tab[data-ver]').forEach(t => {
      t.classList.toggle('active', t.dataset.ver === W.data.ver);
    });

    W.ui.buildKeyboard(W.core.handleLetter);
    W.core.nextQuestion();
  };
})(window.Wubi = window.Wubi || {});
