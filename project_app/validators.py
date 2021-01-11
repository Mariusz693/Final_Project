from django.core.exceptions import ValidationError


def validate_tel_number(tel_number):
    if len(tel_number) != 9:
        raise ValidationError('Wpisz poprawnie  numer telefonu, musi zawierać 9 cyfr')
    for num in tel_number:
        if not num.isdigit():
            raise ValidationError('Wpisz poprawnie  numer telefonu')