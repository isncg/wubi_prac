# -*- coding: utf-8 -*-
# 打印各 R4 候选字在 98 拆分表中的编码与末位性质，用于判定「编码一致→判定直传」。
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
chai = {}
for ln in open('tools/codetables/wubi98_chai_20902.txt', encoding='utf-16'):
    ln = ln.strip()
    if '\t' not in ln: continue
    ch, rest = ln.split('\t', 1)
    puas = re.findall(r'[\U000F0000-\U000FFFFD]', rest)
    m = re.search(r'※([a-z]{1,4})※', rest)
    if m: chai[ch] = (puas, m.group(1).upper())

ROWS = ['GFDSA', 'HJKLM', 'TREWQ', 'YUIOP', 'NBVCX']
KEY_AT = {}
for zi, row in enumerate(ROWS, 1):
    for pi, L in enumerate(row, 1): KEY_AT[(zi, pi)] = L

# 15 个已校准的识别码标记 → (区,位)
MARK = {0xF0005:(5,2),0xF000C:(1,3),0xF000F:(3,3),0xF0018:(1,2),0xF001D:(1,1),
        0xF0022:(2,1),0xF0026:(4,3),0xF002C:(2,2),0xF0035:(2,3),0xF0040:(5,1),
        0xF0063:(3,2),0xF0065:(3,1),0xF0067:(4,2),0xF006B:(5,3),0xF0076:(4,1)}
mset = {chr(k) for k in MARK}

chars = '到能得作道都面第使两重制身给常教提解毛路用样高然通'
for ch in chars:
    if ch not in chai:
        print(f'{ch}: 不在拆分表'); continue
    puas, code = chai[ch]
    lp = puas[-1] if puas else '?'
    if lp in mset:
        zi, pi = MARK[ord(lp)]
        tag = f'末位=识别码标记({zi}{pi})→98期望ID={KEY_AT[(zi,pi)]}'
    else:
        tag = '末位=字根'
    print(f'{ch}: chai={code} 拆分位数={len(puas)} {tag}')
