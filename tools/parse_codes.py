#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析五笔码表文件，为练习用的字集生成 86 / 98 / 新世纪 三个版本的编码数据。

数据来源：
  tools/codetables/GB18030-27533.txt   98版全码表（yanhuacuo/98wubi-tables，GB18030 编码）
  tools/codetables/wubi06-CJK.txt      新世纪版全码表（CNMan/UnicodeCJK-WuBi06，UTF-8）
  tools/codetables/wubi86-CJK.txt      86版全码表（CNMan/UnicodeCJK-WuBi，UTF-8，含旧86/修正列）
  tools/codetables/wubi98_chai_20902.txt  98 拆分表（yanhuacuo/98wubi-unicode，PUA 字根序列，
                                      用于判定每个字末码是「字根」还是「识别码」，id:1 标志）
  js/data/chars.js                     app 现有字库（决定字集与顺序；读取时兼容 id:1）
  js/data/keys.js                      各键字根表（成字字根判定用）

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
CHAI_FILE = DIR_TABLES / 'wubi98_chai_20902.txt'   # 98 拆分表（PUA 字根序列）

# 键盘区位：字母 → (区号, 位号)；KEY_AT 为反查表。
_ROWS = ['GFDSA', 'HJKLM', 'TREWQ', 'YUIOP', 'NBVCX']
ZP = {}
for _z, _row in enumerate(_ROWS, 1):
    for _p, _L in enumerate(_row, 1):
        ZP[_L] = (_z, _p)
KEY_AT = {v: k for k, v in ZP.items()}

# 末码性质人工裁定（自动化规则覆盖不到的条目）：(字, 编码) → 'ID' | '根'。
# 裁定依据：笔画覆盖验证（字根须覆盖全部笔画、识别码不占笔画）+ 版本拆分差异
# 考证（力/刀/戈末笔区号 86 与 98/06 规定不同；样/用在新世纪重新拆分）。
CORRECTIONS = {
    ('年', 'RHFK'): 'ID',  # 𠂉丨二+识别码 K(23 竖×杂合)
    ('动', 'FCLN'): 'ID',  # 二厶力+识别码 N(51)；86 规定力末笔作折
    ('分', 'WVB'): 'ID',   # 八刀+识别码 B(52)；86 规定刀末笔作折
    ('战', 'HKAT'): 'ID',  # 卜口戈+识别码 T(31)；86 戈末笔取撇（98/06 取点）
    ('毛', 'TFNV'): 'ID',  # 丿二乚+识别码 V(53 折×杂合)
    ('样', 'SUGH'): 'ID',  # 新世纪 木丷龶+识别码 H(21)；龶=青头∈06-G
    ('用', 'EHK'): 'ID',   # 新世纪 月丨+识别码 K(23 竖×杂合)；用非 06 字根
    ('面', 'DMJD'): '根',  # 丆冂刂三 4 字根；识别码读法笔画覆盖不上
    ('制', 'RMHJ'): '根',  # 𠂉冂丨刂 4 字根，末位 J=刂
    ('使', 'WGKQ'): '根',  # 亻一口乂 4 字根，末位 Q=乂
    ('解', 'QEVH'): '根',  # ⺈用刀+牛底字根；识别码读法余 4 笔无字根可覆盖
    ('解', 'QEHG'): '根',  # 同上（新世纪）
    ('样', 'SUDH'): '根',  # 木丷三丨 4 字根（书写顺序拆法，无识别码）
}

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
    pairs = re.findall(r"\{c:'(.)',code:'([A-Z]+)'(?:,id:1)?\}", text)
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


def load_chai():
    """98 拆分表：'字\t[PUA字根序列…,※编码※,…]'，字根以 PUA 码位表示，
    拆分位数与编码字母一一对应。"""
    chai = {}
    for ln in CHAI_FILE.read_text(encoding='utf-16').splitlines():
        ln = ln.strip()
        if '\t' not in ln:
            continue
        ch, rest = ln.split('\t', 1)
        puas = re.findall(r'[\U000F0000-\U000FFFFD]', rest)
        m = re.search(r'※([a-z]{1,4})※', rest)
        if m:
            chai[ch] = (puas, m.group(1).upper())
    report(f'[98拆分] 共解析 {len(chai)} 字')
    return chai


def load_root_chars():
    """从 js/data/keys.js 提取各版本全部字根（成字字根判定用）。"""
    text = (ROOT / 'js' / 'data' / 'keys.js').read_text(encoding='utf-8')
    out = {}
    for ver in ('86', '98', '06'):
        m = re.search(r'KEYS_%s = \[(.*?)\n  \];' % ver, text, re.S)
        s = set()
        for grp in re.findall(r'roots:\[(.*?)\]', m.group(1)):
            s.update(re.findall(r"'(.)'", grp))
        out[ver] = s
    return out


def calibrate_markers(chai, rc98):
    """自校准「识别码 PUA 标记」：用全表 3 码非成字字根字（末码必为识别码）
    的末位 PUA 投票，仅当某 (区,位) 得票 ≥80% 且 ≥5 票时认定该 PUA 为其标记。
    预期恰好 15 种（5 区 × 3 字型）。"""
    votes = {}
    for ch, (puas, code) in chai.items():
        if len(code) != 3 or len(puas) != 3 or ch in rc98:
            continue
        zp = ZP.get(code[2])
        if zp is None or zp[1] > 3:
            continue
        votes.setdefault(puas[2], {}).setdefault(zp, 0)
        votes[puas[2]][zp] += 1
    markers = {}
    for p, cnt in votes.items():
        zp, n = max(cnt.items(), key=lambda kv: kv[1])
        if n / sum(cnt.values()) >= 0.8 and n >= 5:
            markers[p] = zp
    return markers


