import datetime as dt


def year(request):
        d = dt.datetime.today()
        year = d.year
        return {'year': year,}
