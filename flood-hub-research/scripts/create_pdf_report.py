#!/usr/bin/env python3
"""
Convert the comprehensive markdown report to PDF
Uses basic HTML conversion for compatibility
"""

import os

# Simple HTML template for better formatting
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pakistan Flood Hub Comprehensive Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .highlight {{
            background-color: #ffffcc;
            padding: 2px 4px;
        }}
        .warning {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .success {{
            color: #27ae60;
            font-weight: bold;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin-left: 0;
            padding-left: 20px;
            color: #555;
        }}
        @media print {{
            body {{
                font-size: 12pt;
            }}
            h1 {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

def markdown_to_html(markdown_text):
    """Simple markdown to HTML conversion"""
    import re
    
    # Convert headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', markdown_text, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold and italic
    html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Convert code blocks
    html = re.sub(r'```python(.*?)```', r'<pre><code class="python">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```json(.*?)```', r'<pre><code class="json">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```sql(.*?)```', r'<pre><code class="sql">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Convert lists
    html = re.sub(r'^\* (.*)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.*)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive list items
    html = re.sub(r'(<li>.*?</li>\n)+', lambda m: '<ul>\n' + m.group(0) + '</ul>\n', html)
    
    # Convert line breaks
    html = re.sub(r'\n\n', '</p><p>', html)
    html = '<p>' + html + '</p>'
    
    # Clean up
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>(<h[1-6]>)', r'\1', html)
    html = re.sub(r'(</h[1-6]>)</p>', r'\1', html)
    
    # Convert horizontal rules
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    
    return html

def create_pdf_report():
    """Generate PDF from markdown report"""
    print("📄 Creating PDF Report...")
    
    # Read markdown file
    md_path = '../reports/Pakistan_Flood_Hub_Comprehensive_Report.md'
    with open(md_path, 'r') as f:
        markdown_content = f.read()
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content)
    final_html = HTML_TEMPLATE.format(content=html_content)
    
    # Save HTML version
    html_path = '../reports/Pakistan_Flood_Hub_Comprehensive_Report.html'
    with open(html_path, 'w') as f:
        f.write(final_html)
    print(f"✓ HTML version saved to: {html_path}")
    
    # Instructions for PDF conversion
    print("\n📋 To create PDF:")
    print("1. Open the HTML file in your browser")
    print("2. Print to PDF (Cmd+P on Mac, Ctrl+P on Windows)")
    print("3. Or use wkhtmltopdf: wkhtmltopdf report.html report.pdf")
    print("\nAlternatively, use online converter: https://www.ilovepdf.com/html-to-pdf")
    
    # Create a simple text version too
    text_path = '../reports/Pakistan_Flood_Hub_Comprehensive_Report.txt'
    with open(text_path, 'w') as f:
        # Remove markdown formatting for plain text
        text_content = markdown_content
        text_content = re.sub(r'[#*`]', '', text_content)
        text_content = re.sub(r'---', '='*50, text_content)
        f.write(text_content)
    print(f"\n✓ Plain text version saved to: {text_path}")

if __name__ == "__main__":
    import re
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_pdf_report()