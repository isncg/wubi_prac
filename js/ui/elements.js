/* ============================================================
 * UI 层：DOM 引用（集中管理）
 * ============================================================ */
(function (W) {
  'use strict';

  W.ui = W.ui || {};

  const byId = (id) => document.getElementById(id);

  W.ui.el = {
    stageRoot:  byId('stageRoot'),
    stageChar:  byId('stageChar'),
    rootDisplay:byId('rootDisplay'),
    charDisplay:byId('charDisplay'),
    charPrompt: byId('charPrompt'),
    textPicker: byId('textPicker'),
    textSelect: byId('textSelect'),
    textRestart: byId('textRestart'),
    slots:      byId('slots'),
    textTicker: byId('textTicker'),
    feedback:   byId('feedback'),
    teach:      byId('teach'),
    panel:      byId('panel'),
    panelMain:  byId('panelMain'),
    keyboard:   byId('keyboard'),
    statRight:  byId('statRight'),
    statWrong:  byId('statWrong'),
    statAcc:    byId('statAcc'),
    statStreak: byId('statStreak'),
    statBest:   byId('statBest'),
  };
})(window.Wubi = window.Wubi || {});
