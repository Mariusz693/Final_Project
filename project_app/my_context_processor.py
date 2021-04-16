import datetime


def my_cp(request):
    
    today = datetime.date.today()
    
    return {'context_day': today}