import logging
logging.basicConfig(level=logging.DEBUG)

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = 'xoxb-2648998061985-4248212523443-edFsYQrsjdjGmhaVk78uqKC0' # 토큰 아이디
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel="C04779XRUBX", # Channel ID
        text="Hello from your app! :tada:"
    )
except SlackApiError as e:
    assert e.response["error"]
    