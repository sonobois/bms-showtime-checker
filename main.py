import pytz
import random
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

def check_movie_showtime_availability(url, date, title):
    logging.debug(f"Checking for {title}: {url} on {date}")
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    UAS = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    )
    ua = UAS[random.randrange(len(UAS))]
    headers = {"user-agent": ua}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # title = soup.find("div", class_="sticky-filtertitle").text
        available_dates = soup.find_all("a", class_="date-href")
        for i, available_date in enumerate(available_dates):
            available_date = available_date.text.strip().split("\n")
            available_date = list(map(str.strip, available_date))
            available_date = list(filter(bool, available_date))
            movie_date, movie_month = available_date[1:]
            available_dates[i] = datetime.datetime.strptime(
                f"{movie_date} {movie_month} {date.year}", "%d %b %Y"
            ).date()
        check = date in available_dates
        if check:
            logging.info(f"Movie {title} is available on {date}")
            logging.debug(f"Movie {title} removed from job list")
            scheduler.remove_job(title)
        return check, title
    except Exception as e:
        logging.error(f"Error while checking movie availability for {url}: {e}")
        return False, None

if __name__ == "__main__":
    urls = {
        "Doctor Strange Multiverse of Madness - IMAX 3D": 
            r"https://in.bookmyshow.com/buytickets/doctor-strange-in-the-multiverse-of-madness-bengaluru/movie-bang-ET00326385-MT/20220506",
        "Doctor Strange Multiverse of Madness - 3D": 
            r"https://in.bookmyshow.com/buytickets/doctor-strange-in-the-multiverse-of-madness-bengaluru/movie-bang-ET00326386-MT/20220506"
    }
    date = datetime.datetime(2022, 5, 14, tzinfo=IST).date()
    logging.info(f"Setting up scheduler for checking showtimes on {date}")
    scheduler = BackgroundScheduler()
    for title, url in urls.items():
        scheduler.add_job(
            func=check_movie_showtime_availability,
            args=(url, date, title),
            trigger="interval",
            seconds=60,
            id=title,
        )
    scheduler.start()
    logging.info("Scheduler started")
    while True:
        pass