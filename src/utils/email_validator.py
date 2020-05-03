import re


def email(email_str):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.fullmatch(email_regex, email_str):
        return email_str
    else:
        raise ValueError('{} is not a valid email'.format(email_str))
