import requests
import json

def main():
    url = "http://localhost:46130/conversation"

    # 可以修改以下变量来测试不同的输入
    # 测试方法，首先使用conversation_id和parent_message_id为none请求，你会得到
    # 类似输出
    # \API2D-MySQL-Context>python testgpt.py
    # 响应:  您上一句话是“我正在测试上下文，请记住我说的这句话，我说今天天气真好。”
    # conversationId:  f0ccac05-34fa-450f-ab99-175a3c654547
    # messageId:  8021976f-63f0-455b-805d-5fb969792fa9
    # 在下一次运行testgpt.py时，在conversationId和parent_message_id填入获得的conversationId和messageId
    # 你会得到一个和原生chatgpt网页接口体验一致的api上下文
    # 每次仅需传递conversationId和上一次回复时候的messageId，即可自动维持上下文
    # 支持从同一个conversationId的任何parent_message_id继续对话，并且得益于mysql，上下文可以持久化存储。
    message = "我正在进行上下文测试，请你记住我说的话，我说今天的天气真好"
    conversation_id = None
    parent_message_id = None

    data = {
        "message": message,
        "conversationId": conversation_id,
        "parentMessageId": parent_message_id
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        print("响应: ", response_data["response"])
        print("conversationId: ", response_data["conversationId"])
        print("messageId: ", response_data["messageId"])
    else:
        print("请求失败，状态码: ", response.status_code)
        print("错误信息: ", response.text)

if __name__ == "__main__":
    main()