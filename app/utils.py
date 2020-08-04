def jsonify_object(instance, cls, remove_keys=[]):
    return {i.key: instance.__getattribute__(i.key) for i in cls.__table__.columns if i.key not in remove_keys}


def one_rep_max(a_set):
    # come back and check if the unit of weight is pounds or kilograms
    if a_set.unit == "pound":
        return a_set.weight * a_set.repetition * .033 + a_set.weight
    else:
        return a_set.weight * a_set.repetition * .033 + a_set.weight


def date_formatter(date):
    day = date.day
    month = date.month
    year = date.year
    if month < 10:
        month = f"0{month}"
    if day < 10:
        day = f"0{day}"
    return f"{year}-{month}-{day}"