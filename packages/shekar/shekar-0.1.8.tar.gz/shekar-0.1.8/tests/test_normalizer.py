import pytest
from shekar.normalizer import Normalizer


@pytest.fixture
def normalizer():
    return Normalizer()


def test_normalize_numbers(normalizer):
    input_text = "٠١٢٣٤٥٦٧٨٩ ⒕34"
    expected_output = "۰۱۲۳۴۵۶۷۸۹ ۱۴۳۴"
    assert normalizer.normalize(input_text) == expected_output


def test_unify_characters(normalizer):
    input_text = "نشان‌دهندة"
    expected_output = "نشان‌دهنده"
    assert normalizer.normalize(input_text) == expected_output

    input_text = "سایة"
    expected_output = "سایه"
    assert normalizer.normalize(input_text) == expected_output

    input_text = "ۿدف ما ػمګ بۀ ێڪډيڱڕ أښټ"
    expected_output = "هدف ما کمک به یکدیگر است"
    print(normalizer.normalize(input_text))
    print(expected_output)
    assert normalizer.normalize(input_text) == expected_output

    input_text = "کارتون"
    expected_output = "کارتون"
    assert normalizer.normalize(input_text) == expected_output

    # correct examples
    input_text = "همه با هم در برابر پلیدی و ستم خواهیم ایستاد"
    expected_output = "همه با هم در برابر پلیدی و ستم خواهیم ایستاد"
    assert normalizer.normalize(input_text) == expected_output


def test_unify_punctuations(normalizer):
    input_text = "؟?،٬!%:«»؛"
    expected_output = "؟؟،،!٪:«»؛"
    assert normalizer.unify_punctuations(input_text) == expected_output


def test_remove_emojis(normalizer):
    input_text = "😊🇮🇷سلام گلای تو خونه!🎉🎉🎊🎈"
    expected_output = "سلام گلای تو خونه!"
    assert normalizer.remove_emojis(input_text) == expected_output

    input_text = "🌹 باز هم مرغ سحر🐔 بر سر منبر گل "
    expected_output = " باز هم مرغ سحر بر سر منبر گل "
    print(normalizer.remove_emojis(input_text))
    print(expected_output)
    assert normalizer.remove_emojis(input_text) == expected_output


def test_remove_diacritics(normalizer):
    input_text = "مَنْ"
    expected_output = "من"
    assert normalizer.remove_diacritics(input_text) == expected_output

    input_text = "کُجا نِشانِ قَدَم ناتَمام خواهَد ماند؟"
    expected_output = "کجا نشان قدم ناتمام خواهد ماند؟"
    assert normalizer.remove_diacritics(input_text) == expected_output


def test_unify_arabic_unicode(normalizer):
    input_text = "﷽"
    expected_output = "بسم الله الرحمن الرحیم"
    assert normalizer.unify_arabic_unicode(input_text) == expected_output

    input_text = "پنجاه هزار ﷼"
    expected_output = "پنجاه هزار ریال"
    assert normalizer.unify_arabic_unicode(input_text) == expected_output

    input_text = "ﷲ اعلم "
    expected_output = "الله اعلم "
    assert normalizer.unify_arabic_unicode(input_text) == expected_output

    input_text = "ﷲ ﷳ"
    expected_output = "الله اکبر"
    assert normalizer.unify_arabic_unicode(input_text) == expected_output

    input_text = "ﷴ"
    expected_output = "محمد"
    assert normalizer.unify_arabic_unicode(input_text) == expected_output


def test_remove_punctuations(normalizer):
    input_text = "$@^<</من:<, ()).^%!?میروم"
    expected_output = "من میروم"
    assert normalizer.remove_punctuations(input_text) == expected_output


def test_correct_spacings(normalizer):
    """Tests normalization with a Persian sentence."""
    input_text = "   این یک جمله   نمونه   است . "
    expected_output = " این یک جمله نمونه است. "
    assert normalizer.correct_spacings(input_text) == expected_output

    input_text = "اینجا کجاست؟تو میدونی؟نمیدونم!"
    expected_output = "اینجا کجاست؟ تو میدونی؟ نمیدونم!"
    assert normalizer.correct_spacings(input_text) == expected_output

    input_text = "ناصر گفت:«من می‌روم.»"
    expected_output = "ناصر گفت: «من می‌روم.»"
    assert normalizer.correct_spacings(input_text) == expected_output

    input_text = "با کی داری حرف می زنی؟"
    expected_output = "با کی داری حرف می زنی؟"
    assert normalizer.correct_spacings(input_text) == expected_output

    input_text = "من می‌روم.تو نمی‌آیی؟"
    expected_output = "من می‌روم. تو نمی‌آیی؟"
    assert normalizer.correct_spacings(input_text) == expected_output

    input_text = "به نکته ریزی اشاره کردی!"
    expected_output = "به نکته ریزی اشاره کردی!"
    assert normalizer.correct_spacings(input_text) == expected_output


def test_remove_extra_spaces(normalizer):
    input_text = "این  یک  تست  است"
    expected_output = "این یک تست است"
    assert normalizer.remove_extra_spaces(input_text) == expected_output

    input_text = "این  یک\n\n\nتست  است"
    expected_output = "این یک\n\nتست است"
    assert normalizer.remove_extra_spaces(input_text) == expected_output

    input_text = "این\u200cیک\u200cتست\u200cاست"
    expected_output = "این\u200cیک\u200cتست\u200cاست"
    assert normalizer.remove_extra_spaces(input_text) == expected_output

    input_text = "این\u200c یک\u200c تست\u200c است"
    expected_output = "این یک تست است"
    assert normalizer.remove_extra_spaces(input_text) == expected_output

    input_text = "این  یک  تست  است  "
    expected_output = "این یک تست است "
    assert normalizer.remove_extra_spaces(input_text) == expected_output

    input_text = "این  یک  تست  است\n\n\n\n"
    expected_output = "این یک تست است\n\n"
    assert normalizer.remove_extra_spaces(input_text) == expected_output


def test_normalize(normalizer):
    input_text = "ناصر گفت:«من می‌روم.» \u200c 🎉🎉🎊🎈"
    expected_output = "ناصر گفت: «من می‌روم.»"
    assert normalizer.normalize(input_text) == expected_output

    input_text = (
        "⚡️ کاربرانی که واجد شرایط بودند نیز با پاداش های بسیار ناچیز مواجه شدند."
    )
    expected_output = (
        " کاربرانی که واجد شرایط بودند نیز با پاداش های بسیار ناچیز مواجه شدند."
    )
