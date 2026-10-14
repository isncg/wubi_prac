#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析五笔码表文件，为练习用的字集生成 86 / 98 / 新世纪 三个版本的编码数据。

数据来源：
  tools/codetables/GB18030-27533.txt   98版全码表（yanhuacuo/98wubi-tables，GB18030 编码）
  tools/codetables/wubi06-CJK.txt      新世纪版全码表（CNMan/UnicodeCJK-WuBi06，UTF-8）
  tools/codetables/wubi86-CJK.txt      86版全码表（CNMan/UnicodeCJK-WuBi，UTF-8，含旧86/修正列）
  js/data/chars.js                     app 现有 86 版字库（决定字集与顺序）

输出：
  tools/output/chars_generated.js      新版 js/data/chars.js 内容（三版本字码表）
  tools/output/report.txt              差异 / 缺失 / 抽查报告

用法（MSYS2 / Git Bash）：
  /c/msys64/usr/bin/python tools/parse_codes.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_CHARS = ROOT / 'js' / 'data' / 'chars.js'
DIR_TABLES = ROOT / 'tools' / 'codetables'
DIR_OUT = ROOT / 'tools' / 'output'

# 一级简码（86/98/新世纪三版一致，app 数据统一按简码收录）
YIJI = {
    '一': 'G', '地': 'F', '在': 'D', '要': 'S', '工': 'A',
    '上': 'H', '是': 'J', '中': 'K', '国': 'L', '同': 'M',
    '和': 'T', '的': 'R', '有': 'E', '人': 'W', '我': 'Q',
    '主': 'Y', '产': 'U', '不': 'I', '为': 'O', '这': 'P',
    '民': 'N', '了': 'B', '发': 'V', '以': 'C', '经': 'X',
}

report_lines = []
def report(s=''):
    print(s)
    report_lines.append(s)


def load_app_chars():
    """从 js/data/chars.js 提取 (字, 86码) 有序列表。"""
    text = SRC_CHARS.read_text(encoding='utf-8')
    pairs = re.findall(r"\{c:'(.)',code:'([A-Z]+)'\}", text)
    if not pairs:
        sys.exit('ERROR: 未能从 js/data/chars.js 解析出字码条目')
    # 去重并保持顺序
    seen, result = set(), []
    for ch, code in pairs:
        if ch not in seen:
            seen.add(ch)
            result.append((ch, code))
    return result


def load_98():
    """98版：'字.' + 空白 + 小写全码，文件为 GB18030 编码。"""
    raw = (DIR_TABLES / 'GB18030-27533.txt').read_bytes()
    used_enc = None
    text = None
    for enc in ('utf-16', 'utf-8', 'gb18030'):
        try:
            text = raw.decode(enc)
            used_enc = enc
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode('utf-16-le', errors='replace')
        used_enc = 'utf-16-le(replace)'
    table = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        word = parts[0].rstrip('.').rstrip('．')
        code = parts[1]
        if len(word) == 1 and re.fullmatch(r'[a-z]{1,4}', code):
            table.setdefault(word, code.upper())
    report(f'[98] 编码判定: {used_enc}，共解析 {len(table)} 字')
    return table


def load_06():
    """新世纪版：U+XXXX <空白> 字 <空白> 小写全码（UTF-8，可能多码取第一码）。"""
    text = (DIR_TABLES / 'wubi06-CJK.txt').read_text(encoding='utf-8')
    table, nocode = {}, 0
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].startswith('U+'):
            ch, code = parts[1], parts[2]
            if len(ch) == 1 and re.fullmatch(r'[a-z]{1,4}', code):
                table.setdefault(ch, code.upper())
        elif len(parts) == 2 and parts[0].startswith('U+'):
            nocode += 1
    report(f'[06] 共解析 {len(table)} 字（无编码行 {nocode}，多为非 G 源字形）')
    return table


def load_86():
    """86版仓库：U+码位,字,旧86,98版,新世纪版,笔顺,笔顺 —— 列2=旧86，列3=98，列4=新世纪。"""
    text = (DIR_TABLES / 'wubi86-CJK.txt').read_text(encoding='utf-8')
    table_old, table_98, table_06 = {}, {}, {}
    for line in text.splitlines():
        parts = line.split(',')
        if len(parts) >= 5 and parts[0].startswith('U+'):
            ch = parts[1]
            if len(ch) == 1:
                for idx, tbl in ((2, table_old), (3, table_98), (4, table_06)):
                    if re.fullmatch(r'[a-z]{1,4}', parts[idx]):
                        tbl.setdefault(ch, parts[idx].upper())
    report(f'[86库] 共解析 旧86 {len(table_old)} 字 / 98 {len(table_98)} 字 / 新世纪 {len(table_06)} 字')
    return table_old, table_98, table_06


def code_for(ch, table, use_yiji=True):
    """取码：一级简码字按简码收录，其余取全码；返回 (最终码, 表中全码)。"""
    full = table.get(ch)
    if use_yiji and ch in YIJI:
        return YIJI[ch], full
    return full, full


