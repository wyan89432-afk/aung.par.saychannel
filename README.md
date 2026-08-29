# YouTube → Telegram Auto Sync

Checks @htunmin7245 every 30 minutes and sends new videos to Telegram at max 360p.

## Setup
Add GitHub Actions secrets:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

Add the bot to the target Telegram group/channel and allow it to post.

Videos are downloaded only to temporary runner storage, uploaded, then deleted. The repository stores only processed video IDs.
