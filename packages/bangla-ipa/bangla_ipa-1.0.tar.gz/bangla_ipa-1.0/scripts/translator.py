from bangla_ipa.ipa import BanglaIPATranslator


def ipa_checker(word):
    """
    Performs IPA checking with the model.

    Params:
        word (str): Bengali word for IPA checking.

    Returns:
        None
    """
    ipa = BanglaIPATranslator()
    ipa_translated = ipa.translate(word)
    print(ipa_translated)


#
word_ipa = ipa_checker("চাষাবাদ")
word_ipa2 = ipa_checker("মহারাজ\n")
word_ipa3 = ipa_checker("সম্প্রতি\n")
word_ipa4 = ipa_checker("ভারকেন্দ্র\n")
word_ipa5 = ipa_checker("কথায়\n")
print(word_ipa2)
print(word_ipa, word_ipa2, word_ipa3, word_ipa4, word_ipa5)
