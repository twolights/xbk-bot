# -*- encoding: UTF-8 -*-
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, StickerMessage, TextMessage, TextSendMessage

import redis
import os

from stickers import STICKERS_TO_COUNT

GROUP_ID = os.environ['THE_LINE_GROUP_ID']

STICKERS_ID_TO_COUNT = []

for sticker in STICKERS_TO_COUNT:
    STICKERS_ID_TO_COUNT.append(sticker['id'])

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

redis_client = redis.StrictRedis(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT'])
)

@app.route("/b9d0f6b86be604eb/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message
    text = message.text.strip()
    if not text == 'bot stats':
        return
    hash_key = 'GROUP_%s_PREVIOUS' % GROUP_ID
    summary = '昨日厭世貼圖統計：\n'
    for sticker in STICKERS_TO_COUNT:
        count = redis_client.hget(hash_key, sticker['id'])
        if count is None:
            count = 0
        summary += '%s - %d 次\n' % (sticker['name'], int(count))
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    message = event.message
    sticker_id = message.sticker_id
    if sticker_id not in STICKERS_ID_TO_COUNT:
        return
    hash_key = 'GROUP_%s' % GROUP_ID
    redis_client.hincrby(hash_key, sticker_id)
    app.logger.info('Sticker#' + sticker_id + ' counted')

if __name__ == "__main__":
    app.run()
