"""
Pintes
~~~~~~~~~~~~~~~~
*An amalgamation of horror.*
Pintes is a Python module designed to generate static HTML pages.
"""
# Variables
__author__ = "Formuna"

# TODO: Make this pretty :3

class CreatePint:
    """
    Creates a new pint for you to use.
    """
    def __init__(self):
        self.body = []
        self.head = []

    # Create functions
    def create(self, text: str = 'UNNAMED', className: str = '', tag: str = 'p'):
        """
        Creates a new customizable tag.
        `text` is the text inside the tag. Defaults to 'UNNAMED' if none specified.
        `className` is the class of the tag. Optional.
        `tag` is the tag type. Defaults to 'p' (paragraph) if none specified.
        """
        self.body.append(f'<{tag} class="{className}">{text}</{tag}>')
    def create_anchor(self, text: str = 'UNNAMED', href: str = '#', className: str = ''):
        """
        Creates an anchor tag.
        `text` is the text inside the anchor tag. Defaults to 'UNNAMED' if none specified.
        `href` is the href of the anchor tag. Defaults to '#' if none specified. (does nothing)
        `className` is the class of the anchor tag. Optional.
        """
        self.body.append(f'<a href="{href}" class="{className}">{text}</a>')
    def create_image(self, src: str, alt: str = 'Image', className: str = '', height: str = '100%', width:str='100%'):
        """
        Creates an image tag.
        `src` is the source of the image. Required.
        `alt` is the alt text of the image. Defaults to 'Image' but recommended to change.
        `className` is the class of the image tag. Optional.
        """
        self.body.append(f'<img src="{src}" alt="{alt}" class="{className}" style="width:{width}; height:{height};"/>')

    # Export functions
    def export_to_html(self):
        """
        Exports the body to an HTML string. Useful for debugging or PyWebview.
        """
        #return "".join(self.body)
        body = "".join(self.body)
        head = ''.join(self.head)
        html = f'<!DOCTYPE html><html><head>{head}</head><body>{body}</body></html>'
        return html

    def export_to_html_file(self, filename: str = 'index.html', printResult: bool = True):
        """
        Exports the body to an HTML file.
        `filename` is the filename of the exported HTML file. Defaults to 'index.html' if none specified.
        `printResult` controls whether the function will print the result of the export. Defaults to True.
        """
        html = self.export_to_html()
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html)
        if printResult:
            print(f'Exported to {filename} successfully.')

    # Pint merger
    def pint_merge(self, pint):
        """
        Merges two Pints together.
        `pint` is the Pint object to merge with.
        """
        if not isinstance(pint, CreatePint):
            raise TypeError("pint must be an instance of CreatePint")
        divhtml = f'<div>{"".join(pint.body)}</div>'
        self.body.append(divhtml)

    # Head functions
    def retitle_page(self, title: str = ''):
        """
        Retitles the page.
        `title` is the new title of the page. Defaults to ''.
        """
        self.head.append(f'<title>{title}</title>')
    def add_favicon(self, href: str = 'favicon.ico'):
        """
        Adds a favicon to the page.
        `href` is the href of the favicon. Defaults to 'favicon.ico'.
        """
        self.head.append(f'<link rel="icon" href="{href}">')
    def add_metadata(self, name: str = '', content: str = ''):
        """
        Adds metadata to the page. Useful for search engines such as Google.
        `name` is the name of the metadata. (e.g. 'author' or 'description')
        `content` is the content of the metadata. (e.g. 'Formuna' or 'A Pintes demo')
        """
        self.head.append(f'<meta name="{name}" content="{content}">')
    def add_css(self, css: str = ''):
        """
        Adds raw CSS data to the page.
        `css` is the string of CSS. Defaults to Nothing.
        """
        self.head.append(f'<style>{css}</style>')

if __name__ == '__main__':
    print('What are you doing? Run demo.py instead.')
