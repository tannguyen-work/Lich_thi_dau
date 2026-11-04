import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone

# Tự động lấy thông tin từ GitHub Secrets
BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
CHAT_ID = os.environ["CHAT_ID"].strip()
FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

def main():
    vn_tz = timezone(timedelta(hours=7))
    now = datetime.now(vn_tz)
    
    # Ánh xạ thứ trong tuần sang tiếng Việt (0 = Thứ 2 ... 6 = Chủ Nhật)
    weekdays_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    today_str = f"{weekdays_vn[now.weekday()]}, {now.strftime('%d/%m/%Y')}"

    # Khung lọc: 06:00 sáng nay đến 06:00 sáng mai (giờ VN)
    start_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=1)

    req = urllib.request.Request(
        FF_URL, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        events = json.loads(response.read().decode("utf-8"))

    red_usd_news = []
    for ev in events:
        if ev.get("country") == "USD" and ev.get("impact") == "High":
            ev_time = datetime.fromisoformat(ev["date"]).astimezone(vn_tz)
            if start_time <= ev_time < end_time:
                day_note = " (rạng sáng mai)" if ev_time.date() > now.date() else ""
                time_str = ev_time.strftime("%H:%M") + day_note
                red_usd_news.append(f"• <b>{time_str}</b> — {ev.get('title')}")

    if red_usd_news:
        msg = f"🔴 <b>TIN ĐỎ USD HÔM NAY ({today_str})</b>\n\n" + "\n".join(red_usd_news)
    else:
        msg = f"✅ <b>{today_str}:</b> Hôm nay không có tin Đỏ (High Impact) nào cho đồng USD."

    tele_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }).encode("utf-8")
    
    tele_req = urllib.request.Request(
        tele_url, 
        data=payload, 
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(tele_req, timeout=10) as res:
        print("Kết quả gửi Telegram:", res.read().decode("utf-8"))

if __name__ == "__main__":
    main()
