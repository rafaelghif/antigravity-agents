import sys
with open('test_results.log', 'r') as f:
    lines = f.readlines()
    
in_fail = False
for line in lines:
    if line.startswith('======================================================================'):
        in_fail = True
    if line.startswith('----------------------------------------------------------------------') and not in_fail:
        pass
    if line.startswith('Ran ') and in_fail:
        break
    if in_fail:
        print(line, end='')
