import re

regex = re.compile("somevalue\\(([^\\(\\)]+)\\)")
rst = regex.match("somevalue(adfadsfdf)")
if rst:
    print(rst.group(1))