def last_code_kind(ver, ch, code, roots, chai, markers, csv_end):
    """判定某条目末码是「识别码」还是「字根」，返回 'ID' / '根' / None。

    规则链：人工裁定 → 成字字根（报户口+笔画） → 98 拆分表末位性质
    （本版精确；他版编码一致时直传；编码分歧时按标记 (区,位) 反查期望识别码
    字母做几何判定，末码 ≠ 期望字母者必为字根） → 位 4/5 必为字根。"""
    if len(code) <= 1 or '?' in code:
        return None
    key = (ch, code)
    if key in CORRECTIONS:                        # 人工裁定优先
        return CORRECTIONS[key]
    if ch in roots:                               # 成字字根：各码取笔画
        return '根'
    info = chai.get(ch)
    if info:
        puas, ccode = info
        lp = puas[-1] if puas else None
        if lp in markers:                         # 98 拆分末位 = 识别码标记
            if ver == '98' or ccode == code:
                return 'ID'                       # 本版精确 / 编码一致直传
            return 'ID' if code[-1] == KEY_AT[markers[lp]] else '根'
        if ver == '98' or ccode == code:
            return '根'                           # 拆分末位为字根 / 编码一致直传
    if ZP[code[-1]][1] > 3:                       # 位 4/5 不可能是识别码
        return '根'
    end = csv_end.get(ch)                         # 兜底：正常应已被上文覆盖
    return 'ID?' if end == str(ZP[code[-1]][0]) else '根?'


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

    # ---------- 末码性质判定（识别码 vs 字根）准备 ----------
    chai = load_chai()
    roots = load_root_chars()
    markers = calibrate_markers(chai, roots['98'])
    report(f'[98拆分] 识别码标记校准: {len(markers)} 种（预期 15 = 5 区 × 3 字型）')
    csv_end = {}
    for line in (DIR_TABLES / 'wubi86-CJK.txt').read_text(encoding='utf-8').splitlines():
        p = line.split(',')
        if len(p) >= 6 and len(p[1]) == 1 and p[5]:
            csv_end[p[1]] = p[5][-1]

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
            cells = ["{c:'%s',code:'%s',id:1}," % (c, k) if kind == 'ID'
                     else "{c:'%s',code:'%s'}," % (c, k)
                     for c, k, kind in chunk]
            lines.append('    ' + ''.join(cells))
        return '\n'.join(lines)

    def build_version(ver, table, use_yiji=True):
        out, missing = [], []
        for ch, _ in app:
            final, full = code_for(ch, table, use_yiji)
            if final is None:
                missing.append(ch)
                final = '?' * 1  # 占位，生成后需人工检查
            kind = last_code_kind(ver, ch, final, roots[ver], chai, markers, csv_end)
            if kind in ('ID?', '根?'):
                report(f'  !! 兜底触发 {ver} {ch}{final} → {kind}（应人工复核）')
            out.append((ch, final, kind))
        return out, missing

    v86, m86 = build_version('86', dict(app))   # 86 以 app 现有码为码表
    v98, m98 = build_version('98', t98)
    v06, m06 = build_version('06', t06)

    js = f'''/* ============================================================
 * 数据层：单字编码库（86 版 / 98 版 / 新世纪版）
 * 字集与顺序沿用原 86 版字库；一级简码字按简码收录（三版一致）。
 * 条目中 id:1 表示末码为「识别码」（非字根），由 98 拆分表 + 区位几何
 * + 人工裁定共同判定，教学卡片据此区分末码性质。
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
    # ---------- 末码性质统计 ----------
    report()
    report('== 末码性质统计（id:1 = 末码为识别码）==')
    for name, vers in (('86', v86), ('98', v98), ('06', v06)):
        n_id = sum(1 for _, _, k in vers if k == 'ID')
        n_root = sum(1 for _, _, k in vers if k == '根')
        report(f'  {name}: 识别码 {n_id} / 字根 {n_root} / 简码等 {len(vers) - n_id - n_root}')
        report('    识别码字: ' + ' '.join(f'{c}{k}' for c, k, kind in vers if kind == 'ID'))
    corr_used = {(c, k) for c, k, kind in v86 + v98 + v06 if (c, k) in CORRECTIONS}
    report(f'  人工裁定生效: {len(corr_used)}/{len(CORRECTIONS)} 条')

    DIR_OUT.mkdir(parents=True, exist_ok=True)
    (DIR_OUT / 'chars_generated.js').write_text(js, encoding='utf-8')
    report()
    report('86 生成占位(缺失): ' + (''.join(m86) if m86 else '无'))
    report('98 生成占位(缺失): ' + (''.join(m98) if m98 else '无'))
    report('06 生成占位(缺失): ' + (''.join(m06) if m06 else '无'))
    report('已生成 tools/output/chars_generated.js')

    (DIR_OUT / 'report.txt').write_text('\n'.join(report_lines), encoding='utf-8')


if __name__ == '__main__':
    main()
