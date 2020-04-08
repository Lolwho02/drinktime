from datetime import datetime



def det_current_state(date1 : datetime, date2: datetime):
    if date1.month == date2.month:
        return date2.day - date1.day
    else:
        return (date2 - date1).days