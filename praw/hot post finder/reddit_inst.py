import praw, client

client = praw.Reddit(client_id=client.ID,
                    client_secret=client.Secret,
                    password=client.Pass,
                    user_agent=client.Agent,
                    username=client.Name)