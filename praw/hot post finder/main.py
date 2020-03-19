import praw, asyncio, math, time, client, reddit_inst, logger as log
from prawcore.exceptions import RequestException, Forbidden, ServerError, NotFound
from praw.exceptions import APIException, ClientException
reddit = None
def login():
    global reddit
    reddit = reddit_inst.client
print("Initializing Reddit instance...")
login()
if reddit:
    print("Reddit instance initialized. Initializing Client core...")
else:
    print("Failed to initialize Reddit instance. Stopping process.")
    exit()
if client.CORE:
    print("Client core ({}) initialized.".format(client.CORE))
else:
    print("Core failed to initialize. Check client.py and reinitialize core.")

unreadMessages = []


async def main():
    global unreadMessages
    while True:
        try:
            for item in reddit.inbox.unread():
                unreadMessages.append(item)
                reddit.inbox.mark_read(unreadMessages)
                if 'u/the-number-0' in item.body:
                    comment = reddit.comment(id=item.id)
                    sub = comment.subreddit
                    lim = 10
                    com = ""
                    for word in comment.body.split():
                        if word == "u/the-number-0":
                            continue
                        if 'r/' in word:
                            sub = reddit.subreddit(word.split('/')[1])
                        elif not math.isnan(int(word)):
                            if int(word) > 0 and int(word) < 101:
                                lim = int(word)
                            else:
                                com += "Input number is out of valid request range. Defaulting to 10.\n\n"
                    subs = []
                    try:
                        for subm in sub.hot(limit=lim):
                            subs.append("[{}]({})".format(subm.title, subm.permalink))
                    except NotFound:
                        com += "Your subreddit input is invalid. Defaulting to current subreddit.\n\n"
                        sub = comment.subreddit
                        for subm in sub.hot(limit=lim):
                            subs.append("[{}]({})".format(subm.title, subm.permalink))
                    com += "I have searched {} hot posts in {}. Here are the results:\n\n{}".format(
                        str(lim), sub.display_name, "\n\n".join(subs))
                    try:
                        comment.reply(com)
                    except APIException:
                        comment.reply("The amount of content is to long!")
        except RequestException:
            print("Connection to the API was dropped - Reconnecting in 30 seconds")
            log.error(
                "Connection to the API was dropped - Reconnecting in 30 seconds")
            time.sleep(30)

        except APIException:
            print("The bot was ratelimited by the API - Reconnecting")
            log.error("The bot was ratelimited by the API - Reconnecting")
            time.sleep(10)

        except ServerError:
            print(
                "Error encountered while communicating with the server - Reconnecting in 1 minute")
            log.error(
                "Error encountered while communicating with the server - Reconnecting in 1 minute")
            time.sleep(60)

        except ClientException:
            log.error("Client Exception encountered - Continuing")
            time.sleep(10)

        except Forbidden:
            print("Out of loop forbidden error - Continuing")
            log.error("Out of loop forbidden error - Continuing")

        time.sleep(5)
        unreadMessages = []

if __name__ == "__main__":
    asyncio.run(main())
