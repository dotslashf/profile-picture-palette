from bot import Bot
from db_mongo import Database
import sys
import time
import os


db_name = os.environ.get("DB_NAME")

db = Database()
db.connect_db(db_name)
db.select_col('environment')

consumer_key = db.find_object('consumer_key')
consumer_secret = db.find_object('consumer_secret')
access_token = db.find_object('access_token')
access_token_secret = db.find_object('access_token_secret')

def main(ck, cs, at, ats, db):
    tw = Bot(cs, ck, at, ats)
    db.select_col('tweet')

    minute_wait = 5

    while True:
        l = db.find_last_object()
        last_id = l['tweet_last_id']

        since_id = tw.get_mention(last_id)

        if (last_id != since_id):
            db.insert_object({'tweet_last_id': since_id})
        else:
            print('no new mention')

        for sec in range(minute_wait * 60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d} second to check mention.\r".format(sec))
            sys.stdout.flush()
            time.sleep(1)

        
if __name__ == "__main__":
    main(consumer_key, consumer_secret, access_token, access_token_secret, db)
