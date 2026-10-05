from bleach.css_sanitizer import CSSSanitizer


ALLOWED_TAGS = frozenset({
    # Document sections / structure
    "address", "article", "aside", "div", "footer", "header", "hgroup",
    "main", "nav", "section", "span",
    # Headings
    "h1", "h2", "h3", "h4", "h5", "h6",
    # Text blocks
    "p", "br", "hr", "blockquote", "pre", "figure", "figcaption",
    # Inline text formatting
    "a", "abbr", "acronym", "b", "bdi", "bdo", "big", "cite", "code", "data",
    "del", "dfn", "em", "i", "ins", "kbd", "mark", "q", "rp", "rt", "ruby",
    "s", "samp", "small", "strike", "strong", "sub", "sup", "time", "tt",
    "u", "var", "wbr", "center", "font",
    # Lists
    "ul", "ol", "li", "dl", "dt", "dd", "menu",
    # Tables
    "table", "caption", "colgroup", "col", "thead", "tbody", "tfoot",
    "tr", "th", "td",
    # Interactive-but-safe
    "details", "summary",
    # Media (src is protocol-checked below)
    "img", "picture", "source",
    # Requested explicitly
    "style",
})
 
_GLOBAL_ATTRS = ["class", "id", "title", "lang", "dir", "style", "align", "role", "aria-label", "aria-hidden"]
 
ALLOWED_ATTRIBUTES = {
    "*": _GLOBAL_ATTRS,
    "a": ["href", "target", "rel", "name", "hreflang"],
    "abbr": ["title"],
    "acronym": ["title"],
    "bdo": ["dir"],
    "blockquote": ["cite"],
    "q": ["cite"],
    "col": ["span", "width", "align", "valign"],
    "colgroup": ["span", "width", "align", "valign"],
    "data": ["value"],
    "del": ["cite", "datetime"],
    "ins": ["cite", "datetime"],
    "details": ["open"],
    "font": ["color", "face", "size"],
    "img": ["src", "alt", "width", "height", "loading", "srcset", "sizes"],
    "source": ["src", "srcset", "sizes", "type", "media"],
    "li": ["value"],
    "ol": ["start", "type", "reversed"],
    "ul": ["type"],
    "table": ["border", "cellpadding", "cellspacing", "width", "summary", "bgcolor"],
    "tr": ["valign", "bgcolor"],
    "td": ["colspan", "rowspan", "headers", "valign", "width", "height", "bgcolor", "nowrap"],
    "th": ["colspan", "rowspan", "headers", "scope", "abbr", "valign", "width", "height", "bgcolor", "nowrap"],
    "tbody": ["valign"],
    "thead": ["valign"],
    "tfoot": ["valign"],
    "time": ["datetime"],
    "style": ["media", "type"],
}
 
ALLOWED_PROTOCOLS = frozenset({"http", "https", "mailto", "tel", "data"})
 
# Inline style="" values are filtered through this (default allow-list of safe CSS properties
# is extended with a few extra layout/format ones).
CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=[
        "azimuth", "background", "background-color", "background-image", "background-position",
        "background-repeat", "background-size", "border", "border-bottom", "border-bottom-color",
        "border-bottom-style", "border-bottom-width", "border-collapse", "border-color",
        "border-left", "border-radius", "border-right", "border-spacing", "border-style",
        "border-top", "border-width", "clear", "color", "cursor", "direction", "display",
        "elevation", "float", "font", "font-family", "font-size", "font-style", "font-variant",
        "font-weight", "height", "letter-spacing", "line-height", "list-style",
        "list-style-type", "margin", "margin-bottom", "margin-left", "margin-right",
        "margin-top", "max-height", "max-width", "min-height", "min-width", "opacity",
        "overflow", "padding", "padding-bottom", "padding-left", "padding-right", "padding-top",
        "pitch", "text-align", "text-decoration", "text-indent", "text-transform",
        "unicode-bidi", "vertical-align", "visibility", "white-space", "width", "word-spacing",
        "word-break", "overflow-wrap", "table-layout", "box-shadow", "text-shadow",
    ]
)