# BanglaToIPA Conversion

BanglaToIPA is a Python package designed to transcribe Bengali words into the International Phonetic Alphabet (IPA). This tool simplifies the pronunciation of Bengali words, making it easier for people worldwide who are familiar with IPA to accurately pronounce them.
## Installation

You can install the BanglaToIPA package using pip:

```shell
pip install bangla-ipa
```

## File Structure
```sh
bangla_ipa/
├── bangla_ipa/
│   ├── __init__.py
│   ├── ipa.py
├── model/
│   ├── __init__.py
│   ├── ipa_model.pth
├── data/
│   │   ├── ipa_vocab_data.csv
├── script/
│   │   ├── __init__.py
│   │   ├── translator.py
├── tests/
│   │   ├── __init__.py
│   │   ├── test_bangla_ipa.py
├── __init__.py
├── .gitignore
├── LICENSE
├── setup.py
├── README.md
└── requirements.txt
```


## Usage

Here's an example of how to use the BanglaDictionary package:

```python
# Create an instance of the BanglaDictionary
from bangla_ipa.ipa import BanglaIPATranslator
ipa = BanglaIPATranslator()

# Get the meaning of a word
translated_ipa = ipa.translate("মহারাজ") # Output: "mɔharaɟ"
```

## Data Source

The data used by the BanglaToIPA package is sourced from private annotated corpus for bengali letters and their appropriate form of IPA. It is carefully curated and validated from multiple resources before training and generating the model for transcribing IPA for bengali words.

## Contributing
If you find any issues or would like to contribute to the BanglaToIPA package, please feel free to open an issue or submit a pull request on the GitHub repository. Feel free to create issues to contact.


## License
The BanglaToIPA package is released under the MIT License. You are free to use, modify, and distribute this package in your own projects.

