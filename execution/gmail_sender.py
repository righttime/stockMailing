import os
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message_with_images(sender, to, subject, html_content, image_paths):
    message = MIMEMultipart('related')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)
    msg_html = MIMEText(html_content, 'html')
    msg_alternative.attach(msg_html)
    for ticker, path in image_paths.items():
        if os.path.exists(path):
            with open(path, 'rb') as f:
                msg_image = MIMEImage(f.read())
                msg_image.add_header('Content-ID', f'<{ticker}>')
                message.attach(msg_image)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_report(recipient_email, context_file=".tmp/news_context.json"):
    if not os.path.exists(context_file): return
    with open(context_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    html_head = """
    <html>
    <head>
    <style>
        .container { width: 100%; max-width: 1000px; margin: 0 auto; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }
        .item { 
            display: inline-block; 
            width: 45%; 
            margin: 1%; 
            border: 1px solid #ddd; 
            padding: 15px; 
            vertical-align: top; 
            background: #fff; 
            box-sizing: border-box;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .rank-badge { background: #e74c3c; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 1.1em; }
        .price-info { font-size: 1.2em; color: #333; margin: 10px 0; }
        .rank-details { 
            background: #f8f9fa; 
            padding: 8px; 
            border-radius: 4px; 
            font-size: 0.85em; 
            color: #555; 
            line-height: 1.6;
            margin: 10px 0;
        }
        .news-list { padding-left: 18px; margin: 10px 0; font-size: 0.85em; color: #444; }
        .news-list li { margin-bottom: 5px; }
        img { width: 100%; height: auto; border: 1px solid #eee; border-radius: 4px; margin: 5px 0; }
        h3 { margin: 10px 0 5px 0; color: #2c3e50; }
    </style>
    </head>
    <body>
    <div class="container">
        <h1 style="text-align: center; color: #333;">오늘의 눌림목 TOP 100 분석 리포트</h1>
        <p style="text-align: center; color: #666;">(순위 기준: 등락률 + 시가총액 + 거래대금 합산 점수)</p>
        <div style="text-align: center; margin-bottom: 30px;">
    """

    html_items = ""
    image_paths = {}
    chart_dir = ".tmp/charts"

    for idx, item in enumerate(data):
        ticker = str(item['code']).zfill(6)
        chart_path = os.path.join(chart_dir, f"{ticker}.png")
        
        # Accessing ranking fields precisely
        r_change = item.get('rank_change', '-')
        r_cap = item.get('rank_cap', '-')
        r_value = item.get('rank_value', '-')
        total_score = item.get('total_score', '-')
        
        html_items += f"""
        <div class="item">
            <span class="rank-badge">NO.{idx+1}</span>
            <h3>{item['name']} ({item['code']})</h3>
            <div class="price-info"><strong>{item['price']:,}원</strong> <span style="color:{'#e74c3c' if item['change'] > 0 else '#3498db'}">({item['change']}%)</span></div>
            
            <div class="rank-details">
                <b>종합 점수:</b> {total_score}<br/>
                <b>상세 순위:</b> 등락 {r_change}위 | 시총 {r_cap}위 | 거래 {r_value}위
            </div>
        """
        
        if os.path.exists(chart_path):
            naver_link = f"https://finance.naver.com/item/main.naver?code={ticker}"
            html_items += f'<a href="{naver_link}"><img src="cid:{ticker}" alt="stock chart" style="border:none;"></a>'
            image_paths[ticker] = chart_path
        
        html_items += '<ul class="news-list">'
        for n in item.get('news', []):
            html_items += f"<li><a href='{n['link']}' style='color:#3498db; text-decoration:none;'>{n['title']}</a></li>"
        html_items += "</ul></div>"

    html_foot = "</div></div></body></html>"
    full_html = html_head + html_items + html_foot

    service = get_gmail_service()
    message = create_message_with_images("me", recipient_email, f"[Stock Alpha] 오늘의 분석 리스트 (TOP {len(data)})", full_html, image_paths)
    
    try:
        service.users().messages().send(userId="me", body=message).execute()
        print(f"Report sent to {recipient_email} with {len(data)} items.")
    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    # 메일링 리스트: 여기에 추가하고 싶은 이메일 주소들을 쉼표로 구분해서 넣어주세요.
    mailing_list = [
        "eyedoloveu@gmail.com",
        "1004dlfksl@gmail.com"
    ]
    
    for email in mailing_list:
        send_report(email.strip())
