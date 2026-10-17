# -*- coding: utf-8 -*-
# 调研第 2 步：用 98 拆分表（PUA 字根序列）判断末码性质。
# 原理：拆分条目与编码字母一一对应。3 码非成字字根字的末码必为识别码，
#   其末位 PUA 值的集合 M 即「识别码标记」；末位 PUA ∈ M → 识别码，否则字根。
# 再用 98 拆分得到的末笔/字型信息推断 86/06 的期望识别码字母做交叉验证。
import re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

ROWS = ['GFDSA', 'HJKLM', 'TREWQ', 'YUIOP', 'NBVCX']
ZP = {}
for zi, row in enumerate(ROWS, 1):
    for pi, L in enumerate(row, 1):
        ZP[L] = (zi, pi)
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

# ---- 98 拆分表 ----
chai = {}
for ln in open('tools/codetables/wubi98_chai_20902.txt', encoding='utf-16'):
    ln = ln.strip()
    if not ln or '\t' not in ln: continue
    ch, rest = ln.split('\t', 1)
    puas = re.findall(r'[\U000F0000-\U000FFFFD]', rest)
    m = re.search(r'※([a-z]{1,4})※', rest)
    if not m: continue
    chai[ch] = (puas, m.group(1).upper())

# ---- 自校准：3 码非成字字根 → 末码识别码 → 收集识别码 PUA 标记 ----
rc98 = root_chars('98')
markers = {}
for c, code in block('98'):
    if len(code) != 3 or c in rc98 or c not in chai: continue
    puas, cc = chai[c]
    if len(puas) != len(code): continue
    markers.setdefault(puas[-1], []).append(c + code)
print('识别码 PUA 标记（%d 种）:' % len(markers))
for p, ex in sorted(markers.items()):
    print('  U+%05X  例: %s' % (ord(p), ' '.join(ex[:6])))

# ---- 用标记分类 98 版全部 4 码字 ----
def classify(ver, rootc):
    res = []
    for c, code in block(ver):
        if len(code) != 4 or c not in chai: continue
        puas, cc = chai[c]
        ok_map = (len(puas) == len(code) and cc == code)
        if not ok_map: continue
        kind = 'ID' if puas[-1] in markers else '根'
        res.append((c, code, kind))
    return res

for ver in ['98', '86', '06']:
    res = classify(ver, root_chars(ver))
    ids = [c + code for c, code, k in res if k == 'ID']
    roots = [c + code for c, code, k in res if k == '根']
    print(f'\n[{ver}] 4码字拆分映射成功 {len(res)}: 识别码 {len(ids)} / 字根 {len(roots)}')
    print('  识别码:', ' '.join(ids))
    print('  字根  :', ' '.join(roots))

# ---- 交叉验证：86 版判定 vs 拆分表 ----
# 98 拆分里，末位 PUA 是真实字根的字，其末码对应字根；对照 86 同字末码是否一致
same = diff = 0
diff_list = []
r98 = dict((c, k) for c, code, k in classify('98', root_chars('98')))
for c, code, k in classify('86', root_chars('86')):
    if c not in r98: continue
    if r98[c] == k: same += 1
    else:
        diff += 1
        diff_list.append(f'{c}:86={code}({k}) 98拆分={r98[c]}')
print(f'\n[86 vs 98拆分] 判定一致 {same}, 不一致 {diff}')
print('  不一致:', ' '.join(diff_list))
