from calendar import HTMLCalendar, LocaleHTMLCalendar
import datetime


CHOICE_MONTH = (
    (0, 'Grudzień', 'XII'),
    (1, 'Styczeń', 'I'),
    (2, 'Luty', 'II'),
    (3, 'Marzec', 'III'),
    (4, 'Kwiecień', 'IV'),
    (5, 'Maj', 'V'),
    (6, 'Czerwiec', 'VI'),
    (7, 'Lipiec', 'VII'),
    (8, 'Sierpień', 'VIII'),
    (9, 'Wrzesień', 'IX'),
    (10, 'Październik', 'X'),
    (11, 'Listopad', 'XI'),
    (12, 'Grudzień', 'XII'),
    (13, 'Styczeń', 'I'),
)
CHOICE_WEEK = ('Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd')


class Calendar(LocaleHTMLCalendar):
    def __init__(self):
        super(Calendar, self).__init__()
    #
    # def formatmonth(self, year, month, withyear=True):  # funkcja dla formatu miesiaca z calendar.py
    #     self.year, self.month = year, month
    #     super(Calendar, self).formatmonth(year, month)
    #     v = []
    #     a = v.append
    #     a('<table class="table table-striped table-bordered">')  # tutaj zmiana na tabele bootstrapa
    #     a('\n')
    #     a(self.formatmonthname(year, month, withyear=withyear))
    #     a('\n')
    #     a(self.formatweekheader())
    #     a('\n')
    #     for week in self.monthdays2calendar(year, month):
    #         a(self.formatweek(week))
    #     a('</table>')
    #     return ''.join(v)

#
# def calendar(request, year=2021, month=1):
#     year = int(year)
#     month = int(month)
#     form = MonthForm()
#     if True:
#         cal = Calendar().formatmonth(year, month)
#         return render(
#             request,
#             'timetable.html',
#             context={'form': form, 'calendar': mark_safe(cal)}
#         )


def generate_month(my_month, my_list):
    day_list = []
    week_list = []
    day_name = []
    cal = Calendar().monthdatescalendar(my_month[1], my_month[2])
    for j in range(len(cal)):
        week_list.append([])
        for i in range(7):
            week_list[j].append(f'{cal[j][i].day}.{my_list[cal[j][i].month-1][4]}')
            day_list.append(cal[j][i])
            day_name.append(CHOICE_WEEK[i])

    return [week_list, day_list, day_name]

# def generate_month(my_month, my_list):
#     day_month = []
#     day_week = []
#     day_name = []
#     cal = Calendar().monthdayscalendar(my_month[1], my_month[2])
#     print(cal)
#     # for j in range(len(cal)):
#     #     day_week.append([])
#     #     for i in range(7):
#     #         day_week[j].append(f'{cal[j][i].day}.{my_list[cal[j][i].month-1][4]}')
#     #         day_month.append(cal[j][i])
#     #         day_name.append(CHOICE_WEEK[i])
#     return [day_week, day_month, day_name]


def generate_list():
    today = datetime.datetime.today()
    # today = today + datetime.timedelta(days=60)
    my_list = []
    year = today.year
    month = today.month
    for i in range(24):
        my_list.append([
            i+1,
            year,
            month,
            CHOICE_MONTH[month][1],
            CHOICE_MONTH[month][2],
            datetime.date(year=year, month=month, day=1)
        ])
        month += 1
        if month > 12:
            month = 1
            year += 1

    return my_list


def change_date(my_date):
    table = my_date.split('-')
    if len(table[1]) == 1:
        table[1] = '0' + table[1]
    if len(table[2]) == 1:
        table[2] = '0' + table[2]

    return '-'.join(table)


def change_date2(my_date):
    table = [str(my_date.year), str(my_date.month), str(my_date.day)]
    if len(table[1]) == 1:
        table[1] = '0' + table[1]
    if len(table[2]) == 1:
        table[2] = '0' + table[2]

    return '-'.join(table)
