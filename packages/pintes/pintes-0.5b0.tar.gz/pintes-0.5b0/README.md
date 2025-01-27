# Pintes
*An amalgamation of horror.*

Pintes is a tool made in Python that allows users to develop static HTML pages with ease.

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/FormunaGit/Pintes/python-publish.yml?style=flat&logo=githubactions&logoColor=white) ![GitHub License](https://img.shields.io/github/license/FormunaGit/Pintes?logo=gnu) ![GitHub last commit](https://img.shields.io/github/last-commit/formunagit/pintes)

## Why?
- For the actual tool, I have no idea. I had an idea and I worked on it.
- For the name, I also have no idea.

## How?
Pintes internally uses a list that the tag create functions append to. This list is then joined and written to a file after the necessary tags are added.

## Usage
~~As of 0.1:PRERELEASE, Pintes is not on PyPI. And since I don't understand how to use setup.py, you'll have to clone the repository and use the `pintes.py` file as a module.~~

As of 0.2.alpha.1 (0.2a1), Pintes is now on PyPI. You can install it using `pip install pintes` and use it as a module.

Check out the demo folder for a demo on how to use Pintes.

## What's available?
- [x] Most HTML tags
- [x] Divs support
- [x] Classes support
- [x] CSS support
- [x] Image support
- [x] Anchor/`a` tag support
- [x] JS support
- [x] Custom divs support (e.g. `ul` and `ol`)
- [x] Self-closing tags support (e.g. `br`)

Am I missing something? [Help Pintes and make an issue!](https://github.com/FormunaGit/Pintes/issues)

## License
The license for Pintes is the GNU General Public License v3.0. You can view the license here in the LICENSE file or [here](https://www.gnu.org/licenses/gpl-3.0.html).

Because of the license, Pintes is free to use, modify, and distribute. However, you must provide the source code and the license with the distribution if you modify it.
## Contributing
If you want to contribute to Pintes, you can fork the repository and make a pull request. I'll review it and merge it if it's good.
