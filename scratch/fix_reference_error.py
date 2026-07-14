import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The exact lines to move
vars_to_move = """                const appraisalPrice = item.appraisal_price || item.appraised_value || 0;
                const minBidPrice = item.min_price || item.minimum_value || 0;
                const minBidRate = appraisalPrice > 0 ? (minBidPrice / appraisalPrice * 100) : 0;
                const takeover = calculateEstimatedTakeover(item);
                const yieldRate = calculateYieldRate(item);"""

if vars_to_move in content:
    # Remove them from their original location
    content = content.replace(vars_to_move, "")
    
    # Insert them at the top of the loop
    target = "best3.forEach((item, index) => { try {"
    replacement = target + "\n" + vars_to_move
    content = content.replace(target, replacement)
    
    with open('public/analysis.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully moved variables to fix ReferenceError.")
else:
    print("Could not find the exact variables block. Let me try regex or line by line.")

