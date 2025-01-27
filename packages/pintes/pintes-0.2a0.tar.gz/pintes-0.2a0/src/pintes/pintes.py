"""
Pintes
~~~~~~~~~~~~~~~~
*An amalgamation of horror.*
Pintes is a Python module designed to generate static HTML pages.
"""
# Variables
__author__ = "Formuna"
__version__ = "0.2.alpha"

# TODO: Make this pretty :3

def version():
    """
    Returns the version of Pintes.
    """
    return __version__

class CreatePint:
    """
    Creates a new pint for you to use.
    """
    body = []

    # Create functions
    def create(self, text: str = 'UNNAMED', className: str = '', tag: str = 'p'):
        """
        Creates a new customizable tag.
        `text` is the text inside the tag. Defaults to 'UNNAMED' if none specified.
        `className` is the class of the tag. Optional.
        `tag` is the tag type. Defaults to 'p' (paragraph) if none specified.
        """
        self.body.append(f'<{tag} class={className}>{text}</{tag}>')
    def create_anchor(self, text: str = 'UNNAMED', href: str = '#', className: str = ''):
        """
        Creates an anchor tag.
        `text` is the text inside the anchor tag. Defaults to 'UNNAMED' if none specified.
        `href` is the href of the anchor tag. Defaults to '#' if none specified. (does nothing)
        `className` is the class of the anchor tag. Optional.
        """
        self.body.append(f'<a href={href} class={className}>{text}</a>')

    # Export functions
    def export_to_html(self):
        """
        Exports the body to an HTML string. Useful for debugging or PyWebview.
        """
        return "".join(self.body)

    def export_to_html_file(self, filename: str = 'index.html', printResult: bool = True):
        """
        Exports the body to an HTML file.
        `filename` is the filename of the exported HTML file. Defaults to 'index.html' if none specified.
        `printResult` controls whether the function will print the result of the export. Defaults to True.
        """
        html = ''.join(self.body)
        with open(filename, 'w') as file:
            file.write(html)
        if printResult:
            print(f'Exported to {filename} successfully.')

    # Pint merger
    def pint_merge(self, pint):
        """
        Merges two Pints together.
        `pint` is the Pint object to merge with.
        """
        html = ''.join(pint.body)
        self.body.append(html)

if __name__ == '__main__':
    print('What are you doing? Run demo.py instead.')
