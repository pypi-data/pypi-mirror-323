# Normalization

Normalization is the process of transforming text into a standard format. This involves converting Arabic characters and numbers to Persian equivalents, replacing spaces with ZERO WIDTH NON-JOINER (Half-Space) if needed, and handling special characters. Normalization is an essential step in natural language processing (NLP) as it helps in reducing the complexity of the text and improving the performance of machine learning processing models, search engines, and text analysis tools.

## Normalizer

The `Normalizer` is a tool used to standardize a given text. This is particularly useful in natural language processing tasks where consistency and uniformity of the text are important. The `Normalizer` can handle various text transformations including number standardization, character unification, punctuation normalization, emoji removal, diacritic removal, and spacing corrections.

### Installation

```python
from shekar.normalizers import Normalizer
```

### Configuration Options

When initializing the Normalizer, you can customize its behavior with these parameters:

```python
normalizer = Normalizer(
    space_correction=True,      # Enable/disable space and half-space corrections
    unify_numbers=True,         # Convert different number formats to Persian
    unify_punctuations=True,    # Standardize punctuation marks
    unify_arabic_unicode=True,  # Convert special Arabic Unicode characters
    remove_emojis=True,         # Remove emoji characters
    remove_diactrics=True,      # Remove diacritical marks
    remove_punctuations=False,  # Remove all punctuation marks
)
```

### Methods

#### 1. normalize()
The main method that combines all enabled normalizations:

```python

from shekar.normalizers import Normalizer
normalizer = Normalizer()

text = "ۿدف ما ػمګ بۀ ێڪډيڱڕ أښټ"
normalizer.normalize(text) # Output: هدف ما کمک به یکدیگر است

# Character unification
text = "نشان‌دهندة سایة"
normalizer.normalize(text)  # Output: نشان‌دهنده سایه

# Number unification and space correction
text = "سال 20203 ! درس ؟"
normalizer.normalize(text)  # Output: سال ۲۰۲۳! درس؟

# Emoji removal and space correction
text = "سلام 😊   دوست    من"
normalizer.normalize(text)  # Output: سلام دوست من
```


#### 2. unify_numbers()
Convert different number formats to Persian numerals:

```python
# Converting Arabic/English numbers to Persian
text = "٠١٢٣٤٥٦٧٨٩ 123456789"
normalizer.unify_numbers(text)  # Output: ۰۱۲۳۴۵۶۷۸۹ ۱۲۳۴۵۶۷۸۹

# Converting circled numbers and other variants
text = "① ② ③ ④"
normalizer.unify_numbers(text)  # Output: ۱ ۲ ۳ ۴
```

#### 3. unify_punctuations()
Standardize various punctuation marks:

```python
# Converting different question marks and exclamation points
text = "❔❕⁉ : ；"
normalizer.unify_punctuations(text)  # Output: ؟!!؟ : ؛

# Converting different separators
text = "این٬ آن"
normalizer.unify_punctuations(text)  # Output: این، آن
```

#### 4. unify_characters()
Standardize various Persian/Arabic character forms:

```python
# Converting final forms
text = "ۿدف ما ػمګ بۀ ێڪډيڱڕ أښټ"
normalizer.unify_characters(text)  # Output: هدف ما کمک به یکدیگر است
```

#### 5. unify_arabic_unicode()
Convert special Arabic Unicode characters:

```python
# Converting special symbols to words
text = "﷽"
normalizer.unify_arabic_unicode(text)  # Output: بسم الله الرحمن الرحیم

text = "پنجاه هزار ﷼"
normalizer.unify_arabic_unicode(text)  # Output: پنجاه هزار ریال
```

#### 6. remove_emojis()
Remove emoji characters from text:

```python
text = "😀 سلام 🌐 دوست 🚀 من"
normalizer.remove_emojis(text)  # Output: سلام دوست من

text = "به ایران خوش آمدید! 🇮🇷"
normalizer.remove_emojis(text)  # Output: به ایران خوش آمدید!
```

#### 7. remove_diacritics()
Remove diacritical marks from text:

```python
text = "کُجا نِشانِ قَدَم ناتَمام خواهَد ماند؟"
normalizer.remove_diacritics(text)  # Output: کجا نشان قدم ناتمام خواهد ماند؟
```

#### 8. remove_punctuations()
Remove all punctuation marks:

```python
text = "سلام! چطوری؟ خوبم،"
normalizer.remove_punctuations(text)  # Output: سلام چطوری خوبم
```

#### 9. space_correction()
Fix spacing issues and apply half-space rules:

```python
# Fix extra spaces
text = "این    یک     متن    است"
normalizer.space_correction(text)  # Output: این یک متن است

# Fix spacing around punctuation
text = "سلام !چطوری ؟خوبم ."
normalizer.space_correction(text)  # Output: سلام! چطوری؟ خوبم.
```

## Best Practices

1. Initialize a single instance of `Normalizer` for better performance
2. Configure the normalizer options based on your specific needs during initialization
3. Use the `normalize()` method for general text normalization
4. For specific normalizations, use individual methods
5. Consider the context when choosing normalization options
6. Be aware that some normalizations might change the meaning of text in certain contexts

## Common Issues and Solutions

1. If text appears broken after normalization, check if the input encoding is correct
2. If specific characters aren't being normalized as expected, verify that the corresponding normalization option is enabled
3. When working with mixed Persian/Arabic text, be cautious with character unification
4. For better performance with large texts, process them in chunks
