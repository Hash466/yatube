import datetime as dt


def get_year(request):
    year = dt.date.today().year
    return {'year': year}
