##parameters=ndiff

lines = ndiff.split('\n')
lines = [l.replace('+\n','') for l in lines]
lines = [l.replace('-\n','') for l in lines]

result = []

for line in lines:
    css_class = None
    if line.startswith('+'):
        css_class = 'pos_diff'
    if line.startswith('-'):
        css_class = 'neg_diff'
    result.append( {'css_class':css_class,'line':line} )

return result
