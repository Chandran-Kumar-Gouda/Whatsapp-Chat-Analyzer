import pdfkit
import tempfile

def generate_report(html_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        pdfkit.from_string(html_content, f.name, options={"encoding": "UTF-8"})
        return f.name
