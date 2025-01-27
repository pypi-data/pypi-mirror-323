from zimbabwean_id_number_validator.constants import valid_letters, valid_district_codes
import re

id_number_regex = r"^\d{2}-?\d{6,7}-?[A-HJ-NP-Z]-?\d{2}$"

def validate_id_number(id_number):
    # initialize id validation results
    id_validation_results = {
        "is_id_number_valid": False,
        "description": "id number must be in one of the formats: (082047823Q29), (08-2047823Q29), or (08-2047823-Q-29)"
    }

    # check if the id number is formatted correctly
    is_id_format_correct = re.search(id_number_regex, id_number)

    if (is_id_format_correct):
        # check if the id number is valid
        # extract the letter and application centre district code
        id_letter = re.search(r"[A-Z]", id_number).group()
        application_centre_code = id_number[0:2]

        # replace all hyphens and split the id number into a list using the id letter
        id_number_array = re.sub("-", "", id_number).split(id_letter)
        place_of_origin_code = id_number_array[1]

        # convert the id number digits before the letter into a number
        id_digits_before_letter = int(id_number_array[0])
        numeric_letter_value = id_digits_before_letter % 23  # represents a key in the valid_letters object

        if (application_centre_code in valid_district_codes
                and id_letter == valid_letters[numeric_letter_value]
                and place_of_origin_code in valid_district_codes):
            # update idValidationResults and set the id number to valid
            id_validation_results.update({
                "is_id_number_valid": True,
                "description": "id number is valid"
            })

        else:
            # update the invalid id number's description
            id_validation_results.update({
                "description": "id number is invalid"
            })

    return id_validation_results
