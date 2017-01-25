import datetime

# filterfunc
def upcoming(book):
    release = datetime.datetime.strptime(book.publish_date, '%Y-%m-%d')
    today = datetime.datetime.today()
    return release > today

def all(book):
    return True
