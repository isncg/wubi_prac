# -*- coding: utf-8 -*-
# 调研：4 码字的第 4 码能否区分「字根」还是「末尾识别码」。
# 思路：识别码的区号 = 末笔笔画（1横2竖3撇4捺5折）。
#   第 4 码位号 > 3（识别码只占位 1/2/3）→ 必为字根；
#   第 4 码区号 ≠ 末笔区号            → 必为字根；
#   其余（区号相符且位号 ≤3）        → 疑似识别码，需人工复核。
# 末笔取自 wubi86-CJK.txt 的笔顺列（col6=规范笔顺， col7=王码笔顺，仅分歧字才有）。
# 校准：用 3 码非成字字根字（末码必为识别码）检验哪一列符合王码取末笔的习惯。
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 键盘区/位（三版一致）
ROWS = ['GFDSA', 'HJKLM', 'TREWQ', 'YUIOP', 'NBVCX']
ZP = {}
for zi, row in enumerate(ROWS, 1):
    for pi, L in enumerate(row, 1):
        ZP[L] = (zi, pi)

src = open('js/data/chars.js', encoding='utf-8').read()
def block(ver):
    m = re.search(r"'%s': \[(.*?)\n    \]," % ver, src, re.S)
    return re.findall(r"\{c:'(.)',code:'([A-Z]+)'\}", m.group(1))

rows = {}
for line in open('tools/codetables/wubi86-CJK.txt', encoding='utf-8'):
    p = line.rstrip('\n').split(',')
    if len(p) >= 6 and p[1]:
        rows[p[1]] = p

# ---- 校准：3 码非成字字根 → 末码必为识别码，其区号应等于笔顺末笔 ----
# 成字字根判定：字出现在该版本任一键的 roots 里
keys_src = open('js/data/keys.js', encoding='utf-8').read()
def roots_of(ver):
    m = re.search(r'KEYS_%s = \[(.*?)\n  \];' % ver, keys_src, re.S)
    return re.findall(r"roots:\[(.*?)\]", m.group(1))
def root_chars(ver):
    s = set()
    for grp in roots_of(ver):
        s.update(re.findall(r"'(.)'", grp))
    return s

def calibrate(ver, code_col, rootc):
    agree6 = agree7 = bad6 = bad7 = 0
    for c, code in block(ver):
        if len(code) != 3 or c in rootc: continue
        r = rows.get(c)
        if not r: continue
        idL = code[2]; zi = ZP[idL][0]
        s6 = r[5][-1] if len(r) > 5 and r[5] else None
        s7 = r[6][-1] if len(r) > 6 and r[6] else None
        if s6:
            if s6 == str(zi): agree6 += 1
            else: bad6 += 1
        if s7:
            if s7 == str(zi): agree7 += 1
            else: bad7 += 1
    print(f'[{ver}] 校准(3码非成字字根, 末码=识别码): col6 一致 {agree6} / 不符 {bad6}; col7 一致 {agree7} / 不符 {bad7}')

for ver, code_col in [('86', 2), ('98', 3), ('06', 4)]:
    calibrate(ver, code_col, root_chars(ver))

# ---- 测量：4 码字第 4 码的区分度 ----
def stroke_col_for(r, ver):
    # 王码笔顺列(6)存在则优先（覆盖笔顺分歧字），否则用规范笔顺列(5)；返回末笔数字
    if len(r) > 6 and r[6]: return r[6][-1]
    return r[5][-1] if len(r) > 5 and r[5] else None

for ver, code_col in [('86', 2), ('98', 3), ('06', 4)]:
    rootc = root_chars(ver)
    total = len4 = definite_root = presumed = nostroke = 0
    presumed_list = []
    for c, code in block(ver):
        total += 1
        if len(code) != 4: continue
        len4 += 1
        r = rows.get(c)
        s = stroke_col_for(r, ver) if r else None
        if not s:
            nostroke += 1; continue
        L = code[3]; zi, pi = ZP[L]
        if pi > 3 or s != str(zi):
            definite_root += 1
        else:
            presumed += 1
            presumed_list.append(c + code)
    print(f'[{ver}] 总 {total} 字, 4码 {len4}: 判定字根 {definite_root}, 疑似识别码 {presumed}, 缺笔顺 {nostroke}')
    print('   疑似识别码:', ' '.join(presumed_list))
