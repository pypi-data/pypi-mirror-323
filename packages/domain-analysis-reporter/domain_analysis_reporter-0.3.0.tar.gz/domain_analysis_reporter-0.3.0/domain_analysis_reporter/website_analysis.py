from boilerpy3 import extractors

# This is untested and unused
def extract_text(domain_url, as_list=False):
    extractor = extractors.CanolaExtractor()

    doc = extractor.get_doc_from_url(domain_url)
    page_title = doc.title
    page_contents = doc.content

    if as_list:
        return [ f"{page_title}", f"{page_contents}" ]
    else:
        return f"{page_title}\n{page_contents}"
