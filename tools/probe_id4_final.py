# -*- coding: utf-8 -*-
# 调研第 3 步：形成可直接落地的末码分类器，并输出需人工复核的清单。
#
# 判定规则（按优先级）：
#   R1 成字字根（字本身 ∈ 当前版本某键的字根）：末码 = 笔画（报户口+首笔+次笔+末笔）→ 字根
#   R2 98 版：98 拆分表末位 PUA ∈ 识别码标记集 → 识别码；否则字根（精确）
#   R3 几何传递：98 拆分末位 PUA 为识别码标记时，标记本身编码了（末笔区， 字型位），
#      而识别码的区位规则三版一致 → 期望识别码字母 E 对 86/06 同样成立：
#        末码 == E → 识别码；末码 != E → 字根
#   R4 兜底（R2/R3 几何信息缺失）：末码位号 ≤3 且 区号 == 笔顺列末笔（col6，规范笔顺）
#      → 疑似识别码（需人工复核，包围结构/笔顺分歧字可能误判）
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

ROWS = ['GFDSA', 'HJKLM', 'TREWQ', 'YUIOP', 'NBVCX']
ZP = {}
for zi, row in enumerate(ROWS, 1):
    for pi, L in enumerate(row, 1):
        ZP[L] = (zi, pi)
KEY_AT = {v: k for k, v in ZP.items()}
ZNAME = ['横', '竖', '撇', '捺', '折']
SHAPE = {1: '左右型', 2: '上下型', 3: '杂合型'}

src = open('js/data/chars.js', encoding='utf-8').read()
def block(ver):
    m = re.search(r"'%s': \[(.*?)\n    \]," % ver, src, re.S)
    return re.findall(r"\{c:'(.)',code:'([A-Z]+)'\}", m.group(1))

keys_src = open('js/data/keys.js', encoding='utf-8').read()
def root_chars(ver):
    m = re.search(r'KEYS_%s = \[(.*?)\n  \];' % ver, keys_src, re.S)
    s = set()
    for grp in re.findall(r"roots:\[(.*?)\]", m.group(1)):
        s.update(re.findall(r"'(.)'", grp))
    return s

# CSV：字 → (末笔col6, 期望col7)
csv_end = {}
for line in open('tools/codetables/wubi86-CJK.txt', encoding='utf-8'):
    p = line.rstrip('\n').split(',')
    if len(p) >= 6 and p[1] and len(p[5]) >= 1:
        csv_end[p[1]] = p[5][-1]

# 98 拆分表
chai = {}
for ln in open('tools/codetables/wubi98_chai_20902.txt', encoding='utf-16'):
    ln = ln.strip()
    if '\t' not in ln: continue
    ch, rest = ln.split('\t', 1)
    puas = re.findall(r'[\U000F0000-\U000FFFFD]', rest)
    m = re.search(r'※([a-z]{1,4})※', rest)
    if m: chai[ch] = (puas, m.group(1).upper())

# ---- 识别码标记 ↔ (区,位) 校准：全文件 3 码非成字字根字投票，
#      3 根字（如别GKLJ）的末码是字根，会分散投票；只有当某个(区,位)
#      得票占绝对多数（≥80%）时才认定该 PUA 为识别码标记 ----
from collections import Counter, defaultdict
votes = defaultdict(Counter)
for ch, (puas, code) in chai.items():
    if len(code) != 3 or len(puas) != 3: continue
    if ch in root_chars('98'): continue
    zi, pi = ZP[code[2]]
    if pi > 3: continue          # 位 4/5 不可能是识别码 → 拆分口径不同，跳过
    votes[puas[2]][(zi, pi)] += 1

marker_zp = {}
for p, cnt in votes.items():
    (zi, pi), n = cnt.most_common(1)[0]
    total = sum(cnt.values())
    if n / total >= 0.8 and n >= 5:
        marker_zp[p] = (zi, pi)
    elif total >= 5:
        print(f'?? 未认定 U+{ord(p):05X}: 票型 {dict(cnt)}')

print(f'识别码标记（全表校准）: {len(marker_zp)} 种')
for p, (zi, pi) in sorted(marker_zp.items()):
    print(f'  U+{ord(p):05X} → {zi}{pi}（{ZNAME[zi-1]}区{SHAPE[pi]}）')

# ---- 末码分类器 ----
def classify(ver):
    rc = root_chars(ver)
    out = {}   # char -> (kind, rule)
    for c, code in block(ver):
        n = len(code)
        if n == 1 or c not in chai: continue
        puas, cc = chai[c]
        # R1 成字字根
        if c in rc:
            out[c] = ('根', 'R1'); continue
        if n == 3 and len(puas) == 3:
            if ver == '98':
                out[c] = ('ID' if puas[2] in marker_zp else '根', 'R2'); continue
            if puas[2] in marker_zp:
                zi, pi = marker_zp[puas[2]]
                out[c] = ('ID' if code[2] == KEY_AT[(zi, pi)] else '根', 'R3'); continue
        if n == 4 and len(puas) == 4:
            if ver == '98':
                out[c] = ('ID' if puas[3] in marker_zp else '根', 'R2'); continue
            if puas[3] in marker_zp:
                zi, pi = marker_zp[puas[3]]
                out[c] = ('ID' if code[3] == KEY_AT[(zi, pi)] else '根', 'R3'); continue
        # R4 兜底（86/06 拆分长度不匹配或缺失）
        if n in (3, 4):
            L = code[-1]; zi, pi = ZP[L]
            end = csv_end.get(c)
            if pi <= 3 and end == str(zi):
                out[c] = ('ID?', 'R4')
            else:
                out[c] = ('根', 'R4')
    return out

for ver in ['86', '98', '06']:
    res = classify(ver)
    ids = [c + code for (c, code), (k, r) in zip(block(ver), [res.get(c, ('-', '-')) for c, _ in block(ver)]) if k in ('ID', 'ID?') and len(code) >= 3]
    idq = [c + code for (c, code), (k, r) in zip(block(ver), [res.get(c, ('-', '-')) for c, _ in block(ver)]) if k == 'ID?' and len(code) == 4]
    by_rule = {}
    for c, (k, r) in res.items(): by_rule[r] = by_rule.get(r, 0) + 1
    print(f'\n[{ver}] 规则分布 {by_rule}')
    print(f'  4码·疑似识别码(R4待复核): {" ".join(idq)}')

# ---- 输出 86/06 的全部 4 码判定（含规则），供人工审计 ----
for ver in ['86', '06']:
    res = classify(ver)
    print(f'\n[{ver}] 4码判定明细:')
    line = []
    for c, code in block(ver):
        if len(code) != 4: continue
        k, r = res.get(c, ('?', '?'))
        line.append(f'{c}{code}={k}({r})')
    for i in range(0, len(line), 8):
        print('   ' + ' '.join(line[i:i+8]))
