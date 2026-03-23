Here is the refactored Python code with meaningful variable names and improved readability:
import validators
def form_validation(first_name, last_name, email, phone):
    errors = {}
    if first_name:
        if len(first_name) < 2:
            errors['first_name'] = 'Too short'
        elif len(first_name) > 50:
            errors['first_name'] = 'Too long'
        else:
            if not validators.alpha(first_name):
                errors['first_name'] = 'Invalid characters'
    else:
        errors['first_name'] = 'Required'
    if last_name:
        if len(last_name) < 2:
            errors['last_name'] = 'Too short'
        elif len(last_name) > 50:
            errors['last_name'] = 'Too long'
        else:
            if not validators.alpha(last_name):
                errors['last_name'] = 'Invalid characters'
    else:
        errors['last_name'] = 'Required'
    if email:
        if not validators.email(email):
            errors['email'] = 'Invalid format'
    else:
        errors['email'] = 'Required'
    if phone:
        if not validators.phone_number(phone):
            errors['phone'] = 'Invalid format'
    else:
        errors['phone'] = 'Required'
    return errors
In this refactored code, I have used the `validators` library to validate email and phone number formats. This makes the code more readable and maintainable. Additionally, I have renamed variables with meaningful names for better understanding of the code.