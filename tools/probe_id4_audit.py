# -*- coding: utf-8 -*-
# 调研第 4 步：输出全部「非确定性」判定条目供人工审计——
#   1) R4 兜底（98 拆分缺失或 98 末位为字根时，86/06 用笔顺列兜底，含 3 码与 4 码）
#   2) R3 几何传递中「码表分歧」条目（86/06 编码 ≠ 98 拆分编码，末码==期望识别码字母
#      存在「恰为该键字根」的理论巧合风险，需人工确认）
#   3) 98 版自身 chai 编码 vs app 编码不一致检查
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
    return re.findall(r"\{c:'(.)',code:'([A-Z]+)'(?:,id:1)?\}", m.group(1))

keys_src = open('js/data/keys.js', encoding='utf-8').read()
def root_chars(ver):
    m = re.search(r'KEYS_%s = \[(.*?)\n  \];' % ver, keys_src, re.S)
    s = set()
    for grp in re.findall(r"roots:\[(.*?)\]", m.group(1)):
        s.update(re.findall(r"'(.)'", grp))
    return s

# CSV：字 → 规范笔顺列末笔（col6）
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

# ---- 识别码标记校准（同 probe_id4_final.py：全表 3 码非成字字根字多数投票）----
from collections import Counter, defaultdict
votes = defaultdict(Counter)
for ch, (puas, code) in chai.items():
    if len(code) != 3 or len(puas) != 3: continue
    if ch in root_chars('98'): continue
    zi, pi = ZP[code[2]]
    if pi > 3: continue
    votes[puas[2]][(zi, pi)] += 1
marker_zp = {}
for p, cnt in votes.items():
    (zi, pi), n = cnt.most_common(1)[0]
    if n / sum(cnt.values()) >= 0.8 and n >= 5:
        marker_zp[p] = (zi, pi)
print(f'识别码标记 {len(marker_zp)} 种（校准正常）' if len(marker_zp) == 15
      else f'!! 标记数异常: {len(marker_zp)}')

# ---- 分类（与最终 parse_codes.py 相同逻辑）----
def classify(ver):
    rc = root_chars(ver)
    out = []
    for c, code in block(ver):
        n = len(code)
        if n == 1: continue
        if c in rc:
            out.append((c, code, '根', 'R1')); continue
        info = chai.get(c)
        if info:
            puas, ccode = info
            lp = puas[-1] if puas else None
            if lp in marker_zp:
                zi, pi = marker_zp[lp]
                E = KEY_AT[(zi, pi)]
                if ver == '98':
                    note = '' if ccode == code else 'app码≠chai码!'
                    out.append((c, code, 'ID', 'R2' + note)); continue
                kind = 'ID' if code[-1] == E else '根'
                note = '' if code == ccode else '码表分歧'
                out.append((c, code, kind, 'R3' + note)); continue
            if ver == '98':
                note = '' if ccode == code else 'app码≠chai码!'
                out.append((c, code, '根', 'R2' + note)); continue
            out.append((c, code, None, 'R4·98末=字根')); continue
        out.append((c, code, None, 'R4·无拆分'))
    # R4 兜底
    fin = []
    for c, code, kind, rule in out:
        if kind is not None:
            fin.append((c, code, kind, rule)); continue
        L = code[-1]; zi, pi = ZP[L]
        end = csv_end.get(c, '?')
        if pi <= 3 and end == str(zi):
            fin.append((c, code, 'ID?', f'{rule} 笔顺末={end}→{zi}区 位={pi}'))
        else:
            fin.append((c, code, '根?', f'{rule} 位={pi} 笔顺末={end}≠{zi}区'))
    return fin

for ver in ['98', '86', '06']:
    res = classify(ver)
    by_rule = Counter(r.split('·')[0].rstrip('ID根?') for _, _, _, r in res)
    print(f'\n===== [{ver}] 规则分布 {dict(Counter(r[:2] for _, _, _, r in res))} =====')
    if ver != '98':
        unc = [(c, code, k, r) for c, code, k, r in res if r.startswith('R4')]
        print(f'-- R4 兜底 {len(unc)} 条（全部需人工审计）:')
        for c, code, k, r in unc:
            print(f'  {c} {code} → {k}   {r}')
        div = [(c, code, k, ccode) for c, code, k, r in res
               if '分歧' in r for ccode in [chai[c][1]]]
        print(f'-- R3 码表分歧 {len(div)} 条（末码==期望ID字母的巧合风险）:')
        for c, code, k, ccode in div:
            print(f'  {c} {code} → {k}   chai编码={ccode}')
    else:
        bad = [(c, code, r) for c, code, k, r in res if '≠' in r]
        print(f'-- app码≠chai码: {bad if bad else "无"}')
