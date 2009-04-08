## Script (Python) "exportStatistics"
##parameters=format='tab'
##title=
##

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

from AccessControl import getSecurityManager
ecab_utils = context.ecab_utils

exportFormat = ['tab', '\t', '\n', '"', '"', '"']
colDelim     = exportFormat[1]
rowDelim     = exportFormat[2]
strStart     = exportFormat[3]
strEnd       = exportFormat[4]
escapeChar   = exportFormat[5]
exportEncoding = 'iso-8859-15'
siteEncoding   = context.getCharset()
isReviewer     = getSecurityManager().checkPermission('Review portal content',
                                                      context)

def escape(string):
    escaped = ''
    for c in string:
        if(c in [escapeChar, strStart, strEnd]):
            escaped += escapeChar + c
        else:
            escaped += c
    return escaped.decode(siteEncoding).encode(exportEncoding)

###############################################################################

data = context.summarize()
table  = []
output = ''

# Table heading
output += '%s\t' % '\t'.join(('"user name"', '"full name"', '"title"',
                              '"e-mail"', '"ID"', '"major"', '"assignments"'))
output += '%s\n' % '\t'.join(ecab_utils.getWfStates())

# Create a table containing all required data
for userName in data.keys():
    fullname  = ecab_utils.getFullNameById(userName)
    email     = ecab_utils.getUserPropertyById(userName, 'email')
    studentid = ecab_utils.getUserPropertyById(userName,
                                               context.portal_properties.ecab_properties.student_id_attr) or ""
    major     = ecab_utils.getUserPropertyById(userName,
                                               context.portal_properties.ecab_properties.major_attr) or ""
    perstitle = ecab_utils.getUserPropertyById(userName,
                                               context.portal_properties.ecab_properties.personal_title_attr) or ""
    n_boxes   = context.countContainedBoxes()
    
    row = [userName, fullname, perstitle, email, studentid, major, n_boxes]
    row.extend(data[userName])

    table.append(row)

# Sort the table by full name
table.sort(lambda a, b: cmp(a[1], b[1]))

# Create the output
for row in table:
    for i in range(0, len(row)):
        col = row[i]
        if(same_type(col, '') or same_type(col, u'')):
            output += strStart + escape(col) + strEnd
        elif(same_type(col, 1.1)):
            output += escape(ecab_utils.localizeNumber("%.2f", col))
        else:
            output += escape(str(col))
        
        # append column delimiter or row delimiter
        output += [colDelim, rowDelim][i >= (len(row) - 1)]

###############################################################################

filename = '%s_%s.%s' % (ecab_utils.pathQuote(context.getId()),
                         'statistics', format)

if not isReviewer:
    filename = str(REQUEST.AUTHENTICATED_USER) + '_' + filename

#RESPONSE.setHeader('Content-Disposition', 'inline') # Useful for debugging
RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
RESPONSE.setHeader('Content-Type', 'text/plain')

return output
