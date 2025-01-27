from barkr.connections.base import ConnectionMode
from barkr.connections.mastodon import MastodonConnection
from barkr.connections.bluesky import BlueskyConnection
from barkr.main import Barkr

h = Barkr(
    [
        MastodonConnection(
            "Mastodon (@andresitorresm@fosstodon.org)",
            modes=[ConnectionMode.READ, ConnectionMode.WRITE],
            access_token="bTJUo5EZjD2S-9TBUj7UtwXAZqo1uKlJMAV9Hrp6Cf4",
            instance_url="https://fosstodon.org",
        ),
        BlueskyConnection(
            name="Bluesky (@andresitorresm.com)",
            modes=[ConnectionMode.READ, ConnectionMode.WRITE],
            handle="andresitorresm.com",
            password="g6HU9eWZMuZAimk"
        ),
    ]
)
h.start()
