from Products.PortalTransforms.libtransforms.retransform import retransform

class html_to_text(retransform):
    inputs  = ('text/html',)
    output = 'text/plain'

def register():
    # XXX convert entites with htmlentitydefs.name2codepoint ?
    return html_to_text("html_to_text",
                       ('<script [^>]>.*</script>(?im)', ' '),
                       ('<style [^>]>.*</style>(?im)', ' '),
                       ('<head [^>]>.*</head>(?im)', ' '),
                       ('(?im)</?(font|em|i|strong|b)(?=\W)[^>]*>', ''),
                       ('<[^>]*>(?i)(?m)', ' '),
                       )
