# NER Span Annotator
A Streamlit component for visualizing and modifying Named Entity Recognition (NER) annotations in the spaCy displacy span style. This tool is particularly useful for handling overlapping NER classes.

<img src="https://github.com/forward-it/ner-span-annotator/raw/main/example.png" width="220">

### Key Features:
- **Visualization**: Displays NER annotations in a clear and intuitive span style.
- **Interactivity**: Allows you to modify NER annotations directly in the interface.

The implementation leverages code partially ported from Python to React, inspired by the [spaCy repository](https://github.com/explosion/spaCy/tree/master/spacy/displacy).
For more details about the spaCy span component, visit [this page](https://spacy.io/usage/visualizers#span).

## Installation instructions

```sh
pip install ner_span_annotator
```

## Usage instructions

```python
import streamlit as st

from ner_span_annotator import ner_span_annotator

text = "Welcome to the Bank of China."
spans = [
    {"start_token": 15, "end_token": 28, "label": "ORG"},
    {"start_token": 23, "end_token": 28, "label": "GPE"},
]

result = ner_span_annotator(
    text=text,
    spans=spans,
    labels=["ORG", "GPE"]
)

st.json(result)
```

## Development
To set up and run the development environment, follow these steps:

Navigate to the ner_span_annotator/frontend directory and run:

```
npm install    # Initialize the project and install npm dependencies
npm run start  # Start the Webpack dev server
```

Then go to the project root and run the example app:
```
pip install -e . # install template as editable package
streamlit run ner_span_annotator/example.py # run the example
```

