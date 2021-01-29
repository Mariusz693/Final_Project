from calendar import LocaleHTMLCalendar, calendar
import datetime
import calendar


DAY_NAMES = ('Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd')


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
        week_list.append(f'{week[0].day}.{week[0].month} - {week[6].day}.{week[6].month}')
        for i, day in enumerate(week):
            day_list.append(day)
            day_name.append(DAY_NAMES[i])

    return [week_list, day_list, day_name]


def generate_list():

    today = datetime.date.today()
    my_list = []
    year = today.year - 1
    month = today.month
    for i in range(36):
        next_month = datetime.date(year=year, month=month, day=1)
        my_list.append([next_month, str(next_month)])
        month += 1
        if month > 12:
            month = 1
            year += 1

    return my_list


def change_day_to_data(my_date):

    table = my_date.split('-')
    year = int(table[0])
    month = int(table[1])
    day = int(table[2])

    return datetime.date(year=year, month=month, day=day)


def set_day_look():
    today = datetime.date.today()
    day_of_week = calendar.weekday(today.year, today.month, today.day)
    if day_of_week < 5:
        day_look = today - datetime.timedelta(days=day_of_week)
    elif day_of_week == 5:
        day_look = today + datetime.timedelta(days=2)
    else:
        day_look = today + datetime.timedelta(days=1)

    return str(day_look)


def generate_week_timetable(my_day):

    day_of_week = calendar.weekday(my_day.year, my_day.month, my_day.day)
    week_start = my_day - datetime.timedelta(days=day_of_week)
    week_end = week_start + datetime.timedelta(days=4)
    week_list = []
    for i in range(5):
        day_week = week_start + datetime.timedelta(days=i)
        week_list.append([day_week, str(day_week)])
    prev_week_start = week_start - datetime.timedelta(days=7)
    next_week_start = week_start + datetime.timedelta(days=7)
    change_list = [week_start, week_end, str(prev_week_start), str(next_week_start)]

    return [my_day, week_list, change_list]


def generate_week_user(my_day):

    week_start = my_day
    week_end = week_start + datetime.timedelta(days=4)
    prev_week_start = week_start - datetime.timedelta(days=7)
    next_week_start = week_start + datetime.timedelta(days=7)
    change_list = [week_start, week_end, str(prev_week_start), str(next_week_start)]
    week_list = []
    for i in range(5):
        day_week = week_start + datetime.timedelta(days=i)
        week_list.append(day_week)

    return [change_list, week_list]
