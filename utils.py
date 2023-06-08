
import pdfkit

def split_orders(orders):
    return [orders[:10]] + [orders[i : i + 15] for i in range(10, len(orders), 15)]


def generate_pdf(html_content):
    options = {
        "page-size": "A4",
        "enable-local-file-access": None,
        "footer-right": "页码:[page]/[topage]",
        "footer-font-size": "8",
        "encoding": "UTF-8",
        "custom-header": [("Accept-Encoding", "gzip")],
        "no-outline": None,
        "dpi": 600,
        "zoom": 1,
        "quiet": "",
        "margin-top": "13mm",
        "margin-bottom": "30mm",
        "margin-left": "18mm",
        "margin-right": "18mm",
    }
    return pdfkit.from_string(html_content, False, options=options)

