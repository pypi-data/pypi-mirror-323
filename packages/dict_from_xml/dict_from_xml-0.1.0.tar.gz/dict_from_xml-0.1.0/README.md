# xml_dict

A Python package for converting XML documents and XML strings to dictionaries.

## Installation

```bash
pip install xml_dict
```

## Usage

### Basic Example

```python
from xml_dict import xfile, xstring

# Convert XML file to dictionary
xml_file = "/path/to/file.xml"
result.dict = xfile(xml_file)

# Convert XML string to dictionary
xml_string = """
<root>
    <person>
        <name>John</name>
        <age>30</age>
    </person>
</root>
"""
result_dict = xstring(xml_string)

## Main Functions

### xstring(xml_string)
Converts XML string to dictionary.

- `xml_string`: XML string
- Returns: Dictionary object representation of XML string

### xfile(path)
Converts XML in file to dictionary.

- `path`: absolute or relative path to a xml file
- Returns: Dictionary object representation of XML in file

## License

This project is licensed under the MIT License.
