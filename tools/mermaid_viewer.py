import os
import re
import webbrowser

def extract_mermaid_diagrams(md_file):
    """Extract Mermaid diagrams from markdown file."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all Mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    diagrams = re.findall(pattern, content, re.DOTALL)
    return diagrams

def create_html_viewer(diagrams, output_file):
    """Create an HTML file with Mermaid diagrams."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mermaid Diagrams Viewer</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
            });
        </script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .diagram { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Mermaid Diagrams Viewer</h1>
    """
    
    for i, diagram in enumerate(diagrams, 1):
        html_content += f"""
        <div class="diagram">
            <h3>Diagram {i}</h3>
            <div class="mermaid">
                {diagram}
            </div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    # Create docs/diagrams directory if it doesn't exist
    os.makedirs('docs/diagrams', exist_ok=True)
    
    # Process all markdown files in docs directory
    md_files = [f for f in os.listdir('docs') if f.endswith('.md')]
    all_diagrams = []
    
    for md_file in md_files:
        diagrams = extract_mermaid_diagrams(os.path.join('docs', md_file))
        if diagrams:
            print(f"Found {len(diagrams)} diagrams in {md_file}")
            all_diagrams.extend(diagrams)
    
    if all_diagrams:
        output_file = 'docs/diagrams/mermaid_viewer.html'
        create_html_viewer(all_diagrams, output_file)
        print(f"\nCreated HTML viewer with {len(all_diagrams)} diagrams")
        print(f"Opening {output_file} in your default browser...")
        webbrowser.open('file://' + os.path.abspath(output_file))
    else:
        print("No Mermaid diagrams found in the documentation files.")

if __name__ == '__main__':
    main() 