import re
from typing import List


class SentenceTokenizer:
    """
    A class used to tokenize text into sentences based on punctuation marks.
    Attributes:
        pattern (Pattern): A compiled regular expression pattern used to identify sentence-ending punctuation.
    Methods:
        tokenize(text: str) -> List[str]: Tokenizes the input text into a list of sentences.
    Example:
        >>> tokenizer = SentenceTokenizer()
        >>> text = "چه سیب‌های قشنگی! حیات نشئه تنهایی است."
        >>> tokenizer.tokenize(text)
        ['.چه سیب‌های قشنگی!', 'حیات نشئه تنهایی است']
    """

    def __init__(self) -> None:
        self.pattern = re.compile(r"([!.?⸮؟]+)", re.UNICODE)

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes the input text into a list of sentences.

        Args:
            text (str): The input text to be tokenized.

        Returns:
            List[str]: A list of tokenized sentences.
        """
        text = re.sub(r"\s+", " ", text)
        tokens = self.pattern.split(text)
        sentences = [
            tokens[i].strip() + tokens[i + 1].strip()
            for i in range(0, len(tokens) - 1, 2)
        ]
        if len(tokens) % 2 == 1 and tokens[-1].strip():
            sentences.append(tokens[-1].strip())
        return sentences


class WordTokenizer:
    pattern = re.compile(r"\b\w+\b|\u200c\w+|\w+\u200c|[^ \w]", re.UNICODE)

    def __init__(self):
        pass

    @classmethod
    def tokenize(cls, text):
        return cls.pattern.findall(text)
