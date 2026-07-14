import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the double-spacing issue
lines = [line for line in text.splitlines() if line.strip() != '']
text = '\n'.join(lines)

# The correct block using unicode escapes to avoid encoding errors in powershell/python
correct_block = """                if (matchedLayers.some(l => l.includes('\uc7ac\uac1c\ubc1c') || l.includes('\uc7ac\uac74\ucd95') || l.includes('\uc815\ube44'))) {
                    devDetails.push("\uc815\ube44\uc0ac\uc5c5\uc9c0\uad6c \ucd94\uc9c4 \ud638\uc7ac\uc640 \uc9c1\uacb0\ub418\uc5b4 \uc778\uadfc \ub178\ud6c4 \uc9c0\uc5ed\uc758 \uc815\ube44 \ubc0f \ud604\ub300\ud654\uc5d0 \ub530\ub978 \ud504\ub9ac\ubbf8\uc5c4 \uc9c0\uac00 \uc0c1\uc2b9 \uc5ec\ub825\uc774 \ub300\ub2e8\ud788 \uac15\ub825\ud569\ub2c8\ub2e4.");
                }
                if (matchedLayers.some(l => l.includes('\ud0dd\uc9c0'))) {
                    devDetails.push("\ud0dd\uc9c0\uac1c\ubc1c\uc9c0\uad6c\uc5d0 \uc815\ubc00 \uc5f0\uc811\ud558\uc5ec \ub300\uaddc\ubaa8 \uacf5\uacf5 \uc8fc\uac70\uc9c0 \uc870\uc131\uc5d0 \ub530\ub978 \ub3c4\ub85c \ud655\uc7a5, \uc2e0\ucd95 \ubc30\ud6c4 \ub2e8\uc9c0 \ub4f1 \uc2e0\ud765 \uc8fc\uac70 \ubca8\ud2b8 \ud615\uc131\uc758 \uac00\uce58 \uc0c1\uc2b9 \ud61c\ud0dd\uc744 \uc120\uc810\ud569\ub2c8\ub2e4.");
                }
                if (matchedLayers.some(l => l.includes('\uac1c\ubc1c\ud589\uc704') || l.includes('\uc81c\ud55c\uc9c0\uc5ed'))) {
                    devDetails.push("\uac1c\ubc1c\ud589\uc704\ud5c8\uac00\uc81c\ud55c\uc9c0\uc5ed \ub0b4\uc5d0 \uc704\uce58\ud558\uc5ec \ud5a5\ud6c4 \ubcf8\uaca9\uc801\uc778 \uac1c\ubc1c \uacc4\ud68d\uc758 \uc218\ub9bd \ubc0f \uad6c\uc5ed \uc9c0\uc815\uc5d0 \ub530\ub978 \ud504\ub9ac\ubbf8\uc5c4 \uc9c0\uac00 \uc0c1\uc2b9 \uc5ec\ub825\uc774 \uac15\ub825\ud558\uac8c \uc874\uc7ac\ud569\ub2c8\ub2e4.");
                }
                if (matchedLayers.some(l => l.includes('\ub3c4\ub85c') || l.includes('\ub178\uc120') || l.includes('\uacc4\ud68d\uc120'))) {
                    devDetails.push("\ub3c4\uc2dc\uacc4\ud68d\ub3c4\ub85c \uc2e0\uc124 \ubc0f \uc9c4\uc785\ub85c \uc5f0\uacb0 \ud638\uc7ac\uc120\uc5d0 \uac78\uccd0 \ucc28\ub7c9 \ubc0f \ubcf4\ud589\uc790 \uc811\uadfc\uc131\uc774 \ud68d\uae30\uc801\uc73c\ub85c \ud5a5\uc0c1\ub418\ub294 \uc9c0\uac00 \uc0c1\uc2b9 \ud2b8\ub9ac\uac70\ub97c \uac16\ucdb0\uc2b5\ub2c8\ub2e4.");
                }
                
                if (devDetails.length > 0) {
                    valueAnalysis = `\ubcf8 \ubb3c\uac74\uc740 <strong>${matchedLayersStr}</strong> \uad8c\uc5ed \ub0b4\uc5d0 \uc704\uce58\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4. ${subwayStr}, ${devDetails.join(' ')}`;
                } else {
                    valueAnalysis = `\ubcf8 \ubb3c\uac74\uc740 ${subwayStr}, \uae30\ubcf8 \ubc30\ud6c4 \uc784\ub300\uc218\uc694 \ubc0f \uc815\uc8fc \uc0dd\ud65c\uad8c \uc778\ud504\ub77c\uac00 \uacac\uace0\ud558\uac8c \uc720\uc9c0\ub418\ub294 \uc9c0\uc810\uc785\ub2c8\ub2e4. \ud558\ubc29 \uacbd\uc9c1\uc131\uc774 \uac15\ub825\ud558\uc5ec \uc2dc\uc138 \ud558\ub77d \ub9ac\uc2a4\ud06c\uac00 \ub9e4\uc6b0 \ub0ae\uace0 \uc911\uc7a5\uae30 \uc9c0\uac00 \uc548\uc815\uc774 \ud655\uc2e4\uc2dc\ub429\ub2c8\ub2e4.`;
                }"""

# Using regex to find the corrupted block
# The start is around 'let devDetails = [];' which should be untouched.
start_str = "let devDetails = [];"
start_idx = text.find(start_str)

if start_idx != -1:
    end_str = "let claimsAnalysis = \"\";"
    end_idx = text.find(end_str, start_idx)
    
    if end_idx != -1:
        # Reconstruct exactly:
        final_text = text[:start_idx + len(start_str)] + '\n' + correct_block + '\n                // 2. Differentiated Claims/Takeover Risk analysis (\uc120\uc21c\uc704 \uc778\uc218\uae08\uc561 \uc815\ubc00 \ubd84\uc11d)\n                ' + text[end_idx:]
        with open('public/analysis.html', 'w', encoding='utf-8') as f:
            f.write(final_text)
        print("SUCCESS")
    else:
        print("End string not found")
else:
    print("Start string not found")
