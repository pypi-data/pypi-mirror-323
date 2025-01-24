import regex as re
from typing import List, Tuple


class Normalizer:
    _diacritics_filters = [
        (r"[ًٌٍَُِّْٰٖٕٓٔؕٙٴ̒́]", ""),
    ]

    _punctuation_filters = [
        (r"[^\w\s\d]", ""),
    ]

    _emoji_filters = [
        (r"[😀-😯]", ""),
        (r"[🌐-🖿]", ""),
        (r"[🚀-🛿]", ""),
        (r"[🇠-🇿]", ""),
        (r"[㠠-𯿿]", ""),
        (r"[⏰]", ""),
        (r"[♀-♂]", ""),
        (r"[☀-🔿]", ""),
        (r"[‍]", ""),
        (r"[⏏]", ""),
        (r"[⏩]", ""),
        (r"[⌚]", ""),
        (r"[️]", ""),
        (r"[💯]", ""),
        (r"[〰]", ""),
        (r"[⏱]", ""),
        (r"[⏪]", ""),
    ]

    _character_mappings = [
        (r"[ـ]", ""),
        (r"[ﺁﺂ]", "آ"),
        (r"[ٲٵﭐﭑٳﺇﺈإأٱ]", "ا"),
        (r"[ٮٻڀݐݒݔݕݖﭒﭕﺏﺒ]", "ب"),
        (r"[ﭖﭗﭘﭙﭚﭛﭜﭝ]", "پ"),
        (r"[ٹٺټٿݓﭞﭟﭠﭡﭦﭨﺕﺘ]", "ت"),
        (r"[ٽݑﺙﺚﺛﺜﭢﭤ]", "ث"),
        (r"[ڃڄﭲﭴﭵﭷﺝﺟﺠ]", "ج"),
        (r"[ڇڿﭺݘﭼﮀﮁݯ]", "چ"),
        (r"[ځڂڅݗݮﺡﺤ]", "ح"),
        (r"[ﺥﺦﺧ]", "خ"),
        (r"[ڈډڊڋڍۮݙݚﮂﮈﺩ]", "د"),
        (r"[ڌﱛﺫﺬڎڏڐﮅﮇ]", "ذ"),
        (r"[ڑڒړڔڕږۯݛﮌﺭ]", "ر"),
        (r"[ڗݫﺯﺰ]", "ز"),
        (r"[ڙﮊﮋ]", "ژ"),
        (r"[ښڛﺱﺴ]", "س"),
        (r"[ڜۺﺵﺸݜݭ]", "ش"),
        (r"[ڝڞﺹﺼ]", "ص"),
        (r"[ۻﺽﻀ]", "ض"),
        (r"[ﻁﻃﻄ]", "ط"),
        (r"[ﻅﻆﻈڟ]", "ظ"),
        (r"[ڠݝݞݟﻉﻊﻋ]", "ع"),
        (r"[ۼﻍﻎﻐ]", "غ"),
        (r"[ڡڢڣڤڥڦݠݡﭪﭫﭬﻑﻒﻓ]", "ف"),
        (r"[ٯڧڨﻕﻗ]", "ق"),
        (r"[كػؼڪګڬڭڮݢݣﮎﮐﯓﻙﻛ]", "ک"),
        (r"[ڰڱڲڳڴﮒﮔﮖ]", "گ"),
        (r"[ڵڶڷڸݪﻝﻠ]", "ل"),
        (r"[۾ݥݦﻡﻢﻣ]", "م"),
        (r"[ڹںڻڼڽݧݨݩﮞﻥﻧ]", "ن"),
        (r"[ٶٷﯗﯘﯙﯚﯜﯝﯞﯟﺅۄۅۉۊۋۏﯠﻭؤפ]", "و"),
        (r"[ھۿۀہۂۃەﮤﮦﮧﮨﮩﻩﻫة]", "ه"),
        (
            r"[ؠؽؾؿىيٸۍێېۑےۓﮮﮯﮰﮱﯤﯥﯦﯧﯼﯽﯾﯿﻯﻱﻳﯨﯩﯫﯭﯰﯳﯵﯷﯹﯻﱝ]",
            "ی",
        ),
    ]

    _number_mappings = [
        (r"[0٠𝟢𝟬]", "۰"),
        (r"[1١𝟣𝟭⑴⒈⓵①❶𝟙𝟷ı]", "۱"),
        (r"[2٢𝟤𝟮⑵⒉⓶②❷²𝟐𝟸𝟚ᒿշ]", "۲"),
        (r"[3٣𝟥𝟯⑶⒊⓷③❸³ვ]", "۳"),
        (r"[4٤𝟦𝟰⑷⒋⓸④❹⁴]", "۴"),
        (r"[5٥𝟧𝟱⑸⒌⓹⑤❺⁵]", "۵"),
        (r"[6٦𝟨𝟲⑹⒍⓺⑥❻⁶]", "۶"),
        (r"[7٧𝟩𝟳⑺⒎⓻⑦❼⁷]", "۷"),
        (r"[8٨𝟪𝟴⑻⒏⓼⑧❽⁸۸]", "۸"),
        (r"[9٩𝟫𝟵⑼⒐⓽⑨❾⁹]", "۹"),
        (r"[⑽⒑⓾⑩]", "۱۰"),
        (r"[⑾⒒⑪]", "۱۱"),
        (r"[⑿⒓⑫]", "۱۲"),
        (r"[⒀⒔⑬]", "۱۳"),
        (r"[⒁⒕⑭]", "۱۴"),
        (r"[⒂⒖⑮]", "۱۵"),
        (r"[⒃⒗⑯]", "۱۶"),
        (r"[⒄⒘⑰]", "۱۷"),
        (r"[⒅⒙⑱]", "۱۸"),
        (r"[⒆⒚⑲]", "۱۹"),
        (r"[⒇⒛⑳]", "۲۰"),
    ]

    _punctuation_mappings = [
        (r"[▕❘❙❚▏│]", "|"),
        (r"[ㅡ一—–ー̶ـ]", "-"),
        (r"[▁_̲]", "_"),
        (r"[❔?�؟ʕʔ🏻\x08\x97\x9d]", "؟"),
        (r"[❕！]", "!"),
        (r"[⁉]", "!؟"),
        (r"[‼]", "!!"),
        (r"[℅%]", "٪"),
        (r"[÷]", "/"),
        (r"[×]", "*"),
        (r"[：]", ":"),
        (r"[›]", ">"),
        (r"[‹＜]", "<"),
        (r"[《]", "«"),
        (r"[》]", "»"),
        (r"[•]", "."),
        (r"[٬,]", "،"),
        (r"[;；]", "؛"),
    ]

    _space_mappings = [
        (r" {2,}", " "),  # remove extra spaces
        (r"\n{3,}", "\n\n"),  # remove extra newlines
        (r"\u200c{2,}", "\u200c"),  # remove extra ZWNJs
        (r"\u200c{1,} ", " "),  # remove unneded ZWNJs before space
        (r" \u200c{1,}", " "),  # remove unneded ZWNJs after space
        (r"\b\u200c*\B", ""),  # remove unneded ZWNJs at the beginning of words
        (r"\B\u200c*\b", ""),  # remove unneded ZWNJs at the end of words
        (r"[\u200b\u200d\u200e\u200f\u2066\u2067\u202a\u202b\u202d]", ""),
    ]

    _unicode_mappings = [
        ("﷽", "بسم الله الرحمن الرحیم"),
        ("﷼", "ریال"),
        ("(ﷰ|ﷹ)", "صلی"),
        ("ﷲ", "الله"),
        ("ﷳ", "اکبر"),
        ("ﷴ", "محمد"),
        ("ﷵ", "صلعم"),
        ("ﷶ", "رسول"),
        ("ﷷ", "علیه"),
        ("ﷸ", "وسلم"),
        ("ﻵ|ﻶ|ﻷ|ﻸ|ﻹ|ﻺ|ﻻ|ﻼ", "لا"),
    ]

    def __init__(
        self,
        unifiy_characters: bool = True,
        unify_numbers: bool = True,
        unify_punctuations: bool = True,
        unify_arabic_unicode: bool = True,
        space_correction: bool = True,
        remove_emojis: bool = True,
        remove_diactrics: bool = True,
        remove_punctuations: bool = False,
        filters: List[Tuple[str, str]] = [],
    ):
        self._unify_numbers = unify_numbers
        self._unify_punctuations = unify_punctuations
        self._unify_arabic_unicode = unify_arabic_unicode
        self._remove_emojis = remove_emojis
        self._remove_diactrics = remove_diactrics
        self._remove_punctuations = remove_punctuations

        self._filters_mappings = []

        if unifiy_characters:
            self._filters_mappings.extend(self._character_mappings)
        if remove_punctuations:
            self._filters_mappings.extend(self._punctuation_filters)
        if remove_emojis:
            self._filters_mappings.extend(self._emoji_filters)
        if remove_diactrics:
            self._filters_mappings.extend(self._diacritics_filters)
        if unify_punctuations and not remove_punctuations:
            self._filters_mappings.extend(self._punctuation_mappings)
        if unify_numbers:
            self._filters_mappings.extend(self._number_mappings)
        if unify_arabic_unicode:
            self._filters_mappings.extend(self._unicode_mappings)
        if space_correction:
            self._filters_mappings.extend(self._space_mappings)
        if filters:
            self._filters_mappings.extend(filters)

    def normalize(self, text):
        for pattern, replacement in self._filters_mappings:
            text = re.sub(pattern, replacement, text)
        text = self.correct_spacings(text)
        text = text.strip()
        return text

    @classmethod
    def unify_numbers(cls, text):
        for pattern, replacement in cls._number_mappings:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def unify_punctuations(cls, text):
        for pattern, replacement in cls._punctuation_mappings:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def unify_characters(cls, text):
        for pattern, replacement in cls._character_mappings:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def unify_arabic_unicode(cls, text):
        for pattern, replacement in cls._unicode_mappings:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def remove_emojis(cls, text):
        for pattern, replacement in cls._emoji_filters:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def remove_diactrics(cls, text):
        for pattern, replacement in cls._diacritics_filters:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def remove_punctuations(cls, text):
        for pattern, replacement in cls._punctuation_filters:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def remove_diacritics(cls, text):
        for pattern, replacement in cls._diacritics_filters:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def remove_extra_spaces(cls, text):
        for pattern, replacement in cls._space_mappings:
            text = re.sub(pattern, replacement, text)
        return text

    @classmethod
    def correct_spacings(cls, sentence):
        # copied from ParsiNorm with
        # This Function is a mixture of HAZM and ParsiVar Features

        sentence = re.sub(r"^(بی|می|نمی)( )", r"\1‌", sentence)  # verb_prefix
        sentence = re.sub(r"( )(می|نمی)( )", r"\1\2‌ ", sentence)  # verb_prefix
        sentence = re.sub(r"([^ ]ه) ی ", r"\1‌ی ", sentence)

        # Issue: "واجد شرایط بودند" -> "واجد شرایط‌بودند"
        # sentence = re.sub(
        #     r"( )(هایی|ها|های|ایی|هایم|هایت|هایش|هایمان|هایتان|هایشان|ات|ان|ین"
        #     r"|انی|بان|ام|ای|یم|ید|اید|اند|بودم|بودی|بود|بودیم|بودید|بودند|ست|تر|تری|ترین|گری|گر)( )",
        #     r"‌\2\3",
        #     sentence,
        # )

        # Issue: some suffixes may introduce incorrect spacing!
        # A more complex solution is needed to fix this issue.
        # Example: "با کی‌داری حرف می‌زنی؟" <- "با کی داری حرف می‌زنی؟"
        # Example: "به نکته ریزی اشاره کردی!" -> "به نکته‌ریزی اشاره کردی!"

        # complex_word_suffix_pattern = (
        #     r"( )(طلبان|طلب|گرایی|گرایان|شناس|شناسی|گذاری|گذار|گذاران|شناسان|گیری|پذیری|بندی|آوری|سازی|"
        #     r"بندی|کننده|کنندگان|گیری|پرداز|پردازی|پردازان|آمیز|سنجی|ریزی|داری|دهنده|آمیز|پذیری"
        #     r"|پذیر|پذیران|گر|ریز|ریزی|رسانی|یاب|یابی|گانه|گانه‌ای|انگاری|گا|بند|رسانی|دهندگان|دار)( )"
        # )
        # sentence = re.sub(complex_word_suffix_pattern, r"‌\2\3", sentence)
        sentence = re.sub(r' "([^\n"]+)" ', r'"\1"', sentence)

        punc_after = r".\.:!،؛؟»\]\)\}"
        punc_before = r"«\[\(\{"

        sentence = re.sub(
            r" ([" + punc_after + "])|([" + punc_before + "]) ", r"\1\2", sentence
        )
        sentence = re.sub(
            r"([.،:؟!])([^ {} \d۰۱۲۳۴۵۶۷۸۹])".format(punc_after), r"\1 \2", sentence
        )
        sentence = re.sub(
            r"([^ " + punc_before + "])([" + punc_before + "])", r"\1 \2", sentence
        )

        sentence = cls.remove_extra_spaces(sentence)
        return sentence
