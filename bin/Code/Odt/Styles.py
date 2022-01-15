import os
from Code.Odt import XML


class Styles(XML.XML):
    def __init__(self):
        XML.XML.__init__(self, "office:document-styles")
        self.add_param("xmlns:meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0")
        self.add_param("xmlns:office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0")
        self.add_param("xmlns:fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0")
        self.add_param("xmlns:ooo", "http://openoffice.org/2004/office")
        self.add_param("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.add_param("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        self.add_param("xmlns:style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0")
        self.add_param("xmlns:text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0")
        self.add_param("xmlns:draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0")
        self.add_param("xmlns:dr3d", "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0")
        self.add_param("xmlns:svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0")
        self.add_param("xmlns:chart", "urn:oasis:names:tc:opendocument:xmlns:chart:1.0")
        self.add_param("xmlns:rpt", "http://openoffice.org/2005/report")
        self.add_param("xmlns:table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0")
        self.add_param("xmlns:number", "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0")
        self.add_param("xmlns:ooow", "http://openoffice.org/2004/writer")
        self.add_param("xmlns:oooc", "http://openoffice.org/2004/calc")
        self.add_param("xmlns:of", "urn:oasis:names:tc:opendocument:xmlns:of:1.2")
        self.add_param("xmlns:tableooo", "http://openoffice.org/2009/table")
        self.add_param("xmlns:calcext", "urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0")
        self.add_param("xmlns:drawooo", "http://openoffice.org/2010/draw")
        self.add_param("xmlns:loext", "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0")
        self.add_param("xmlns:field", "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0")
        self.add_param("xmlns:math", "http://www.w3.org/1998/Math/MathML")
        self.add_param("xmlns:form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0")
        self.add_param("xmlns:script", "urn:oasis:names:tc:opendocument:xmlns:script:1.0")
        self.add_param("xmlns:dom", "http://www.w3.org/2001/xml-events")
        self.add_param("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
        self.add_param("xmlns:grddl", "http://www.w3.org/2003/g/data-view#")
        self.add_param("xmlns:css3t", "http://www.w3.org/TR/css3-text/")
        self.add_param("xmlns:officeooo", "http://openoffice.org/2009/office")
        self.add_param("office:version", "1.3")
        element1 = XML.Element("office:font-face-decls")
        self.add_content(element1)
        element2 = XML.Element("style:font-face")
        element2.add_param("style:name", "Liberation Sans")
        element2.add_param("svg:font-family", "&apos;Liberation Sans&apos;")
        element2.add_param("style:font-family-generic", "swiss")
        element2.add_param("style:font-pitch", "variable")
        element1.add_content(element2)
        element3 = XML.Element("style:font-face")
        element3.add_param("style:name", "Liberation Serif")
        element3.add_param("svg:font-family", "&apos;Liberation Serif&apos;")
        element3.add_param("style:font-family-generic", "roman")
        element3.add_param("style:font-pitch", "variable")
        element1.add_content(element3)
        element4 = XML.Element("style:font-face")
        element4.add_param("style:name", "Mangal")
        element4.add_param("svg:font-family", "Mangal")
        element4.add_param("style:font-family-generic", "system")
        element4.add_param("style:font-pitch", "variable")
        element1.add_content(element4)
        element5 = XML.Element("style:font-face")
        element5.add_param("style:name", "Mangal1")
        element5.add_param("svg:font-family", "Mangal")
        element1.add_content(element5)
        element6 = XML.Element("style:font-face")
        element6.add_param("style:name", "Microsoft YaHei")
        element6.add_param("svg:font-family", "&apos;Microsoft YaHei&apos;")
        element6.add_param("style:font-family-generic", "system")
        element6.add_param("style:font-pitch", "variable")
        element1.add_content(element6)
        element7 = XML.Element("style:font-face")
        element7.add_param("style:name", "NSimSun")
        element7.add_param("svg:font-family", "NSimSun")
        element7.add_param("style:font-family-generic", "system")
        element7.add_param("style:font-pitch", "variable")
        element1.add_content(element7)
        element8 = XML.Element("office:styles")
        self.add_content(element8)
        element9 = XML.Element("style:default-style")
        element9.add_param("style:family", "graphic")
        element8.add_content(element9)
        element10 = XML.Element("style:graphic-properties")
        element10.add_param("svg:stroke-color", "#3465a4")
        element10.add_param("draw:fill-color", "#729fcf")
        element10.add_param("fo:wrap-option", "no-wrap")
        element10.add_param("draw:shadow-offset-x", "0.3cm")
        element10.add_param("draw:shadow-offset-y", "0.3cm")
        element10.add_param("draw:start-line-spacing-horizontal", "0.283cm")
        element10.add_param("draw:start-line-spacing-vertical", "0.283cm")
        element10.add_param("draw:end-line-spacing-horizontal", "0.283cm")
        element10.add_param("draw:end-line-spacing-vertical", "0.283cm")
        element10.add_param("style:flow-with-text", "false")
        element9.add_content(element10)
        element11 = XML.Element("style:paragraph-properties")
        element11.add_param("style:text-autospace", "ideograph-alpha")
        element11.add_param("style:line-break", "strict")
        element11.add_param("style:writing-mode", "lr-tb")
        element11.add_param("style:font-independent-line-spacing", "false")
        element9.add_content(element11)
        element12 = XML.Element("style:tab-stops")
        element11.add_content(element12)
        element13 = XML.Element("style:text-properties")
        element13.add_param("style:use-window-font-color", "true")
        element13.add_param("loext:opacity", "0%")
        element13.add_param("style:font-name", "Liberation Serif")
        element13.add_param("fo:font-size", "12pt")
        element13.add_param("fo:language", "es")
        element13.add_param("fo:country", "ES")
        element13.add_param("style:letter-kerning", "true")
        element13.add_param("style:font-name-asian", "NSimSun")
        element13.add_param("style:font-size-asian", "10.5pt")
        element13.add_param("style:language-asian", "zh")
        element13.add_param("style:country-asian", "CN")
        element13.add_param("style:font-name-complex", "Mangal")
        element13.add_param("style:font-size-complex", "12pt")
        element13.add_param("style:language-complex", "hi")
        element13.add_param("style:country-complex", "IN")
        element9.add_content(element13)
        element14 = XML.Element("style:default-style")
        element14.add_param("style:family", "paragraph")
        element8.add_content(element14)
        element15 = XML.Element("style:paragraph-properties")
        element15.add_param("fo:orphans", "2")
        element15.add_param("fo:widows", "2")
        element15.add_param("fo:hyphenation-ladder-count", "no-limit")
        element15.add_param("style:text-autospace", "ideograph-alpha")
        element15.add_param("style:punctuation-wrap", "hanging")
        element15.add_param("style:line-break", "strict")
        element15.add_param("style:tab-stop-distance", "1.251cm")
        element15.add_param("style:writing-mode", "page")
        element14.add_content(element15)
        element16 = XML.Element("style:text-properties")
        element16.add_param("style:use-window-font-color", "true")
        element16.add_param("loext:opacity", "0%")
        element16.add_param("style:font-name", "Liberation Serif")
        element16.add_param("fo:font-size", "12pt")
        element16.add_param("fo:language", "es")
        element16.add_param("fo:country", "ES")
        element16.add_param("style:letter-kerning", "true")
        element16.add_param("style:font-name-asian", "NSimSun")
        element16.add_param("style:font-size-asian", "10.5pt")
        element16.add_param("style:language-asian", "zh")
        element16.add_param("style:country-asian", "CN")
        element16.add_param("style:font-name-complex", "Mangal")
        element16.add_param("style:font-size-complex", "12pt")
        element16.add_param("style:language-complex", "hi")
        element16.add_param("style:country-complex", "IN")
        element16.add_param("fo:hyphenate", "false")
        element16.add_param("fo:hyphenation-remain-char-count", "2")
        element16.add_param("fo:hyphenation-push-char-count", "2")
        element16.add_param("loext:hyphenation-no-caps", "false")
        element14.add_content(element16)
        element17 = XML.Element("style:default-style")
        element17.add_param("style:family", "table")
        element8.add_content(element17)
        element18 = XML.Element("style:table-properties")
        element18.add_param("table:border-model", "collapsing")
        element17.add_content(element18)
        element19 = XML.Element("style:default-style")
        element19.add_param("style:family", "table-row")
        element8.add_content(element19)
        element20 = XML.Element("style:table-row-properties")
        element20.add_param("fo:keep-together", "auto")
        element19.add_content(element20)
        element21 = XML.Element("style:style")
        element21.add_param("style:name", "Standard")
        element21.add_param("style:family", "paragraph")
        element21.add_param("style:class", "text")
        element8.add_content(element21)
        element22 = XML.Element("style:style")
        element22.add_param("style:name", "Heading")
        element22.add_param("style:family", "paragraph")
        element22.add_param("style:parent-style-name", "Standard")
        element22.add_param("style:next-style-name", "Text_20_body")
        element22.add_param("style:class", "text")
        element8.add_content(element22)
        element23 = XML.Element("style:paragraph-properties")
        element23.add_param("fo:margin-top", "0.423cm")
        element23.add_param("fo:margin-bottom", "0.212cm")
        element23.add_param("style:contextual-spacing", "false")
        element23.add_param("fo:keep-with-next", "always")
        element22.add_content(element23)
        element24 = XML.Element("style:text-properties")
        element24.add_param("style:font-name", "Liberation Sans")
        element24.add_param("fo:font-family", "&apos;Liberation Sans&apos;")
        element24.add_param("style:font-family-generic", "swiss")
        element24.add_param("style:font-pitch", "variable")
        element24.add_param("fo:font-size", "14pt")
        element24.add_param("style:font-name-asian", "Microsoft YaHei")
        element24.add_param("style:font-family-asian", "&apos;Microsoft YaHei&apos;")
        element24.add_param("style:font-family-generic-asian", "system")
        element24.add_param("style:font-pitch-asian", "variable")
        element24.add_param("style:font-size-asian", "14pt")
        element24.add_param("style:font-name-complex", "Mangal")
        element24.add_param("style:font-family-complex", "Mangal")
        element24.add_param("style:font-family-generic-complex", "system")
        element24.add_param("style:font-pitch-complex", "variable")
        element24.add_param("style:font-size-complex", "14pt")
        element22.add_content(element24)
        element25 = XML.Element("style:style")
        element25.add_param("style:name", "Text_20_body")
        element25.add_param("style:display-name", "Text body")
        element25.add_param("style:family", "paragraph")
        element25.add_param("style:parent-style-name", "Standard")
        element25.add_param("style:class", "text")
        element8.add_content(element25)
        element26 = XML.Element("style:paragraph-properties")
        element26.add_param("fo:margin-top", "0cm")
        element26.add_param("fo:margin-bottom", "0.247cm")
        element26.add_param("style:contextual-spacing", "false")
        element26.add_param("fo:line-height", "115%")
        element25.add_content(element26)
        element27 = XML.Element("style:style")
        element27.add_param("style:name", "List")
        element27.add_param("style:family", "paragraph")
        element27.add_param("style:parent-style-name", "Text_20_body")
        element27.add_param("style:class", "list")
        element8.add_content(element27)
        element28 = XML.Element("style:text-properties")
        element28.add_param("style:font-size-asian", "12pt")
        element28.add_param("style:font-name-complex", "Mangal1")
        element28.add_param("style:font-family-complex", "Mangal")
        element27.add_content(element28)
        element29 = XML.Element("style:style")
        element29.add_param("style:name", "Caption")
        element29.add_param("style:family", "paragraph")
        element29.add_param("style:parent-style-name", "Standard")
        element29.add_param("style:class", "extra")
        element8.add_content(element29)
        element30 = XML.Element("style:paragraph-properties")
        element30.add_param("fo:margin-top", "0.212cm")
        element30.add_param("fo:margin-bottom", "0.212cm")
        element30.add_param("style:contextual-spacing", "false")
        element30.add_param("text:number-lines", "false")
        element30.add_param("text:line-number", "0")
        element29.add_content(element30)
        element31 = XML.Element("style:text-properties")
        element31.add_param("fo:font-size", "12pt")
        element31.add_param("fo:font-style", "italic")
        element31.add_param("style:font-size-asian", "12pt")
        element31.add_param("style:font-style-asian", "italic")
        element31.add_param("style:font-name-complex", "Mangal1")
        element31.add_param("style:font-family-complex", "Mangal")
        element31.add_param("style:font-size-complex", "12pt")
        element31.add_param("style:font-style-complex", "italic")
        element29.add_content(element31)
        element32 = XML.Element("style:style")
        element32.add_param("style:name", "Index")
        element32.add_param("style:family", "paragraph")
        element32.add_param("style:parent-style-name", "Standard")
        element32.add_param("style:class", "index")
        element8.add_content(element32)
        element33 = XML.Element("style:paragraph-properties")
        element33.add_param("text:number-lines", "false")
        element33.add_param("text:line-number", "0")
        element32.add_content(element33)
        element34 = XML.Element("style:text-properties")
        element34.add_param("fo:language", "zxx")
        element34.add_param("fo:country", "none")
        element34.add_param("style:font-size-asian", "12pt")
        element34.add_param("style:language-asian", "zxx")
        element34.add_param("style:country-asian", "none")
        element34.add_param("style:font-name-complex", "Mangal1")
        element34.add_param("style:font-family-complex", "Mangal")
        element34.add_param("style:language-complex", "zxx")
        element34.add_param("style:country-complex", "none")
        element32.add_content(element34)
        element35 = XML.Element("style:style")
        element35.add_param("style:name", "Header_20_and_20_Footer")
        element35.add_param("style:display-name", "Header and Footer")
        element35.add_param("style:family", "paragraph")
        element35.add_param("style:parent-style-name", "Standard")
        element35.add_param("style:class", "extra")
        element8.add_content(element35)
        element36 = XML.Element("style:paragraph-properties")
        element36.add_param("text:number-lines", "false")
        element36.add_param("text:line-number", "0")
        element35.add_content(element36)
        element37 = XML.Element("style:tab-stops")
        element36.add_content(element37)
        element38 = XML.Element("style:tab-stop")
        element38.add_param("style:position", "12.85cm")
        element38.add_param("style:type", "center")
        element37.add_content(element38)
        element39 = XML.Element("style:tab-stop")
        element39.add_param("style:position", "25.7cm")
        element39.add_param("style:type", "right")
        element37.add_content(element39)
        element40 = XML.Element("style:style")
        element40.add_param("style:name", "Header")
        element40.add_param("style:family", "paragraph")
        element40.add_param("style:parent-style-name", "Header_20_and_20_Footer")
        element40.add_param("style:class", "extra")
        element8.add_content(element40)
        element41 = XML.Element("style:paragraph-properties")
        element41.add_param("text:number-lines", "false")
        element41.add_param("text:line-number", "0")
        element40.add_content(element41)
        element42 = XML.Element("style:tab-stops")
        element41.add_content(element42)
        element43 = XML.Element("style:tab-stop")
        element43.add_param("style:position", "12.85cm")
        element43.add_param("style:type", "center")
        element42.add_content(element43)
        element44 = XML.Element("style:tab-stop")
        element44.add_param("style:position", "25.7cm")
        element44.add_param("style:type", "right")
        element42.add_content(element44)
        element45 = XML.Element("style:style")
        element45.add_param("style:name", "Footer")
        element45.add_param("style:family", "paragraph")
        element45.add_param("style:parent-style-name", "Header_20_and_20_Footer")
        element45.add_param("style:class", "extra")
        element8.add_content(element45)
        element46 = XML.Element("style:paragraph-properties")
        element46.add_param("text:number-lines", "false")
        element46.add_param("text:line-number", "0")
        element45.add_content(element46)
        element47 = XML.Element("style:tab-stops")
        element46.add_content(element47)
        element48 = XML.Element("style:tab-stop")
        element48.add_param("style:position", "12.85cm")
        element48.add_param("style:type", "center")
        element47.add_content(element48)
        element49 = XML.Element("style:tab-stop")
        element49.add_param("style:position", "25.7cm")
        element49.add_param("style:type", "right")
        element47.add_content(element49)
        element50 = XML.Element("style:style")
        element50.add_param("style:name", "Figure")
        element50.add_param("style:family", "paragraph")
        element50.add_param("style:parent-style-name", "Caption")
        element50.add_param("style:class", "extra")
        element8.add_content(element50)
        element51 = XML.Element("style:style")
        element51.add_param("style:name", "Graphics")
        element51.add_param("style:family", "graphic")
        element8.add_content(element51)
        element52 = XML.Element("style:graphic-properties")
        element52.add_param("text:anchor-type", "paragraph")
        element52.add_param("svg:x", "0cm")
        element52.add_param("svg:y", "0cm")
        element52.add_param("style:wrap", "dynamic")
        element52.add_param("style:number-wrapped-paragraphs", "no-limit")
        element52.add_param("style:wrap-contour", "false")
        element52.add_param("style:vertical-pos", "top")
        element52.add_param("style:vertical-rel", "paragraph")
        element52.add_param("style:horizontal-pos", "center")
        element52.add_param("style:horizontal-rel", "paragraph")
        element51.add_content(element52)
        element53 = XML.Element("style:style")
        element53.add_param("style:name", "Frame")
        element53.add_param("style:family", "graphic")
        element8.add_content(element53)
        element54 = XML.Element("style:graphic-properties")
        element54.add_param("text:anchor-type", "paragraph")
        element54.add_param("svg:x", "0cm")
        element54.add_param("svg:y", "0cm")
        element54.add_param("fo:margin-left", "0.201cm")
        element54.add_param("fo:margin-right", "0.201cm")
        element54.add_param("fo:margin-top", "0.201cm")
        element54.add_param("fo:margin-bottom", "0.201cm")
        element54.add_param("style:wrap", "parallel")
        element54.add_param("style:number-wrapped-paragraphs", "no-limit")
        element54.add_param("style:wrap-contour", "false")
        element54.add_param("style:vertical-pos", "top")
        element54.add_param("style:vertical-rel", "paragraph-content")
        element54.add_param("style:horizontal-pos", "center")
        element54.add_param("style:horizontal-rel", "paragraph-content")
        element54.add_param("fo:padding", "0.15cm")
        element54.add_param("fo:border", "0.06pt solid #000000")
        element53.add_content(element54)
        element55 = XML.Element("text:outline-style")
        element55.add_param("style:name", "Outline")
        element8.add_content(element55)
        element56 = XML.Element("text:outline-level-style")
        element56.add_param("text:level", "1")
        element56.add_param("loext:num-list-format", "%1%")
        element56.add_param("style:num-format", "")
        element55.add_content(element56)
        element57 = XML.Element("style:list-level-properties")
        element57.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element56.add_content(element57)
        element58 = XML.Element("style:list-level-label-alignment")
        element58.add_param("text:label-followed-by", "listtab")
        element57.add_content(element58)
        element59 = XML.Element("text:outline-level-style")
        element59.add_param("text:level", "2")
        element59.add_param("loext:num-list-format", "%2%")
        element59.add_param("style:num-format", "")
        element55.add_content(element59)
        element60 = XML.Element("style:list-level-properties")
        element60.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element59.add_content(element60)
        element61 = XML.Element("style:list-level-label-alignment")
        element61.add_param("text:label-followed-by", "listtab")
        element60.add_content(element61)
        element62 = XML.Element("text:outline-level-style")
        element62.add_param("text:level", "3")
        element62.add_param("loext:num-list-format", "%3%")
        element62.add_param("style:num-format", "")
        element55.add_content(element62)
        element63 = XML.Element("style:list-level-properties")
        element63.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element62.add_content(element63)
        element64 = XML.Element("style:list-level-label-alignment")
        element64.add_param("text:label-followed-by", "listtab")
        element63.add_content(element64)
        element65 = XML.Element("text:outline-level-style")
        element65.add_param("text:level", "4")
        element65.add_param("loext:num-list-format", "%4%")
        element65.add_param("style:num-format", "")
        element55.add_content(element65)
        element66 = XML.Element("style:list-level-properties")
        element66.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element65.add_content(element66)
        element67 = XML.Element("style:list-level-label-alignment")
        element67.add_param("text:label-followed-by", "listtab")
        element66.add_content(element67)
        element68 = XML.Element("text:outline-level-style")
        element68.add_param("text:level", "5")
        element68.add_param("loext:num-list-format", "%5%")
        element68.add_param("style:num-format", "")
        element55.add_content(element68)
        element69 = XML.Element("style:list-level-properties")
        element69.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element68.add_content(element69)
        element70 = XML.Element("style:list-level-label-alignment")
        element70.add_param("text:label-followed-by", "listtab")
        element69.add_content(element70)
        element71 = XML.Element("text:outline-level-style")
        element71.add_param("text:level", "6")
        element71.add_param("loext:num-list-format", "%6%")
        element71.add_param("style:num-format", "")
        element55.add_content(element71)
        element72 = XML.Element("style:list-level-properties")
        element72.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element71.add_content(element72)
        element73 = XML.Element("style:list-level-label-alignment")
        element73.add_param("text:label-followed-by", "listtab")
        element72.add_content(element73)
        element74 = XML.Element("text:outline-level-style")
        element74.add_param("text:level", "7")
        element74.add_param("loext:num-list-format", "%7%")
        element74.add_param("style:num-format", "")
        element55.add_content(element74)
        element75 = XML.Element("style:list-level-properties")
        element75.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element74.add_content(element75)
        element76 = XML.Element("style:list-level-label-alignment")
        element76.add_param("text:label-followed-by", "listtab")
        element75.add_content(element76)
        element77 = XML.Element("text:outline-level-style")
        element77.add_param("text:level", "8")
        element77.add_param("loext:num-list-format", "%8%")
        element77.add_param("style:num-format", "")
        element55.add_content(element77)
        element78 = XML.Element("style:list-level-properties")
        element78.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element77.add_content(element78)
        element79 = XML.Element("style:list-level-label-alignment")
        element79.add_param("text:label-followed-by", "listtab")
        element78.add_content(element79)
        element80 = XML.Element("text:outline-level-style")
        element80.add_param("text:level", "9")
        element80.add_param("loext:num-list-format", "%9%")
        element80.add_param("style:num-format", "")
        element55.add_content(element80)
        element81 = XML.Element("style:list-level-properties")
        element81.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element80.add_content(element81)
        element82 = XML.Element("style:list-level-label-alignment")
        element82.add_param("text:label-followed-by", "listtab")
        element81.add_content(element82)
        element83 = XML.Element("text:outline-level-style")
        element83.add_param("text:level", "10")
        element83.add_param("loext:num-list-format", "%10%")
        element83.add_param("style:num-format", "")
        element55.add_content(element83)
        element84 = XML.Element("style:list-level-properties")
        element84.add_param("text:list-level-position-and-space-mode", "label-alignment")
        element83.add_content(element84)
        element85 = XML.Element("style:list-level-label-alignment")
        element85.add_param("text:label-followed-by", "listtab")
        element84.add_content(element85)
        element86 = XML.Element("text:notes-configuration")
        element86.add_param("text:note-class", "footnote")
        element86.add_param("style:num-format", "1")
        element86.add_param("text:start-value", "0")
        element86.add_param("text:footnotes-position", "page")
        element86.add_param("text:start-numbering-at", "document")
        element8.add_content(element86)
        element87 = XML.Element("text:notes-configuration")
        element87.add_param("text:note-class", "endnote")
        element87.add_param("style:num-format", "i")
        element87.add_param("text:start-value", "0")
        element8.add_content(element87)
        element88 = XML.Element("text:linenumbering-configuration")
        element88.add_param("text:number-lines", "false")
        element88.add_param("text:offset", "0.499cm")
        element88.add_param("style:num-format", "1")
        element88.add_param("text:number-position", "left")
        element88.add_param("text:increment", "5")
        element8.add_content(element88)
        element89 = XML.Element("office:automatic-styles")
        self.add_content(element89)
        element90 = XML.Element("style:style")
        element90.add_param("style:name", "MP1")
        element90.add_param("style:family", "paragraph")
        element90.add_param("style:parent-style-name", "Header")
        element89.add_content(element90)
        element91 = XML.Element("style:paragraph-properties")
        element91.add_param("fo:text-align", "center")
        element91.add_param("style:justify-single-word", "false")
        element90.add_content(element91)
        element92 = XML.Element("style:text-properties")
        element92.add_param("fo:font-weight", "bold")
        element92.add_param("officeooo:rsid", "00033015")
        element92.add_param("officeooo:paragraph-rsid", "00033015")
        element92.add_param("style:font-weight-asian", "bold")
        element92.add_param("style:font-weight-complex", "bold")
        element90.add_content(element92)
        element93 = XML.Element("style:style")
        element93.add_param("style:name", "MP2")
        element93.add_param("style:family", "paragraph")
        element93.add_param("style:parent-style-name", "Footer")
        element89.add_content(element93)
        element94 = XML.Element("style:paragraph-properties")
        element94.add_param("fo:text-align", "end")
        element94.add_param("style:justify-single-word", "false")
        element93.add_content(element94)
        element95 = XML.Element("style:page-layout")
        element95.add_param("style:name", "Mpm1")
        element89.add_content(element95)
        element96 = XML.Element("style:page-layout-properties")
        element96.add_param("fo:page-width", "29.7cm")
        element96.add_param("fo:page-height", "21.001cm")
        element96.add_param("style:num-format", "1")
        element96.add_param("style:print-orientation", "landscape")
        element96.add_param("fo:margin-top", "2cm")
        element96.add_param("fo:margin-bottom", "2cm")
        element96.add_param("fo:margin-left", "2cm")
        element96.add_param("fo:margin-right", "2cm")
        element96.add_param("style:writing-mode", "lr-tb")
        element96.add_param("style:layout-grid-color", "#c0c0c0")
        element96.add_param("style:layout-grid-lines", "20")
        element96.add_param("style:layout-grid-base-height", "0.706cm")
        element96.add_param("style:layout-grid-ruby-height", "0.353cm")
        element96.add_param("style:layout-grid-mode", "none")
        element96.add_param("style:layout-grid-ruby-below", "false")
        element96.add_param("style:layout-grid-print", "false")
        element96.add_param("style:layout-grid-display", "false")
        element96.add_param("style:footnote-max-height", "0cm")
        element96.add_param("loext:margin-gutter", "0cm")
        element95.add_content(element96)
        element97 = XML.Element("style:footnote-sep")
        element97.add_param("style:width", "0.018cm")
        element97.add_param("style:distance-before-sep", "0.101cm")
        element97.add_param("style:distance-after-sep", "0.101cm")
        element97.add_param("style:line-style", "solid")
        element97.add_param("style:adjustment", "left")
        element97.add_param("style:rel-width", "25%")
        element97.add_param("style:color", "#000000")
        element96.add_content(element97)
        element98 = XML.Element("style:header-style")
        element95.add_content(element98)
        element99 = XML.Element("style:header-footer-properties")
        element99.add_param("fo:min-height", "0cm")
        element99.add_param("fo:margin-left", "0cm")
        element99.add_param("fo:margin-right", "0cm")
        element99.add_param("fo:margin-bottom", "0.499cm")
        element99.add_param("fo:background-color", "transparent")
        element99.add_param("draw:fill", "none")
        element99.add_param("draw:fill-color", "#729fcf")
        element98.add_content(element99)
        element100 = XML.Element("style:footer-style")
        element95.add_content(element100)
        element101 = XML.Element("style:header-footer-properties")
        element101.add_param("fo:min-height", "0cm")
        element101.add_param("fo:margin-top", "0.499cm")
        element101.add_param("fo:background-color", "transparent")
        element101.add_param("draw:fill", "none")
        element100.add_content(element101)
        element102 = XML.Element("style:style")
        element102.add_param("style:name", "Mdp1")
        element102.add_param("style:family", "drawing-page")
        element89.add_content(element102)
        element103 = XML.Element("style:drawing-page-properties")
        element103.add_param("draw:background-size", "full")
        element102.add_content(element103)
        element104 = XML.Element("office:master-styles")
        self.add_content(element104)
        element105 = XML.Element("style:master-page")
        element105.add_param("style:name", "Standard")
        element105.add_param("style:page-layout-name", "Mpm1")
        element105.add_param("draw:style-name", "Mdp1")
        element104.add_content(element105)
        element106 = XML.Element("style:header")
        element105.add_content(element106)
        element107 = XML.Element("text:p")
        element107.add_param("text:style-name", "MP1")
        element106.add_content(element107)
        element107.set_value("Lucas Chess - Best Move Training: hh")
        element108 = XML.Element("style:footer")
        element105.add_content(element108)
        element109 = XML.Element("text:p")
        element109.add_param("text:style-name", "MP2")
        element108.add_content(element109)
        element110 = XML.Element("text:page-number")
        element110.add_param("text:select-page", "current")
        element109.add_content(element110)
        element110.set_value("41")
        element110.set_later("/")
        element111 = XML.Element("text:page-count")
        element109.add_content(element111)
        element111.set_value("41")

    def run(self, folder):
        path = os.path.join(folder, "styles.xml")
        self.save(path)

    def landscape(self):
        """        element71 = XML.Element("style:page-layout-properties")
        element71.add_param("fo:page-width", "21.001cm")
        element71.add_param("fo:page-height", "29.7cm")
        element71.add_param("style:num-format", "1")
        element71.add_param("style:print-orientation", "portrait")
        """
        element = self.seek("style:page-layout-properties")
        element.change_param("fo:page-height", "21.00cm")
        element.change_param("fo:page-width", "29.70cm")
        element.change_param("style:print-orientation", "landscape")

    def header(self, txt):
        element = self.seek_param_key("text:p", "text:style-name", "MP1")
        element.set_value(txt)


