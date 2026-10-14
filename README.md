# 五笔字型练习（wubi_prac）

一个零构建、纯静态的五笔字根 / 单字打字练习页面。**双击 `index.html` 即可使用**，无需安装依赖、无需启动服务。

内置 **86 版（1986）/ 98 版（1998）/ 新世纪版（2008）** 三个版本的字根键位表与单字编码库，可随时一键切换，选择自动记忆。

## 功能特性

- **双练习模式**
  - 字根练习：给出一个字根，敲出它所在的键位；
  - 单字练习：给出一个汉字，依次敲出完整五笔编码（键位槽逐码回显）。
- **三版本切换**：顶部绿色按钮组切换 86版 / 98版 / 新世纪版，键位字根、助记口诀、单字编码随之整体切换，`localStorage` 记住上次选择。
- **可视化键盘**：真实 QWERTY 三行错位布局，五区配色（横/竖/撇/捺/折），键帽标注区位号；支持鼠标 / 触屏直接点按。
- **答错讲解卡**：答错时展开讲解——应敲键位、键名、助记口诀、该键字根（单字模式另附正确编码），内容随当前版本变化。
- **练习统计**：正确 / 错误 / 正确率 / 连击 / 最高连击，一键重置。
- **触屏与响应式**：窄屏下键盘等比撑满全宽（容器查询）、统计单行排布、反馈文案改为「点按继续」。

## 快速开始

```text
双击 index.html        # 直接以 file:// 打开即可
# 或者起个本地服务：
python -m http.server 8000    # 访问 http://localhost:8000
```

## 操作指南

| 操作 | 方式 |
| --- | --- |
| 切换练习模式 | 顶部「字根练习 / 单字练习」按钮 |
| 切换五笔版本 | 顶部「86版 / 98版 / 新世纪版」按钮（绿色高亮） |
| 答题 | 直接敲物理键盘字母，或点按屏幕键帽（Z 键五笔未使用） |
| 答对 | 键帽闪绿，稍候自动进入下一题 |
| 答错后继续 | 讲解卡展开，按 **空格 / 回车** 或点按题目区继续 |
| 清零统计 | 右上「重置统计」 |

## 目录结构

```text
wubi_prac/
├── index.html            入口页面（唯一页面，双击即用）
├── demo.html             最早的参考原型（仅留存）
├── css/                  样式模块（style.css 按 @import 聚合）
│   ├── variables.css     设计令牌：配色 / 阴影
│   ├── base.css          全局与 .wrap 页面骨架
│   ├── header.css        标题 / 模式切换 / 版本切换
│   ├── panel.css         题目面板与对错反馈
│   ├── teach.css         答错讲解卡
│   ├── keyboard.css      键盘布局与五区配色
│   ├── stats.css         统计块与操作提示
│   ├── animations.css    动画
│   └── responsive.css    响应式（窄屏 / 触屏）
├── js/
│   ├── main.js           入口：事件绑定与初始化
│   ├── data/
│   │   ├── keys.js       三版本键位字根表 + 版本注册（VERSIONS）
│   │   └── chars.js      三版本单字编码库（★ 生成文件，勿手改）
│   ├── core/
│   │   ├── state.js      全局练习状态与统计
│   │   ├── pools.js      题池构建（字根池 / 单字池）
│   │   └── practice.js   出题 / 判题 / 模式与版本切换
│   └── ui/
│       ├── elements.js   DOM 引用集中管理
│       ├── keyboard.js   键盘渲染与按键闪烁反馈
│       ├── stage.js      题目展示
│       ├── feedback.js   对错文案反馈
│       ├── teach.js      讲解卡内容
│       └── stats.js      统计渲染
└── tools/
    ├── parse_codes.py    码表解析与 chars.js 生成脚本
    ├── codetables/       原始码表（已 gitignore，不入库）
    └── output/           生成结果与报告（已 gitignore）
```

## 数据与码表

### 内置数据

- `js/data/keys.js`：每个版本一张 25 键表（不含 Z），每键含 `键名 / 助记词 mn / 字根 roots`。三版助记词均取自公开教程并与字根分布互校。
- `js/data/chars.js`：由脚本生成的 `W.data.CHARS = { '86': […], '98': […], '06': […] }`，当前每版本收录 **211 个常用字**（含 25 个一级简码字，简码字按简码收录——三个版本的一级简码完全一致）。字集与顺序沿用旧 86 版字库。

