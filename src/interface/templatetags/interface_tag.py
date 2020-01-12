from django import template
register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def per_num(text):
    number = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    output = ''
    for digit in str(text):
        if '0' <= digit <= '9':
            output += number[int(digit)]
        else:
            output += digit
    return output


@register.filter
def weak_day(num):
    if num == 0:
        return 'دوشنبه'
    elif num == 1:
        return 'سه‌شنبه'
    elif num == 2:
        return 'چهارشنبه'
    elif num == 3:
        return 'پنج‌شنبه'
    elif num == 4:
        return 'جمعه'
    elif num == 5:
        return 'شنبه'
    elif num == 6:
        return 'یکشنبه'
    else:
        return '---'


@register.filter
def per_time(time):
    number = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    output = ''
    if time.hour < 10:
        output += '۰'
    for i in str(time.hour):
        output += number[int(i)]
    output += ':'
    if time.minute < 10:
        output += '۰'
    for j in str(time.minute):
        output += number[int(j)]
    return output