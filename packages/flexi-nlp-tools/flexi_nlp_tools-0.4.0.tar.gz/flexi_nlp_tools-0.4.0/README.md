# flexi-nlp-tools

[![Python Versions](https://img.shields.io/badge/Python%20Versions-%3E%3D3.11-informational)](https://pypi.org/project/nlp-flexi-tools/)
[![Version](https://img.shields.io/badge/Version-0.4.0-informational)](https://pypi.org/project/nlp-flexi-tools/)

A natural language processing toolkit based on the flexi-dict data structure, designed for efficient fuzzy search, with a focus on simplicity, performance, and flexibility.

## Table of Contents

1. [Tools](#tools)
    - [Numeral Converter](#numeral-converter)
    - [Lite Search](#lite-search)
2. [Installation](#installation)
3. [Demo](#demo)
4. [License](#license)

---

## Tools
### Numeral Converter

#### Overview
**Numeral Converter** is a Python library that provides functionality to convert numbers to text and vice versa, supporting multiple languages. 
It also allows the processing of numbers in text with support for grammatical cases, gender, and pluralization. 
Additionally, it can detect and convert numbers embedded in sentences into their numerical equivalents.

---

#### Supported Languages
- **English (en)**
- **Ukrainian (uk)**
- **Russian (ru)**

---

#### Core Functions

##### `get_available_languages()`
Retrieves a list of languages supported by the numeral converter.

- **Returns**:
  - A list of language codes (e.g., `['uk', 'en', 'ru']`).

- **Example**:

```python
from flexi_nlp_tools.numeral_converter import get_available_languages

print(get_available_languages())  # Output: ['uk', 'en', 'ru']
```

---

##### `get_max_order(lang)`
Returns the maximum numerical order supported for a specific language.

- **Parameters**:
  - `lang` (*str*): The language code (e.g., `'en'`, `'uk'`, `'ru'`).

- **Returns**:
  - The maximum numerical order as an integer.

- **Example**:

```python
from flexi_nlp_tools.numeral_converter import get_max_order

print(get_max_order('en'))  # Output: 47
print(get_max_order('uk'))  # Output: 65
```

---

##### `numeral2int(numeral, lang)`
Converts a numeral in text form into its integer representation.

- **Parameters**:
  - `numeral` (*str*): The numeral string (e.g., `'one'`, `'одного'`).
  - `lang` (*str*): The language code (e.g., `'en'`, `'uk'`, `'ru'`).

- **Returns**:
  - An integer representing the value of the numeral.

- **Example**:

```python
from flexi_nlp_tools.numeral_converter import numeral2int

print(numeral2int('one', 'en'))  # Output: 1
print(numeral2int('одного', 'ru'))  # Output: 1
print(numeral2int('тисячний', 'uk'))  # Output: 1000
```

---

##### `int2numeral(value, lang, num_class=None, gender=None, case=None, number=None)`
Converts an integer into its textual representation.

- **Parameters**:
  - `value` (*int*): The numerical value to convert.
  - `lang` (*str*): The language code.
  - `num_class` (*NumClass*, optional): Specifies the numeral class (`CARDINAL` or `ORDINAL`).
  - `gender` (*Gender*, optional): Specifies the grammatical gender (`MASCULINE`, `FEMININE`, `NEUTER`).
  - `case` (*Case*, optional): Specifies the grammatical case (`NOMINATIVE`, `GENITIVE`, etc.).
  - `number` (*Number*, optional): Specifies singular or plural (`SINGULAR`, `PLURAL`).

- **Returns**:
  - A string representing the numeral in text form.

- **Example**:

```python
from flexi_nlp_tools.numeral_converter import int2numeral

print(int2numeral(
  2023,
  lang="uk",
  num_class='ORDINAL',
  number='SINGULAR')
# Output: "дві тисячі двадцять третій"
```

---

##### `convert_numerical_in_text(text, lang, **kwargs)`
Detects numbers in a string and converts them into their numerical representation.

- **Parameters**:
  - `text` (*str*): The input text containing numerical values.
  - `lang` (*str*): The language code.

- **Returns**:
  - A string with detected numbers converted to numerical form.

- **Example**:

```python
from flexi_nlp_tools.numeral_converter import convert_numerical_in_text

text = (
  "After twenty, numbers such as twenty-five and fifty follow. "
  "For example thirty-three is thirty plus three."
)
result = convert_numerical_in_text(text, lang="en")
print(result)
# Output: "After 20, numbers such as 25 and 50 follow. "
#         "For example 33 is 30 plus 3." 
```

---

### Lite Search

#### Overview
**Lite Search** designed for efficient fuzzy searching and indexing of text data. 
It enables you to build a search index from textual data and perform approximate matches on queries, 
supporting optional transliteration for non-Latin scripts. 
The library is lightweight and ideal for scenarios where quick, non-exact text matching is required.

#### Core Functions

##### `build_search_index(data, transliterate_latin=False)`
Builds a search index from a dataset.

- **Parameters**:
  - `data` (*list of tuples*): The dataset to index, where each tuple contains a unique identifier and a string value (e.g., `[(1, "text1"), (2, "text2")]`).
  - `transliterate_latin` (*bool*, optional): Enables transliteration of non-Latin scripts for better matching.

- **Returns**:
  - A search index object that can be used with `fuzzy_search`.

- **Example**:

```python
from flexi_nlp_tools.lite_search import build_search_index

data = [(1, "one"), (2, "two"), (3, "three")]
search_index = build_search_index(data)
```

##### `fuzzy_search(query, search_index, topn=None)`
Performs a fuzzy search on the given query.

- **Parameters**:
  - `query` (*str*): The search query string.
  - `search_index` (*object*): The search index generated by `build_search_index`.
  - `topn` (*int*, optional): Limits the number of results returned. If `None`, all matching results are returned.

- **Returns**:
  - A list of identifiers (from the dataset) ranked by relevance.

- **Example**:

```python
from flexi_nlp_tools.lite_search import fuzzy_search

result = fuzzy_search(query="one", search_index=search_index)
print(result)
# Output: [1]
```

##### `fuzzy_search_internal(query, search_index, topn=None)`
Returns detailed information about the matching process, including corrections applied to the query.

- **Parameters**:
  - Same as `fuzzy_search`.

- **Returns**:
  - A list of objects containing detailed matching information.

---

#### Usage Examples

##### Example 1: Basic Fuzzy Search

```python
from flexi_nlp_tools.lite_search import build_search_index, fuzzy_search

data = [(1, "one"), (2, "two"), (3, "three")]
search_index = build_search_index(data)

result = fuzzy_search(query="one", search_index=search_index)
print(result)  # Output: [1]
```

##### Example 2: Fuzzy Search with Transliteration

```python
from flexi_nlp_tools.lite_search import build_search_index, fuzzy_search

data = [(1, "ван"), (2, "ту"), (3, "срі")]
search_index = build_search_index(data, transliterate_latin=True)

result = fuzzy_search(query="ван", search_index=search_index)
print(result)  # Output: [1]
```

##### Example 3: Advanced Query Matching

```python
from flexi_nlp_tools.lite_search import build_search_index, fuzzy_search

data = [
  (1, "Burger Vegan"),
  (2, "Burger with Pork"),
  (3, "Burger with Meat and Garlic"),
]
search_index = build_search_index(data)

query = "burger"
result = fuzzy_search(query=query, search_index=search_index)
print(result)  # Output: [1, 2, 3]
```

##### Example 4: Detailed Search Results

```python
from flexi_nlp_tools.lite_search import fuzzy_search_internal

query = "bollo"
result = fuzzy_search_internal(query=query, search_index=search_index)
for match in result:
  print(match)
```


---

## Environment Variables

The following environment variables can be used to customize the behavior of the package.
Modules are validates environment variables to ensure they meet the expected constraints. 
Invalid values will raise an `InvalidEnvironmentVariable` exception. 
Default values are used when the variables are not explicitly set.

### FlexiDict environment variables
- **`DEFAULT_TOPN_LEAVES`** (default: `10`): A positive integer representing the maximum number of top leaves to retrieve in searches. Must be greater than `0`.
- **`MIN_CORRECTION_PRICE`** (default: `1e-5`): A float in the range `[0, 1]`, representing the minimum price for applying a correction.
- **`MAX_CORRECTION_RATE`** (default: `2/3`): A float in the range `[0, 1]`, representing the maximum correction rate allowed.
- **`MAX_CORRECTION_RATE_FOR_SEARCH`** (default: `1.`): A float in the range `[0, 1]`, representing the maximum correction rate allowed when adding leaves.
- **`DEFAULT_DELETION_PRICE`** (default: `0.4`): A float in the range `[0, 1]`, representing the cost of a deletion operation.
- **`DEFAULT_SUBSTITUTION_PRICE`** (default: `0.2`): A float in the range `[0, 1]`, representing the cost of a substitution operation.
- **`DEFAULT_INSERTION_PRICE`** (default: `0.05`): A float in the range `[0, 1]`, representing the cost of an insertion operation.
- **`DEFAULT_TRANSPOSITION_PRICE`** (default: `0.35`): A float in the range `[0, 1]`, representing the cost of a transposition operation.
- **`MAX_QUEUE_SIZE`** (default: `1024`): A positive integer defining the maximum queue size for processing tasks. Must be greater than `0`.

### LiteSearch environment variables
- **`MIN_START_TOKEN_LENGTH`** (default: `3`): A positive integer defining the minimum length of a starting token. Must be greater than `0`.
- **`DEFAULT_QUERY_TRANSFORMATION_PRICE`** (default: `0.4`): A float in the range `[0, ∞)`, representing the cost of a query transformation. Must be non-negative.

---

## Installation

You can easily install nlp-flexi-tools from PyPI using pip:

```bash
pip install flexi-nlp-dict
```
---

## Demo

Check out the live demo of Flexi NLP Tools here:

[Flexi NLP Tools Demo](https://flexi-nlp-tools-8825f3a8045e.herokuapp.com/)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
