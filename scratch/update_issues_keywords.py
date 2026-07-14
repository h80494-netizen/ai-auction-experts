import re

with open('public/issues.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the source condition
source_pattern = r"\(i\.source\.includes\('지자체'\) \|\| i\.source\.includes\('청'\) \|\| i\.title\.includes\('지자체'\) \|\| i\.title\.includes\('고시공고'\)\) &&"
source_replacement = "(i.source.includes('지자체') || i.source.includes('청') || i.title.includes('지자체') || i.title.includes('고시공고') || i.source.includes('의회') || i.source.includes('의사록') || i.title.includes('고시') || i.title.includes('공시')) &&"

content = re.sub(source_pattern, source_replacement, content)

# Update the title condition
title_pattern = r"i\.title\.includes\('개발진흥지구'\) \|\|"
title_replacement = "i.title.includes('재개발') || i.title.includes('재건축') || i.title.includes('정비예정구역') || i.title.includes('고시') || i.title.includes('공시') || i.title.includes('의회') || i.title.includes('의사록') || i.title.includes('논의') || i.title.includes('개발진흥지구') ||"

content = re.sub(title_pattern, title_replacement, content)

# Update the keyword condition
keyword_pattern = r"i\.keywords\.includes\('지자체'\)\n"
keyword_replacement = "i.keywords.includes('지자체') || i.keywords.includes('재개발') || i.keywords.includes('재건축') || i.keywords.includes('정비예정구역') || i.keywords.includes('고시') || i.keywords.includes('공시') || i.keywords.includes('의회') || i.keywords.includes('의사록') || i.keywords.includes('논의')\n"

content = re.sub(keyword_pattern, keyword_replacement, content)

with open('public/issues.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated issues.html")
