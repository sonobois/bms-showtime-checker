import pytz
import logging
import requests
import datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

IST = pytz.timezone('Asia/Kolkata')
logging.basicConfig(
    level=logging.NOTSET,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='app.log',
    filemode='w'
)

def check_movie_showtimes(title, url, date):
    logging.info(f"Checking showtimes for {title} on {date}")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        available_dates = soup.find_all("a", class_="date-href")
        available_dates = [
            datetime.datetime(
                date.year, 
                date.month, 
                int(list(map(str.strip, available_date.text.strip().split("\n")))[0])
            ).date()
            for available_date in available_dates
        ]
        available_dates_string = ', '.join(list(map(str, available_dates)))
        logging.debug(f"Dates found for {title}: {available_dates_string}")
        check = date in available_dates
        if check:
            logging.info(f"{title} is showing on {date}")
        logging.info("Checking showtimes complete")
        return check
    except Exception as e:
        logging.error(f"Error while looking for showtimes: {e}")

if __name__ == "__main__":
    urls = {
        "IMAX 3D": r"https://in.bookmyshow.com/buytickets/doctor-strange-in-the-multiverse-of-madness-bengaluru/movie-bang-ET00326385-MT/20220506",
        "3D": r"https://in.bookmyshow.com/buytickets/doctor-strange-in-the-multiverse-of-madness-bengaluru/movie-bang-ET00326386-MT/20220506"
    }
    date = datetime.datetime(2022, 5, 14, tzinfo=IST).date()
    logging.info(f"Setting up scheduler for checking showtimes on {date}")
    scheduler = BackgroundScheduler()
    for title, url in urls.items():
        scheduler.add_job(
            func=check_movie_showtimes,
            args=(title, url, date),
            trigger="interval",
            seconds=60
        )
    scheduler.start()
    logging.info("Scheduler started")
    while True:
        pass