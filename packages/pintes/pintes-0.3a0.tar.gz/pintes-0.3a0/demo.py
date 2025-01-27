import pintes

# Create a new Pint object
root = pintes.CreatePint()

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

# Now, to export the code you've made to an HTML file.
root.export_to_html_file('rework.html')
# This will overwrite the file if it already exists.
# You can also use `export_to_html()` to export to a string instead of a file,
# which is useful for debugging or PyWebview.
#export = root.export_to_html()
#print(export)