三个版本并不只是换个说法，编码实质不同，例如：

| 字 | 86 版 | 98 版 | 新世纪版 | 说明 |
| --- | --- | --- | --- | --- |
| 物 | TRQR | CQRT | TQRT | 「牛」86 在 R，98/新世纪移到 C |
| 特 | TRFF | CFFY | TFFY | 同上 |
| G 键助记 | 王旁青头戋（兼）五一 | 王旁青头五夫一 | 王旁青头五一提 | 字根与口诀均有增删 |

### 码表来源

单字编码解析自以下公开码表（下载后置于 `tools/codetables/`，文件名须一致）：

| 本地文件名 | 版本 | 来源仓库 | 格式备注 |
| --- | --- | --- | --- |
| `GB18030-27533.txt` | 98 版全码 | [yanhuacuo/98wubi-tables](https://github.com/yanhuacuo/98wubi-tables) | **UTF-16LE（带 BOM）**，格式「字. 全码」 |
| `wubi06-CJK.txt` | 新世纪版全码 | [CNMan/UnicodeCJK-WuBi06](https://github.com/CNMan/UnicodeCJK-WuBi06)（`CJK.txt`） | UTF-8，格式「U+码位 字 全码」 |
| `wubi86-CJK.txt` | 旧86 / 98 / 新世纪 三列 | [CNMan/UnicodeCJK-WuBi](https://github.com/CNMan/UnicodeCJK-WuBi)（`CJK.txt`） | UTF-8 CSV：`U+码位,字,旧86,98,新世纪,笔顺,…` |

### 重新生成 chars.js

`chars.js` 是生成文件，**请勿手工增删条目**；调整字集后按以下流程再生成：

```bash
# 1. 修改字集：直接编辑 js/data/chars.js 中 '86' 数组
#    （脚本以现有 86 条目决定字集与顺序）
# 2. 放好三份码表后运行（任意 Python 3 均可；MSYS2 / Git Bash 环境）：
/c/msys64/usr/bin/python tools/parse_codes.py
# 3. 核对 tools/output/report.txt，确认无缺失 / 不一致后覆盖：
cp tools/output/chars_generated.js js/data/chars.js
```

脚本会做**双源交叉验证**（98 版：yanhuacuo 表 vs CNMan 表的 98 列；新世纪版：WuBi06 库 vs WuBi 库的新世纪列），最近一次运行两版均 **0 处不一致**；86 版数据与 CNMan「旧86」列 185/186 一致（唯一例外「并」保留更通行的 UAG 拆分）。

## 实现要点（开发约定）

- **零构建**：无打包器、无 npm 依赖；JS 为经典 `defer` 脚本按依赖顺序加载，禁止引入 ES module。
- **命名空间**：所有模块挂载于单一 `window.Wubi` 命名空间，按 `Wubi.data`（数据）/ `Wubi.core`（状态与逻辑）/ `Wubi.ui`（渲染）分层，各文件为 `'use strict'` IIFE。
- **版本切换链路**：`.tab[data-ver]` 点击 → `main.js` → `W.core.setVersion(ver)` → 清空两池并重建键盘、立即出题；数据面由 `W.data.ver` 驱动 `keys() / chars()`，选择持久化于 `localStorage['wubi_ver']`。
- **键盘尺寸**：键宽由 CSS 变量 `--kw` 控制，窄屏 / 触屏下改用容器查询单位 `calc((100cqw - 9*var(--gap))/10)` 等比撑满；`.wrap` 需保持 `min-width:0` 防止 flex 居中溢出。

## 回归自检（可选）

`tools/output/` 下附带两个无构建自检页（配合 headless Edge `--dump-dom` 使用）：

- `diag.html`：输出关键元素计算样式，验证窄屏布局无横向溢出；
- `diag_app.html`：真实点击切换版本 / 模式并断言出题、判题、讲解卡与持久化逻辑（最近一次 25/25 通过）。

用法示例：

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless=new --disable-gpu --window-size=1280,900 \
  --virtual-time-budget=4000 --dump-dom \
  "http://localhost:8000/tools/output/diag_app.html" | grep APPDIAG
```
