# Zimbabwean ID Number Validator

The ID numbers issued in Zimbabwe consist of either 11 or 12 alphanumeric characters. Each ID contains one alphabetic letter, while the remaining characters are numeric digits. Various systems may capture ID numbers in different formats, with the most common formats including:
- 082047823Q29  
- 08-2047823-Q-29
- 08-2047823Q29

| ID | Description           |
|------|-----------------------|
| 08   | District Code         |
| 2047823 | 6 or 7 digit sequence |
| Q    | Alphabetic letter     |
| 29   | District Code         |
-----------------------------------------------------------------------------------

This package uses regular expressions to validate the input against the established patterns. It also includes a lookup of District Codes to ensure the correctness of the ID number.
The three possible responses are as follows:
```python
{
    "is_id_number_valid": False,
    "description": "id number must be in one of the formats: (082047823Q29), (08-2047823Q29), or (08-2047823-Q-29)"
},

{
    "is_id_number_valid": False,
    "description": "id number is invalid"
},

{
    "is_id_number_valid": True,
    "description": "id number is valid"
}

```

District Codes used in the validation procedures were acquired from the following [source](https://ntjwg.uwazi.io/entity/seif769joed?file=15512639038111am2iqd21an.pdf&page=9).


## Usage

Install the package using the following command:

```bash
pip install zimbabwean-id-number-validator
```

### Usage In Python

``` python
from zimbabwean_id_number_validator import validator
validation_results = validator.validate_id_number("082047823Q21")
```

## Keywords
**Zimbabwe** **ID Number** **Validator**


