import datetime
import calendar

from calendar import LocaleHTMLCalendar


DAY_NAMES = ('Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd')
MONTH_SYMBOLS = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII')


class Calendar(LocaleHTMLCalendar):
    def __init__(self):
        super(Calendar, self).__init__()


def generate_month(month_look):

    week_list = []
    day_list = []
    day_name = []
    cal = Calendar().monthdatescalendar(month_look.year, month_look.month)
    if cal[0].index(month_look) > 4:
        cal = cal[1:]

    for week in cal:
        week_list.append(f'{week[0].day}.{MONTH_SYMBOLS[week[0].month - 1]} - {week[6].day}.{MONTH_SYMBOLS[week[6].month - 1]}')
        for i, day in enumerate(week):
            day_name.append(DAY_NAMES[i])
            day_list.append(day)

    return [week_list, day_name, day_list]


def generate_list():

    today = datetime.date.today()
    my_list = []
    year = today.year - 1
    month = today.month
    for _ in range(36):
        next_month = datetime.date(year=year, month=month, day=1)
        my_list.append(next_month)
        month += 1
        if month > 12:
            month = 1
            year += 1

    return my_list


def change_day_to_date(my_date):

    table = my_date.split('-')
    year = int(table[0])
    month = int(table[1])
    day = int(table[2]) if len(table) > 2 else 1

    return datetime.date(year=year, month=month, day=day)


def set_day_look(day_look=None):
    
    if day_look:
        day_look = change_day_to_date(day_look)
    else:
        day_look = datetime.date.today()
    
    day_of_week = calendar.weekday(day_look.year, day_look.month, day_look.day)
    
    if day_of_week == 5:
        day_look = day_look + datetime.timedelta(days=2)
    elif day_of_week == 6:
        day_look = day_look + datetime.timedelta(days=1)

    return day_look


def generate_week_timetable(my_day):

    day_of_week = calendar.weekday(my_day.year, my_day.month, my_day.day)
    week_start = my_day - datetime.timedelta(days=day_of_week)
    week_list = [week_start + datetime.timedelta(days=i) for i in range(5)]
    
    return [week_list, week_start - datetime.timedelta(days=7), week_start + datetime.timedelta(days=7)]

