import tweepy
import time
from thief import Thief

class Bot:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.auth = self.authentication()
        self.api = tweepy.API(self.auth)
        
    def authentication(self):
        self.auth = tweepy.OAuthHandler(
            self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(
            self.access_token, self.access_token_secret)
        return self.auth

    def get_user(self, user):
        return self.api.get_user(screen_name=user)

    def get_mention(self, since_id):
        new_since_id = since_id

        list_mentions = []

        for tweet in tweepy.Cursor(self.api.mentions_timeline, since_id=since_id).items():
            new_since_id = max(tweet.id, new_since_id)

            trigger_words = "can you"
            print(tweet.text)

            if trigger_words in tweet.text:
                list_mentions.append(tweet)

        self.process_mention(list_mentions)

        return new_since_id

    def get_the_palette(self, user):
        t = Thief(user)

        t.download_profile_image()
        t.generate_pattern()
        t.palette_to_gradient()
        t.first_last_color_to_gradient()
        t.dominant_color()

        print(f"Success generating 🎨  for {user.screen_name}")

    def tweet_the_palette(self, username, tweet_id):
        
        dominant = f"img/dominant/{username}_dominant.png"
        palette = f"img/palette/{username}_palette.png"
        palette_to_gradient = f"img/palette_to_gradient/{username}_palette_to_gradient.png"
        first_last_to_gradient = f"img/first_last_to_gradient/{username}_first_last_to_gradient.png"

        media_list = [dominant, palette, palette_to_gradient, first_last_to_gradient]
        media_ids = []

        for media in media_list:
            media_file = self.api.media_upload(filename=media)
            media_ids.append(media_file.media_id_string)

        status = f"🎨 Here is your palette based on your profile picture 🎨\n\nLeft to right:\nDominant Color\nPalette\nPalette to Gradient\nFirst & Last Color to Gradient"

        self.api.update_status(status=status, in_reply_to_status_id=tweet_id,
                               auto_populate_reply_metadata=True, media_ids=media_ids)
        print(f"Success tweeting the 🎨  for {username}")

    def process_mention(self, list_mentions):

        for tweet in reversed(list_mentions):
            username = tweet.user.screen_name
            user = self.get_user(username)
            
            self.get_the_palette(user)
            self.tweet_the_palette(username, tweet.id)
            time.sleep(30)