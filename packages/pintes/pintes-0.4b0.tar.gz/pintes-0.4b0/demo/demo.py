import pintes

# Create a new Pint object
root = pintes.CreatePint()

# Give the page a title (this shows up in the tab)
root.retitle_page('Pintes Demo')

# ...and give it an icon. (called a favicon)
root.add_favicon('favicon.ico')

# Let's add some metadata to the page. This is useful for search engines.
root.add_metadata('author', 'Formuna') # This is equivalent to <meta name="author" content="Formuna">
root.add_metadata('description', 'A Pintes demo') # This is equivalent to <meta name="description" content="A Pintes demo">

# Create a h1 tag
root.create('Hello, World!', tag='h1')

# Not specifying the `tag` parameter will default to a paragraph tag.
root.create('This is a paragraph tag')

# Creating an anchor tag can't be done with the `create()` function for now. Instead, use `create_anchor()`.
root.create_anchor('Click me!', 'https://example.com')

# Creating a div is fairly easy, since it's just creating another Pint.
divRoot = pintes.CreatePint()

# Adding a paragraph inside the div is the same as adding a paragraph to the root,
# except you use the divRoot instead of the root.
divRoot.create('This is in a div tag!', tag='h2')
divRoot.create('This is also inside a div tag!')

# If you export now, the div will not be show up since it is a different Pint.
# In order to merge them, you need to use `merge_pints()` function.
root.pint_merge(divRoot)
# ^ This will merge the divRoot into the root Pint.
# It is recommended to write this right before exporting.

# Before we export, let's add some CSS to the page.
# If you have a CSS file, use Python's built-in file reading functions to pipe the file contents to `add_css()`.
css_file_contents = open('demo.css', 'r').read()
root.add_css(css_file_contents)

# Let's also create a p tag with a class, and some CSS to go with it.
# Remember that not specifying the `tag` parameter will default to a paragraph tag.
root.create('This is a stylized paragraph with a class.', className='demo-class')
root.create('This is a centered paragraph with a class.', className='centered')

# Let's add an image to the page.
# It's recommended to write a small description in the `alt` parameter incase the image doesn't load or a screen reader is used.
# The `width` and `height` parameters internally lead to the `style` attribute of the image tag, so you can use any CSS units such as px, em, %, etc.
# Or you could just use CSS and give the image a class. Here we use the `width` and `height` parameters to make the image smaller.
root.create_image('./image-demo.png', alt='Image Demo', width='25%', height='25%')

# Now, to export the code you've made to an HTML file.
root.export_to_html_file('demo.html')
# This will overwrite the file if it already exists.
# You can also use `export_to_html()` to export to a string instead of a file,
# which is useful for debugging or PyWebview.
#export = root.export_to_html()
#print(export)
