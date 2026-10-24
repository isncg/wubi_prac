#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 texts/ 目录生成文章库 js/data/texts.js。

目录约定（一篇一个文件，便于扩展）：
  texts/ 下每篇文章一个 .txt 文件（UTF-8，容忍 BOM；仅扫描 *.txt）：
    - 首个非空行 = 下拉列表显示名（如「曹刿论战 · 《左传》」）；
    - 其余内容 = 正文，生成时自动去除全部换行与空白（走马灯为单行展示）；
    - 文件名建议「两位数字前缀_短篇名」（如 01_曹刿论战.txt），下拉顺序
      即文件名排序，文件名本身不参与显示。

工作流（新增 / 修改 / 删除文章后）：
  1. 编辑 texts/ 下的 .txt 文件；
  2. /c/msys64/usr/bin/python tools/gen_texts.py         # 重新生成 texts.js
  3. 若提示有未覆盖取码的汉字，再运行：
     /c/msys64/usr/bin/python tools/gen_article_codes.py # 同步补充码表 codes.js
  4. 刷新页面即可（index.html 无需改动）。

输出：
  js/data/texts.js   W.data.texts() -> [{ name, text }, ...]
  控制台              每篇字数 / 总计 / 码表覆盖检查
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR_TEXTS = ROOT / 'texts'
OUT_JS = ROOT / 'js' / 'data' / 'texts.js'
SRC_CHARS = ROOT / 'js' / 'data' / 'chars.js'
SRC_CODES = ROOT / 'js' / 'data' / 'codes.js'


def is_han(ch):
    """CJK 统一汉字（含扩展 A）；标点 / 字母等不参与覆盖检查。"""
    return '\u3400' <= ch <= '\u4dbf' or '\u4e00' <= ch <= '\u9fff'


def js_str(s):
    """转义反斜杠与单引号，保证生成的字符串字面量恒合法。"""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def load_articles():
    """扫描 texts/*.txt：首行 = 显示名，其余 = 正文（去除全部空白）。"""
    files = sorted(p for p in DIR_TEXTS.glob('*.txt') if p.is_file())
    if not files:
        sys.exit(f'ERROR: {DIR_TEXTS} 下没有 .txt 文章文件')
    articles = []
    for p in files:
        lines = [ln.strip() for ln in p.read_text(encoding='utf-8-sig').splitlines()]
        lines = [ln for ln in lines if ln]
        if len(lines) < 2:
            sys.exit(f'ERROR: {p.name} 至少需要两行：首行显示名 + 正文')
        articles.append({'name': lines[0], 'text': ''.join(''.join(lines[1:]).split())})
    return articles


def load_covered():
    """已可取码字符集 = 练习字库 chars.js ∪ 补充码表 codes.js。"""
    covered = {ch for ch, _ in re.findall(
        r"\{c:'(.)',code:'([A-Z]+)'(?:,id:1)?\}",
        SRC_CHARS.read_text(encoding='utf-8'))}
    if SRC_CODES.exists():
        covered |= set(re.findall(r"'(.)':'[A-Z]+'", SRC_CODES.read_text(encoding='utf-8')))
    return covered


def main():
    articles = load_articles()
    covered = load_covered()
    total_han, seen, uncovered = 0, set(), []
    for i, a in enumerate(articles, 1):
        print(f'[{i:02d}] {a["name"]} · {len(a["text"])} 字')
        for ch in a['text']:
            if is_han(ch):
                total_han += 1
                if ch not in seen:
                    seen.add(ch)
                    if ch not in covered:
                        uncovered.append(ch)

    cells = []
    for a in articles:
        cells.append("    {\n      name: '%s',\n      text: '%s',\n    },"
                     % (js_str(a['name']), js_str(a['text'])))

    js = f'''/* ============================================================
 * 数据层：文章练习素材（{len(articles)} 篇《古文观止》选篇）
 * ★ 本文件由 tools/gen_texts.py 从 texts/ 目录生成，请勿直接编辑。
 * 新增 / 修改 / 删除文章请编辑 texts/ 下的 .txt 后重新生成：
 * 一篇一个文件，首个非空行 = 下拉显示名，其余 = 正文（自动去除
 * 换行与空白，走马灯为单行展示）；文件名建议两位数字前缀_短篇名，
 * 下拉顺序即文件名排序，文件名本身不参与显示。
 * 篇内全部汉字均可逐字敲码（字库外的字由 js/data/codes.js 补充
 * 码表提供三版全码），标点等无编码字符自动跳过。
 * ============================================================ */
(function (W) {{
  'use strict';

  W.data = W.data || {{}};

  const TEXTS = [
{chr(10).join(cells)}
  ];

  W.data.texts = function () {{ return TEXTS; }};
}})(window.Wubi = window.Wubi || {{}});
'''
    OUT_JS.write_text(js, encoding='utf-8')

    print(f'共 {len(articles)} 篇，正文合计 {total_han} 字，'
          f'不重复汉字 {len(seen)} 个')
    if uncovered:
        print(f'⚠ 有 {len(uncovered)} 个正文汉字尚无取码'
              f'（不在 chars.js / codes.js 中）：{"".join(uncovered)}')
        print('  请运行 tools/gen_article_codes.py 重新生成 js/data/codes.js；')
        print('  若该工具仍报缺失，则原始码表未收录这些字。')
    else:
        print('取码覆盖完整（练习字库 + 补充码表）。')
    print(f'已生成 {OUT_JS}（{OUT_JS.stat().st_size} 字节）')


if __name__ == '__main__':
    main()
