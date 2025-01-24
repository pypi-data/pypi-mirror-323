
![Banner](https://amirivojdan.io/wp-content/uploads/2025/01/shekar-lib.png)

<p align="center">
    <em>Simplifying Persian NLP for Everyone</em>
</p>

<p align="center">
 <a href="https://img.shields.io/github/actions/workflow/status/amirivojdan/shekar/test.yml" target="_blank">
 <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/amirivojdan/shekar/test.yml?color=00A693">
</a>
<a href="https://pypi.org/project/shekar" target="_blank">
    <img src="https://img.shields.io/pypi/v/shekar?color=00A693" alt="Package version">
</a>

<a href="https://pypi.org/project/shekar" target="_blank">
    <img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Famirivojdan%2Fshekar%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&color=00A693" alt="Supported Python versions">
</a>
</p>

## Introduction

Shekar (meaning 'sugar' in Persian) is a Python library for Persian natural language processing, named after the influential satirical story *"فارسی شکر است"* (Persian is Sugar) published in 1921 by Mohammad Ali Jamalzadeh.
The story became a cornerstone of Iran's literary renaissance, advocating for accessible yet eloquent expression.

Inspired by the story’s role in making Persian literature more relatable and expressive, Shekar aspires to democratize Persian natural language processing by offering a user-friendly yet powerful toolkit that captures the richness and elegance of the Persian language. Just as Jamalzadeh’s story bridged tradition and modernity, Shekar bridges the gap between technical complexity and linguistic accessibility, empowering developers and researchers to explore and innovate in Persian NLP with ease.

## Installation

To install the package, you can use `pip`. Run the following command:

```bash
pip install shekar
```

## Usage

### Normalization

```python

from shekar.normalizers import Normalizer
normalizer = Normalizer()

text = "ۿدف ما ػمګ بۀ ێڪډيڱڕ أښټ"
text = normalizer.normalize(text) # Output: هدف ما کمک به یکدیگر است
print(text)
```
```output
هدف ما کمک به یکدیگر است
```

### Sentence Tokenization

Here is a simple example of how to use the `shekar` package:

```python

from shekar.tokenizers import SentenceTokenizer

text = "هدف ما کمک به یکدیگر است! ما می‌توانیم با هم کار کنیم."
tokenizer = SentenceTokenizer()
sentences = tokenizer.tokenize(text)

for sentence in sentences:
    print(sentence)
```

```output
هدف ما کمک به یکدیگر است!
ما می‌توانیم با هم کار کنیم.
```