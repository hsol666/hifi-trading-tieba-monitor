import os, json, asyncio, requests
import aiotieba as tb

BA_NAME = "hifi交易"          # 贴吧名（不带“吧”字后缀）
SEEN_FILE = "seen.json"
KEYWORDS_FILE = "keywords.txt"

def load_keywords():
    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

async def fetch_threads():
    async with tb.Client() as client:
        threads = await client.get_threads(BA_NAME)
        return [{"id": str(t.tid), "title": t.title} for t in threads.objs]

def send_wechat(hits):
    sendkey = os.environ["SCT_KEY"]   # Server酱 SendKey
    title = f"贴吧新帖提醒（{len(hits)}条）"
    desp = "\n\n".join(f"### {t['title']}\nhttps://tieba.baidu.com/p/{t['id']}" for t in hits)
    r = requests.post(f"https://sctapi.ftqq.com/{sendkey}.send",
                      data={"title": title, "desp": desp}, timeout=15)
    r.raise_for_status()

def main():
    keywords = load_keywords()
    seen = set()
    if os.path.exists(SEEN_FILE):
        seen = set(json.load(open(SEEN_FILE)))
    threads = asyncio.run(fetch_threads())
    new = [t for t in threads if t["id"] not in seen]
    hits = [t for t in new if any(k.lower() in t["title"].lower() for k in keywords)]
    if hits:
        send_wechat(hits)
        print(f"命中 {len(hits)} 条，已推送")
    else:
        print(f"无命中（新帖 {len(new)} 条）")
    seen.update(t["id"] for t in threads)
    json.dump(list(seen)[-3000:], open(SEEN_FILE, "w"))

if __name__ == "__main__":
    main()
