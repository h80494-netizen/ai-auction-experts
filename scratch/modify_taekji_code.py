with open('public/map.html', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the getTaekjiStage definition inside updateTaekjiLayer
old_get_taekji = """                function getTaekjiStage(stepCode) {
                    if (!stepCode) return '초기';
                    const code = stepCode.toUpperCase();
                    if (['PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(code)) return '초기';
                    if (['PP2005'].includes(code)) return '중기';
                    if (['PP2006', 'PP2007'].includes(code)) return '후기';
                    return '초기';
                }"""

new_get_taekji = """                function getTaekjiStage(stepCode) {
                    if (!stepCode) return '초기';
                    const code = stepCode.toUpperCase();
                    if (['PC', 'PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(code)) return '초기';
                    if (['SA', 'DA', 'PP2005'].includes(code)) return '중기';
                    if (['RA', 'CP', 'PP2006', 'PP2007'].includes(code)) return '후기';
                    return '초기';
                }"""

code = code.replace(old_get_taekji.replace('\r\n', '\n'), new_get_taekji.replace('\r\n', '\n'))
code = code.replace(old_get_taekji, new_get_taekji)

# Replace the tooltip stageName mapping inside updateTaekjiLayer
old_tooltip = """                        let stageName = '초기 단계';
                        if (['PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(stepCode)) stageName = '초기 단계 (지구지정 등)';
                        else if (stepCode === 'PP2005') stageName = '중기 단계 (지구계획승인 등)';
                        else if (['PP2006', 'PP2007'].includes(stepCode)) stageName = '후기 단계 (착공/분양 등)';"""

new_tooltip = """                        let stageName = '초기 단계';
                        if (['PC', 'PP2001', 'PP2002', 'PP2003', 'PP2004'].includes(stepCode)) stageName = '초기 단계 (지구지정 등)';
                        else if (['SA', 'DA', 'PP2005'].includes(stepCode)) stageName = '중기 단계 (지구계획승인 등)';
                        else if (['RA', 'CP', 'PP2006', 'PP2007'].includes(stepCode)) stageName = '후기 단계 (착공/분양/완료 등)';"""

code = code.replace(old_tooltip.replace('\r\n', '\n'), new_tooltip.replace('\r\n', '\n'))
code = code.replace(old_tooltip, new_tooltip)

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("getTaekjiStage updated inside map.html successfully!")
