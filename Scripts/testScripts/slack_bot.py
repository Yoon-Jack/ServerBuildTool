import json
from datetime import datetime
from flask import Flask, request, make_response
from slack_sdk import WebClient
 
token = "xoxb-2648998061985-4248212523443-edFsYQrsjdjGmhaVk78uqKC0"
app = Flask(__name__)
client = WebClient(token)
 
 
def get_day_of_week():
    weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
 
    weekday = weekday_list[datetime.today().weekday()]
    date = datetime.today().strftime('%Y년 %m월 %d일'.encode('unicode-escape').decode()
    ).encode().decode('unicode-escape')
    result = '{}({})'.format(date, weekday)
    return result
 
def get_time():
    return datetime.today().strftime('%H시 %M분 %S초.'.encode('unicode-escape').decode()
    ).encode().decode('unicode-escape')
 
 
def get_answer(text):
    trim_text = text.replace(" ", "")
 
    answer_dict = {
        '안녕': '안녕하세요.',
        '요일': ': 오늘은 {}입니다'.format(get_day_of_week()),
        '시간': ': 현재 시간은 {}입니다.'.format(get_time()),    
    }
 
    if trim_text == '' or None:
        return "알 수 없는 질의입니다. 답변을 드릴 수 없습니다."
    elif trim_text in answer_dict.keys():
        return answer_dict[trim_text]
    else:
        for key in answer_dict.keys():
            if key.find(trim_text) != -1:
                return "연관 단어 [" + key + "]에 대한 답변입니다.\n" + answer_dict[key]
 
        for key in answer_dict.keys():
            if answer_dict[key].find(text[1:]) != -1:
                return "질문과 가장 유사한 질문 [" + key + "]에 대한 답변이에요.\n"+ answer_dict[key]
 
    return text + "은(는) 없는 질문입니다."
 
 
def event_handler(event_type, slack_event):
    channel = slack_event["event"]["channel"]
    string_slack_event = str(slack_event)
 
    if string_slack_event.find("{'type': 'user', 'user_id': ") != -1:
        try:
            if event_type == 'app_mention':
                user_query = slack_event['event']['blocks'][0]['elements'][0]['elements'][1]['text']
                answer = get_answer(user_query)
                result = client.chat_postMessage(channel=channel,
                                                 text=answer)
            return make_response("ok", 200, )
        except IndexError:
            pass
 
    message = "[%s] cannot find event handler" % event_type
 
    return make_response(message, 200, {"X-Slack-No-Retry": 1})
 
 
@app.route('/', methods=['POST'])
def hello_there():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})
 
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return event_handler(event_type, slack_event)
    return make_response("There are no slack request events", 404, {"X-Slack-No-Retry": 1})
 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)