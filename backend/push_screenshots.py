"""推送产业链截图到飞书 (使用 image 消息类型)"""
import os, sys, json, ssl, urllib.request, uuid

sys.path.insert(0, os.path.dirname(__file__))
from hermes_push import get_feishu_token, FEISHU_CHAT_ID

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


def upload_image(token, image_path, filename):
    """上传图片到飞书, 返回 image_key"""
    boundary = uuid.uuid4().hex
    with open(image_path, "rb") as f:
        img_data = f.read()
    data = b""
    data += f'--{boundary}\r\nContent-Disposition: form-data; name="image_type"\r\n\r\nmessage\r\n'.encode()
    data += f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{filename}"\r\nContent-Type: image/png\r\n\r\n'.encode()
    data += img_data
    data += f'\r\n--{boundary}--\r\n'.encode()

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request("https://open.feishu.cn/open-apis/im/v1/images",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=60, context=ctx).read())
    if resp.get("code") == 0:
        return resp["data"]["image_key"]
    print(f"[!] 上传失败: {resp}")
    return None


def send_text(token, text):
    """发送纯文本消息"""
    payload = json.dumps({
        "receive_id": FEISHU_CHAT_ID, "msg_type": "text",
        "content": json.dumps({"text": text})
    }).encode()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=30, context=ctx)


def send_image_msg(token, image_key, text=""):
    """发送图片消息"""
    payload = json.dumps({
        "receive_id": FEISHU_CHAT_ID,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }).encode()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30, context=ctx).read())
    if resp.get("code") == 0:
        print(f"[✅] 发送成功")
    else:
        print(f"[!] 发送失败: {resp.get('msg','')}")


def push():
    print("[Hermes] 获取 Token...")
    token = get_feishu_token()
    if not token:
        return

    screenshots = [
        "01-graph-overview.png", "02-search.png", "03-enterprise-detail.png",
        "04-analysis.png", "05-chain-detail.png",
    ]
    descs = {
        "01-graph-overview.png": "📊 图谱主视图 (111节点/160边)",
        "02-search.png": "🔍 搜索\"润泽\"结果",
        "03-enterprise-detail.png": "🏢 企业详情面板",
        "04-analysis.png": "📈 产业链分析弹窗",
        "05-chain-detail.png": "⛓️ 产业链详情",
    }

    # 发送开头消息
    send_text(token, f"📸 **高明区产业链知识图谱截图** ({len(screenshots)}张)")

    for fname in screenshots:
        path = os.path.join(ASSETS_DIR, fname)
        if not os.path.exists(path):
            continue
        desc = descs.get(fname, fname)
        print(f"[上传] {desc}...")
        key = upload_image(token, path, fname)
        if key:
            print(f"[发送] {desc}...")
            send_image_msg(token, key)

    print(f"\n✅ 截图推送完成")


if __name__ == "__main__":
    push()
