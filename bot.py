# -*- encoding: UTF-8 -*-
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageSendMessage, MessageEvent, StickerMessage, TextMessage, TextSendMessage

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

@app.route('/', methods=['GET'])
def index():
    return 'OK'

@app.route('/b9d0f6b86be604eb/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def summarize_stickers(hash_key):
    summary = ''
    for sticker in STICKERS_TO_COUNT:
        count = redis_client.hget(hash_key, sticker['id'])
        if count is None:
            count = 0
        summary += '%s - %d 次\n' % (sticker['name'], int(count))
    return summary

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message
    text = message.text.strip()
    summary = None
    if text == 'bot stats':
        summary = '昨日厭世貼圖統計：\n'
        hash_key = 'GROUP_%s_PREVIOUS' % GROUP_ID
    if text == 'bot today':
        summary = '本日厭世貼圖統計：\n'
        hash_key = 'GROUP_%s' % GROUP_ID
    if summary is not None:
        summary += summarize_stickers(hash_key)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))

    if u'馮世寬' in text:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='超過 100 分！'))
    elif u'咩咩' in text:
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url='https://storage.googleapis.com/evanchen/temp/batmap-slaps-robin.jpg',
                preview_image_url='https://storage.googleapis.com/evanchen/temp/batmap-slaps-robin.jpg'
            )
        )
    elif u'陳經理' in text:
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url='https://storage.googleapis.com/evanchen/temp/cayenne.jpg',
                preview_image_url='https://storage.googleapis.com/evanchen/temp/cayenne.jpg'
            )
        )

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    message = event.message
    sticker_id = message.sticker_id
    # app.logger.info('Sticker#' + sticker_id)
    if sticker_id not in STICKERS_ID_TO_COUNT:
        return
    hash_key = 'GROUP_%s' % GROUP_ID
    redis_client.hincrby(hash_key, sticker_id)
    app.logger.info('Sticker#' + sticker_id + ' counted')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
