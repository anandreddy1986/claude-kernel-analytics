#!/usr/bin/env python3
"""
Generate Executive Presentation PDF
Converts markdown presentation to professional HTML slides and PDF
"""

import os
import re
import subprocess
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
PRESENTATIONS_DIR = PROJECT_ROOT / "data" / "presentations"
MARKDOWN_FILE = PRESENTATIONS_DIR / "Executive_Presentation_Agentic_AI_Project.md"
HTML_FILE = PRESENTATIONS_DIR / "Executive_Presentation_Agentic_AI_Project.html"
PDF_FILE = PRESENTATIONS_DIR / "Executive_Presentation_Agentic_AI_Project.pdf"

# Ensure presentations directory exists
PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)

def markdown_to_presentation_html(markdown_path, html_path):
    """Convert markdown to professional presentation HTML"""

    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by slide delimiter (---)
    slides = content.split('\n---\n')

    # HTML template with professional slide styling
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous AI Agent System - Executive Presentation</title>
    <style>
        @page {
            size: 11in 8.5in landscape;
            margin: 0;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        .slide {
            width: 11in;
            height: 8.5in;
            padding: 60px 80px;
            background: white;
            page-break-after: always;
            position: relative;
            border-bottom: 4px solid #0066cc;
        }

        .slide:last-child {
            page-break-after: avoid;
        }

        /* Title slide */
        .slide.title-slide {
            background: linear-gradient(135deg, #0066cc 0%, #004c99 100%);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            border-bottom: none;
        }

        .slide.title-slide h1 {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
            line-height: 1.2;
        }

        .slide.title-slide h2 {
            font-size: 32px;
            font-weight: 400;
            margin-bottom: 40px;
            opacity: 0.95;
        }

        .slide.title-slide p {
            font-size: 20px;
            margin-top: 60px;
            opacity: 0.9;
        }

        /* Regular slide headings */
        h2 {
            font-size: 36px;
            color: #0066cc;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #0066cc;
        }

        h3 {
            font-size: 28px;
            color: #004c99;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        h4 {
            font-size: 22px;
            color: #333;
            margin-top: 20px;
            margin-bottom: 12px;
            font-weight: 600;
        }

        p {
            font-size: 18px;
            margin-bottom: 15px;
            line-height: 1.7;
        }

        ul, ol {
            margin-left: 30px;
            margin-bottom: 20px;
        }

        li {
            font-size: 18px;
            margin-bottom: 10px;
            line-height: 1.6;
        }

        /* Code blocks */
        pre {
            background: #f8f8f8;
            border: 1px solid #ddd;
            border-left: 4px solid #0066cc;
            padding: 20px;
            margin: 20px 0;
            font-size: 14px;
            overflow-x: auto;
            border-radius: 4px;
        }

        code {
            font-family: 'Courier New', Consolas, monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 16px;
        }

        pre code {
            background: none;
            padding: 0;
        }

        /* Blockquotes */
        blockquote {
            border-left: 4px solid #0066cc;
            background: #f0f7ff;
            padding: 15px 20px;
            margin: 20px 0;
            font-style: italic;
            color: #004c99;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 16px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background: #0066cc;
            color: white;
            font-weight: 600;
        }

        tr:nth-child(even) {
            background: #f8f8f8;
        }

        /* Checkmarks and X marks */
        .slide ul li:before {
            content: '';
        }

        /* Slide footer */
        .slide-footer {
            position: absolute;
            bottom: 20px;
            right: 80px;
            font-size: 14px;
            color: #666;
        }

        /* Strong emphasis */
        strong {
            color: #0066cc;
            font-weight: 600;
        }

        /* Horizontal rules */
        hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }

        /* Special formatting for diagrams */
        .diagram {
            background: #f8f8f8;
            border: 2px solid #0066cc;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
            white-space: pre;
            overflow-x: auto;
        }
    </style>
</head>
<body>
"""

    html_content = html_template
    slide_number = 0

    for slide_content in slides:
        slide_number += 1

        # Determine if title slide
        is_title = slide_number == 1

        slide_class = "slide title-slide" if is_title else "slide"

        # Convert markdown to HTML (simple conversion)
        slide_html = slide_content

        # Headers
        slide_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', slide_html, flags=re.MULTILINE)

        # Bold and italic
        slide_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', slide_html)
        slide_html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', slide_html)

        # Code blocks
        slide_html = re.sub(r'```([^`]+)```', r'<pre class="diagram">\1</pre>', slide_html, flags=re.DOTALL)

        # Inline code
        slide_html = re.sub(r'`([^`]+)`', r'<code>\1</code>', slide_html)

        # Blockquotes
        slide_html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', slide_html, flags=re.MULTILINE)

        # Lists (simple approach)
        slide_html = re.sub(r'^- (.+)$', r'<li>\1</li>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^• (.+)$', r'<li>\1</li>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^✅ (.+)$', r'<li>✅ \1</li>', slide_html, flags=re.MULTILINE)
        slide_html = re.sub(r'^❌ (.+)$', r'<li>❌ \1</li>', slide_html, flags=re.MULTILINE)

        # Wrap consecutive <li> in <ul>
        slide_html = re.sub(r'(<li>.*?</li>\n)+', lambda m: '<ul>' + m.group(0) + '</ul>', slide_html, flags=re.DOTALL)

        # Paragraphs
        slide_html = re.sub(r'\n\n([^<\n][^\n]*)\n', r'\n<p>\1</p>\n', slide_html)

        # Build slide
        footer = f'<div class="slide-footer">Slide {slide_number}</div>' if not is_title else ''

        html_content += f'''
<div class="{slide_class}">
{slide_html}
{footer}
</div>
'''

    html_content += """
</body>
</html>
"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_path


def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF using Chrome headless"""

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    if not os.path.exists(chrome_path):
        print(f"ERROR: Chrome not found at {chrome_path}")
        return False

    try:
        result = subprocess.run([
            chrome_path,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            f"file://{html_path}"
        ], capture_output=True, text=True, timeout=30)

        if pdf_path.exists():
            return True
        else:
            print(f"ERROR: PDF generation failed")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("="*70)
    print("EXECUTIVE PRESENTATION GENERATOR")
    print("="*70)
    print()

    # Step 1: Convert markdown to HTML
    print("Step 1: Converting markdown to presentation HTML...")
    try:
        html_path = markdown_to_presentation_html(MARKDOWN_FILE, HTML_FILE)
        print(f"✓ HTML generated: {HTML_FILE}")
    except Exception as e:
        print(f"✗ HTML generation failed: {e}")
        return False

    # Step 2: Convert HTML to PDF
    print("\nStep 2: Converting HTML to PDF...")
    if html_to_pdf(HTML_FILE, PDF_FILE):
        size_mb = PDF_FILE.stat().st_size / 1024 / 1024
        print(f"✓ PDF generated: {PDF_FILE} ({size_mb:.1f} MB)")
    else:
        print("✗ PDF generation failed (but HTML is available)")
        return False

    print("\n" + "="*70)
    print("✓ PRESENTATION GENERATION COMPLETE")
    print("="*70)
    print(f"\nFiles created:")
    print(f"  HTML: {HTML_FILE}")
    print(f"  PDF:  {PDF_FILE}")
    print()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
