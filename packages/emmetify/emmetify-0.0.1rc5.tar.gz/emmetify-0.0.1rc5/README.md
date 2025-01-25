# Emmetify 🚀

[![pypi](https://img.shields.io/pypi/v/emmetify.svg)](https://pypi.python.org/pypi/emmetify)
[![versions](https://img.shields.io/pypi/pyversions/emmetify.svg)](https://github.com/emmetify/emmetify-py)
[![PyPI Downloads](https://static.pepy.tech/badge/emmetify)](https://pepy.tech/projects/emmetify)
[![codecov](https://codecov.io/gh/emmetify/emmetify-py/graph/badge.svg?token=GY70C7TMD8)](https://codecov.io/gh/emmetify/emmetify-py)
[![license](https://img.shields.io/github/license/emmetify/emmetify-py.svg)](https://github.com/emmetify/emmetify-py/blob/main/LICENSE)

Cut your LLM processing costs by up to 90% by transforming verbose HTML into efficient Emmet notation, without losing structural integrity.

## Why Emmetify? 🤔

- 💰 **Drastically Reduce Costs** - Process HTML with your LLM agents at a fraction of the cost by using our efficient Emmet-based compression
- 🎯 **Maintain Performance** - Your LLM agents can still generate XPath and CSS selectors with the same accuracy using the compressed format
- 🔌 **Seamless Integration** - Emmet syntax is well-understood by all major LLMs thanks to its 10+ years of widespread use in frontend development
- ⚡ **Fast Processing** - Less tokens means faster processing times for your HTML analysis tasks

## How It Works 🛠️

Emmetify converts complex HTML structures into concise Emmet notation. For example:

```html
<div class="container">
    <header class="header">
        <nav class="nav">
            <ul class="nav-list">
                <li class="nav-item"><a href="#">Link</a></li>
            </ul>
        </nav>
    </header>
</div>
```
Becomes:
```
div.container>header.header>nav.nav>ul.nav-list>li.nav-item>a[href=#]{Link}
```

Using the [OpenAI Tokenizer](https://platform.openai.com/tokenizer), we can see this simple transformation reduces token count from:
- HTML: 59 tokens
- Emmet: 22 tokens

That's 63% fewer tokens while preserving all structural information! And this is just with default settings.

You can achieve even higher compression rates (up to 90%, or even more depending on the HTML structure) by using advanced configuration options:
- Removing unnecessary tags
- Simplifying attributes
- Optimizing class names
- Shortening URLs

Check our documentation for detailed optimization strategies and their impact on token reduction.

## The Technology Behind It 🔍

Emmetify leverages [Emmet](https://emmet.io) notation - a powerful and mature syntax that's been a standard in web development for over a decade. While developers typically use Emmet to expand short abbreviations into HTML:

```
div.container>h1{Title}+p{Content}
```
↓ Expands to ↓
```html
<div class="container">
    <h1>Title</h1>
    <p>Content</p>
</div>
```

Emmetify uses this well-established syntax in reverse, converting verbose HTML back into this concise format that LLMs can understand just as well as raw HTML.

## Installation 🔧

```bash
pip install emmetify
```

## Usage 💻

### Basic Usage

```python
from emmetify import Emmetifier
import requests

emmetifier = Emmetifier()
html = requests.get("https://example.com").text
emmet = emmetifier.emmetify(html)
print(emmet)
```

### Advanced HTML Simplification ⚡

Transform verbose HTML into its most essential form while preserving navigational structure. This mode intelligently:
- Skips non-essential HTML tags
- Prioritizes important attributes
- Removes redundant information

For example, this verbose HTML:

```html
<link rel="stylesheet" href="style.css">
<div id="main" class="container" style="color: red;" data-test="ignore">Example</div>
```

Becomes this concise Emmet notation:

```
div#main.container{Example}
```

Much shorter, yet retains all necessary information for LLM navigation and processing!

#### Advanced Usage:

```python
from emmetify import Emmetifier
import requests
import openai

# Configure HTML simplification
emmetifier = Emmetifier(config={
    "html": {
        "skip_tags": True,
        "prioritize_attributes": True
    }
})

# Fetch and process HTML
html = requests.get("https://example.com").text
result = emmetifier.emmetify(html).result
print(result)

# Use with your favorite LLM
llm = openai.OpenAI()
prompt = f"Get list of xpath selectors for all the links on the following page: {result}"
response = llm.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": emmet}],
)
```

## Backlog 📝

- [x] Add support for HTML
- [ ] Add examples

## Supported Formats 📊

- ✅ HTML
- 🚧 XML (Coming Soon)
- 🚧 JSON (Coming Soon)