def main():
    app = load_app_chars()
    chars = [ch for ch, _ in app]
    report(f'app 字集: {len(app)} 字（含一级简码 {sum(1 for c, _ in app if len(_) == 1)} 个简码字）')

    t98 = load_98()
    t06 = load_06()
    t86_old, t86_98, t86_06 = load_86()

    # ---------- 交叉验证：两个独立来源的 98 / 新世纪 码表 ----------
    report()
    report('== 交叉验证 ==')
    diff98 = [(c, t98[c], t86_98[c]) for c in chars
              if c in t98 and c in t86_98 and t98[c] != t86_98[c]]
    report(f'98: yanhuacuo表 vs CNMan表 不一致 {len(diff98)} 字: ' +
           (' '.join(f'{c}({a}/{b})' for c, a, b in diff98) if diff98 else '完全一致'))
    diff06 = [(c, t06[c], t86_06[c]) for c in chars
              if c in t06 and c in t86_06 and t06[c] != t86_06[c]]
    report(f'新世纪: CNMan06库 vs CNMan86库 不一致 {len(diff06)} 字: ' +
           (' '.join(f'{c}({a}/{b})' for c, a, b in diff06) if diff06 else '完全一致'))

    # ---------- 报告：缺失 ----------
    report()
    report('== 缺失检查 ==')
    for name, t in (('98', t98), ('06', t06)):
        missing = [c for c in chars if c not in t and c not in YIJI]
        report(f'{name} 缺失: {"".join(missing) if missing else "无"}')

    # ---------- 报告：app 现有 86 数据 vs 码表 ----------
    report()
    report('== app 86 数据与 CNMan 旧86 / 新世纪列 比对（字 app码 | 旧86 | 新世纪列）==')
    diff_old = diff_new = 0
    for ch, code in app:
        if len(code) == 1:
            continue  # 一级简码，不比对全码
        o, n = t86_old.get(ch), t86_06.get(ch)
        marks = []
        if o and o != code:
            marks.append(f'旧86={o}')
            diff_old += 1
        if n and n != code:
            marks.append(f'新世纪列={n}')
            diff_new += 1
        if marks:
            report(f'  {ch} {code} | {o} | {n}   <- {", ".join(marks)}')
    report(f'  与旧86不同: {diff_old} 字；与新世纪列不同(即98≠86或06≠86字): {diff_new} 字')

    # ---------- 报告：一级简码全码抽查 ----------
    report()
    report('== 一级简码字的全码（98 / 06，校验三版简码体系一致性）==')
    for ch in YIJI:
        f98 = t98.get(ch, '?')
        f06 = t06.get(ch, '?')
        report(f'  {ch} 简码={YIJI[ch]}  98全码={f98}  06全码={f06}')

    # ---------- 报告：版本间差异概览 ----------
    report()
    report('== 版本差异概览（非简码字）==')
    for ch, code86 in app:
        if len(code86) == 1:
            continue
        c98, _ = code_for(ch, t98)
        c06, _ = code_for(ch, t06)
        flags = []
        if c98 and c98 != code86:
            flags.append('98≠86')
        if c06 and c06 != code86:
            flags.append('06≠86')
        if c98 and c06 and c98 != c06:
            flags.append('98≠06')
        if flags:
            report(f'  {ch}: 86={code86} 98={c98} 06={c06}  [{",".join(flags)}]')

    # ---------- 生成 chars.js ----------
    def fmt_entries(entries, per_line=4):
        lines = []
        for i in range(0, len(entries), per_line):
            chunk = entries[i:i + per_line]
            lines.append('    ' + ''.join("{c:'%s',code:'%s'}," % (c, k) for c, k in chunk))
        return '\n'.join(lines)

    def build_version(name, table, use_yiji=True):
        out, missing = [], []
        for ch, _ in app:
            final, full = code_for(ch, table, use_yiji)
            if final is None:
                missing.append(ch)
                final = '?' * 1  # 占位，生成后需人工检查
            out.append((ch, final))
        return out, missing

    v86 = [(ch, code) for ch, code in app]
    v98, m98 = build_version('98', t98)
    v06, m06 = build_version('06', t06)

    js = f'''/* ============================================================
 * 数据层：单字编码库（86 版 / 98 版 / 新世纪版）
 * 字集与顺序沿用原 86 版字库；一级简码字按简码收录（三版一致）。
 * 98 版编码取自 yanhuacuo/98wubi-tables「GB18030-27533.txt」全码表；
 * 新世纪版编码取自 CNMan/UnicodeCJK-WuBi06「CJK.txt」全码表。
 * 本文件由 tools/parse_codes.py 生成（{len(app)} 字 / 版本），请勿手工增删条目。
 * ============================================================ */
(function (W) {{
  'use strict';

  W.data = W.data || {{}};

  W.data.CHARS = {{
    '86': [
{fmt_entries(v86)}
    ],
    '98': [
{fmt_entries(v98)}
    ],
    '06': [
{fmt_entries(v06)}
    ],
  }};
}})(window.Wubi = window.Wubi || {{}});
'''
    DIR_OUT.mkdir(parents=True, exist_ok=True)
    (DIR_OUT / 'chars_generated.js').write_text(js, encoding='utf-8')
    report()
    report('98 生成占位(缺失): ' + (''.join(m98) if m98 else '无'))
    report('06 生成占位(缺失): ' + (''.join(m06) if m06 else '无'))
    report('已生成 tools/output/chars_generated.js')

    (DIR_OUT / 'report.txt').write_text('\n'.join(report_lines), encoding='utf-8')


if __name__ == '__main__':
    main()
