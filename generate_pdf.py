#!/usr/bin/env python3
"""
PDF Generator for LinkedIn Blog Posts
Converts markdown blog to professional PDF format.
"""

import markdown2
from pathlib import Path
from datetime import datetime


def markdown_to_pdf(markdown_file: str, output_pdf: str):
    """Convert markdown file to PDF."""

    # Read markdown
    with open(markdown_file, 'r') as f:
        md_content = f.read()

    # Fix the datetime placeholder
    md_content = md_content.replace(
        "{datetime.now().strftime('%B %d, %Y')}",
        datetime.now().strftime('%B %d, %Y')
    )

    # Convert markdown to HTML
    html_content = markdown2.markdown(
        md_content,
        extras=["tables", "fenced-code-blocks", "header-ids"]
    )

    # Create styled HTML
    styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Linux Storage Stack Trends - Spring 2026</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            font-size: 11pt;
        }}

        h1 {{
            color: #0077B5;
            border-bottom: 3px solid #0077B5;
            padding-bottom: 10px;
            margin-top: 20px;
            font-size: 24pt;
        }}

        h2 {{
            color: #0077B5;
            margin-top: 25px;
            font-size: 18pt;
            border-bottom: 2px solid #eee;
            padding-bottom: 5px;
        }}

        h3 {{
            color: #333;
            margin-top: 15px;
            font-size: 14pt;
        }}

        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}

        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-left: 4px solid #0077B5;
            overflow-x: auto;
            border-radius: 5px;
        }}

        blockquote {{
            border-left: 4px solid #0077B5;
            margin: 15px 0;
            padding-left: 15px;
            color: #666;
            font-style: italic;
        }}

        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 5px 0;
        }}

        a {{
            color: #0077B5;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 25px 0;
        }}

        strong {{
            color: #0077B5;
            font-weight: 600;
        }}

        em {{
            color: #666;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #0077B5 0%, #00A0DC 100%);
            color: white;
            border-radius: 8px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            font-size: 9pt;
            color: #666;
            text-align: center;
        }}

        .business-impact {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #28a745;
        }}

        .tech-detail {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="color: white; border: none; margin: 0;">Linux Storage Stack Trends</h1>
        <p style="margin: 5px 0;">Filesystems, I/O and Cloud Infrastructure</p>
        <p style="margin: 5px 0; font-size: 10pt;">Spring 2026 Upstream Analysis</p>
    </div>

    {html_content}

    <div class="footer">
        <p>git.kernel.org | lore.kernel.org</p>
    </div>
</body>
</html>
"""

    # Write HTML to temp file
    html_file = Path(output_pdf).with_suffix('.html')
    with open(html_file, 'w') as f:
        f.write(styled_html)

    print(f"✓ HTML generated: {html_file}")

    # Convert HTML to PDF using weasyprint
    try:
        from weasyprint import HTML
        HTML(html_file).write_pdf(output_pdf)
        print(f"✅ PDF generated: {output_pdf}")

        # Clean up HTML file
        html_file.unlink()

        return output_pdf
    except ImportError:
        print("⚠️  WeasyPrint not available, trying alternative method...")

        # Alternative: Use markdown2pdf or just keep HTML
        print(f"✓ HTML file saved: {html_file}")
        print(f"  You can open this in a browser and print to PDF")
        return str(html_file)


def main():
    """Generate PDF from LinkedIn blog."""
    markdown_file = "data/drafts/linkedin_kernel_update_apr_may_2026.md"
    output_pdf = "data/drafts/Linux_Kernel_Storage_Update_Apr_May_2026.pdf"

    if not Path(markdown_file).exists():
        # Try old filename for backwards compatibility
        markdown_file = "data/drafts/linkedin_kernel_update_may2025.md"
        output_pdf = "data/drafts/LinkedIn_Kernel_Storage_Update_May2025.pdf"

    if not Path(markdown_file).exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return

    print(f"Converting {markdown_file} to PDF...")
    result = markdown_to_pdf(markdown_file, output_pdf)

    print(f"\n{'='*60}")
    print(f"✅ CONVERSION COMPLETE")
    print(f"{'='*60}")
    print(f"Input:  {markdown_file}")
    print(f"Output: {result}")

    if result.endswith('.pdf'):
        # Get file size
        size_kb = Path(result).stat().st_size / 1024
        print(f"Size:   {size_kb:.1f} KB")
        print(f"\n📄 PDF ready for LinkedIn sharing!")


if __name__ == "__main__":
    main()
