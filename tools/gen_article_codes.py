#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为文章模式生成补充码表 js/data/codes.js。

覆盖文章库 js/data/texts.js（由 tools/gen_texts.py 从 texts/ 生成）
全部选篇正文中的每个汉字（三版本全码），使文章练习从篇首第一字
开始逐字敲码；练习字库（chars.js，211 字）内的字不收录——取码时
字库优先（简码 / 识别码标志齐全）。

码表来源与 tools/parse_codes.py 完全一致：
  tools/codetables/GB18030-27533.txt   98版全码表（yanhuacuo/98wubi-tables）
  tools/codetables/wubi06-CJK.txt      新世纪版全码表（CNMan/UnicodeCJK-WuBi06）
  tools/codetables/wubi86-CJK.txt      86版（CNMan/UnicodeCJK-WuBi，列2=旧86）

输出：
  js/data/codes.js                     W.data.ARTCODES = { '86': {字:码}, '98': …, '06': … }
  控制台                                字数 / 各版本缺失报告

用法（MSYS2 / Git Bash）：
  /c/msys64/usr/bin/python tools/gen_article_codes.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_TEXTS = ROOT / 'js' / 'data' / 'texts.js'
SRC_CHARS = ROOT / 'js' / 'data' / 'chars.js'
DIR_TABLES = ROOT / 'tools' / 'codetables'
OUT_JS = ROOT / 'js' / 'data' / 'codes.js'

# 一级简码（86/98/新世纪三版一致，与 parse_codes.py 保持同一收录口径）
YIJI = {
    '一': 'G', '地': 'F', '在': 'D', '要': 'S', '工': 'A',
    '上': 'H', '是': 'J', '中': 'K', '国': 'L', '同': 'M',
    '和': 'T', '的': 'R', '有': 'E', '人': 'W', '我': 'Q',
    '主': 'Y', '产': 'U', '不': 'I', '为': 'O', '这': 'P',
    '民': 'N', '了': 'B', '发': 'V', '以': 'C', '经': 'X',
}


def is_han(ch):
    """CJK 统一汉字（含扩展 A）；标点 / 字母等不参与。"""
    return '\u3400' <= ch <= '\u4dbf' or '\u4e00' <= ch <= '\u9fff'


def load_lib_chars():
    """练习字库（chars.js）字集——这些字取码走字库，不进补充表。"""
    text = SRC_CHARS.read_text(encoding='utf-8')
    pairs = re.findall(r"\{c:'(.)',code:'([A-Z]+)'(?:,id:1)?\}", text)
    if not pairs:
        sys.exit('ERROR: 未能从 js/data/chars.js 解析出字码条目')
    return {ch for ch, _ in pairs}


def load_article_chars():
    """从文章库 texts.js 提取全部正文汉字（保持首次出现顺序）。"""
    text = SRC_TEXTS.read_text(encoding='utf-8')
    bodies = re.findall(r"text:\s*'([^']*)'", text)
    if not bodies:
        sys.exit('ERROR: 未能从 js/data/texts.js 解析出文章正文')
    seen, chars = set(), []
    for body in bodies:
        for ch in body:
            if is_han(ch) and ch not in seen:
                seen.add(ch)
                chars.append(ch)
    return chars


def load_98():
    """98版：'字.' + 空白 + 小写全码，文件为 GB18030 编码（同 parse_codes.py）。"""
    raw = (DIR_TABLES / 'GB18030-27533.txt').read_bytes()
    text = None
    for enc in ('utf-16', 'utf-8', 'gb18030'):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode('utf-16-le', errors='replace')
    table = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        word = parts[0].rstrip('.').rstrip('．')
        code = parts[1]
        if len(word) == 1 and re.fullmatch(r'[a-z]{1,4}', code):
            table.setdefault(word, code.upper())
    print(f'[98] 解析 {len(table)} 字')
    return table


def load_06():
    """新世纪版：U+XXXX <空白> 字 <空白> 小写全码，多码取第一码（同 parse_codes.py）。"""
    text = (DIR_TABLES / 'wubi06-CJK.txt').read_text(encoding='utf-8')
    table = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].startswith('U+'):
            ch, code = parts[1], parts[2]
            if len(ch) == 1 and re.fullmatch(r'[a-z]{1,4}', code):
                table.setdefault(ch, code.upper())
    print(f'[06] 解析 {len(table)} 字')
    return table


def load_86():
    """86版仓库：U+码位,字,旧86,98版,新世纪版,笔顺,笔顺 —— 取列2（旧86）。"""
    text = (DIR_TABLES / 'wubi86-CJK.txt').read_text(encoding='utf-8')
    table = {}
    for line in text.splitlines():
        parts = line.split(',')
        if len(parts) >= 5 and parts[0].startswith('U+'):
            ch = parts[1]
            if len(ch) == 1 and re.fullmatch(r'[a-z]{1,4}', parts[2]):
                table.setdefault(ch, parts[2].upper())
    print(f'[86] 解析 {len(table)} 字（旧86 列）')
    return table


def main():
    lib = load_lib_chars()
    chars = load_article_chars()
    outside = [ch for ch in chars if ch not in lib and ch not in YIJI]
    print(f'文章正文共 {len(chars)} 个不重复汉字'
          f'（字库外 {len(outside)} 个，其余 {len(chars) - len(outside)} 个走练习字库）')

    t86 = load_86()
    t98 = load_98()
    t06 = load_06()

    tables = {'86': t86, '98': t98, '06': t06}
    out, missing = {}, {}
    for ver, tbl in tables.items():
        entries, miss = {}, []
        for ch in outside:
            code = YIJI.get(ch) or tbl.get(ch)
            if code:
                entries[ch] = code
            else:
                miss.append(ch)
        out[ver] = entries
        missing[ver] = miss
        print(f'[{ver}] 收录 {len(entries)} 字'
              + (f'，缺失 {len(miss)}: {"".join(miss)}' if miss else '，无缺失'))

    def fmt(ver):
        cells = [f"'{ch}':'{code}'," for ch, code in out[ver].items()]
        lines = []
        for i in range(0, len(cells), 8):
            lines.append('      ' + ''.join(cells[i:i + 8]))
        return '\n'.join(lines)

    js = f'''/* ============================================================
 * 数据层：文章模式补充码表（86 版 / 98 版 / 新世纪版）
 * 覆盖 js/data/texts.js 全部《古文观止》选篇正文中的 {len(outside)} 个
 * 练习字库（chars.js，211 字）之外汉字，使文章练习从篇首第一字开始。
 * 练习字库内的字不收录——取码时字库优先（简码 / 识别码标志齐全）。
 * 编码来源与 tools/parse_codes.py 相同的码表（98：GB18030-27533.txt；
 * 新世纪：UnicodeCJK-WuBi06 CJK.txt；86：UnicodeCJK-WuBi 旧86 列）。
 * 本文件由 tools/gen_article_codes.py 生成，请勿手工增删条目。
 * ============================================================ */
(function (W) {{
  'use strict';

  W.data = W.data || {{}};

  W.data.ARTCODES = {{
    '86': {{
{fmt('86')}
    }},
    '98': {{
{fmt('98')}
    }},
    '06': {{
{fmt('06')}
    }},
  }};
}})(window.Wubi = window.Wubi || {{}});
'''
    OUT_JS.write_text(js, encoding='utf-8')
    print(f'已生成 {OUT_JS}（{OUT_JS.stat().st_size} 字节）')


if __name__ == '__main__':
    main()
