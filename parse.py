import re
html = open('leetcode_dump.html', encoding='utf-8').read()
links = re.findall(r'<a[^>]+href=[\'\"](/problems/[^\'\"]+)[\'\"][^>]*>(.*?)</a>', html)
for href, text in links:
    # remove inner tags from text
    text = re.sub(r'<[^>]+>', '', text)
    print(href, text)
