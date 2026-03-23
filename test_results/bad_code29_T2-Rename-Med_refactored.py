Here is the refactored code with meaningful variable names and improved readability:
import validators
def form_validation(first_name, last_name, email, phone):
    errors = {}
    if first_name:
        if len(first_name) < 2 or len(first_name) > 50 or not validators.alpha(first_name):
            errors['first_name'] = 'Invalid'
    else:
        errors['first_name'] = 'Required'
    if last_name:
        if len(last_name) < 2 or len(last_name) > 50 or not validators.alpha(last_name):
            errors['last_name'] = 'Invalid'
    else:
        errors['last_name'] = 'Required'
    if email:
        if not validators.email(email):
            errors['email'] = 'Invalid'
    else:
        errors['email'] = 'Required'
    if phone:
        import re
        if not re.match(r'\d{3}-\d{3}-\d{4}', phone):
            errors['phone'] = 'Invalid'
    else:
        errors['phone'] = 'Required'
    return errors
In this refactored code, I have used the `validators` library for validating email addresses and alphabetic characters. For phone number validation, I assumed it to be a US phone number format (area code - three digits - four digits) and used regular expressions for that. Also, I removed the unused imports (json and re).