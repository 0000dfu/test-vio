import asyncio
from playwright.async_api import async_playwright
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# قائمة User-Agent لمحاكاة التصفح الطبيعي
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5043.102 Mobile Safari/537.36",
]

class YouTubeViewer:
    """
    Class to manage YouTube video watching functionality.
    """
    def __init__(self, user_agents=None):
        self.user_agents = user_agents or USER_AGENTS

    async def watch_video(self, video_url, proxy=None):
        """
        Simulate watching a YouTube video to ensure a view is recorded.
        
        Args:
            video_url (str): The YouTube video URL.
            proxy (str): Proxy settings (optional).
        """
        async with async_playwright() as p:
            # Configure browser
            browser_args = ["--no-sandbox", "--disable-setuid-sandbox"]
            if proxy:
                browser_args.append(f"--proxy-server={proxy}")

            # Launch the browser in headless mode
            browser = await p.chromium.launch(headless=True, args=browser_args)
            context = await browser.new_context(user_agent=random.choice(self.user_agents))
            page = await context.new_page()

            try:
                print(f"🌐 Opening video: {video_url}")
                await page.goto(video_url, timeout=60000)
                print("✅ Page loaded successfully.")

                # Wait for video to load
                await asyncio.sleep(5)

                # Play the video
                print("🎥 Playing the video...")
                play_button = await page.query_selector("button[aria-label='Play']")
                if play_button:
                    await play_button.click()

                # Watch the video for a random duration
                watch_time = random.randint(350, 500)
                print(f"⏳ Watching the video for {watch_time} seconds...")
                await asyncio.sleep(watch_time)

                # Optional: Interact with the video (change quality)
                if random.choice([True, False]):
                    print("🔄 Changing video quality...")
                    quality_menu = await page.query_selector("button[aria-label='Settings']")
                    if quality_menu:
                        await quality_menu.click()
                        await asyncio.sleep(2)  # Wait for the quality menu
                        quality_option = await page.query_selector("span:has-text('480p')")
                        if quality_option:
                            await quality_option.click()

                print("✅ Finished watching the video.")
            except Exception as e:
                print(f"❌ Error while watching the video: {e}")
            finally:
                # Close the browser
                await browser.close()

# Instance of YouTubeViewer
viewer = YouTubeViewer()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command to display a welcome message.
    """
    await update.message.reply_text(
        "👋 Welcome to the YouTube Views Bot.\n"
        "Send a YouTube video link to start viewing automatically."
    )

async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /watch command to start viewing a YouTube video.
    """
    if not context.args:
        await update.message.reply_text("❌ Please provide a YouTube video link after the command.")
        return

    video_url = context.args[0]
    await update.message.reply_text(f"🚀 Starting to watch the video: {video_url}")

    # Start watching the video
    try:
        await viewer.watch_video(video_url)
        await update.message.reply_text(f"✅ Finished watching: {video_url}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main() -> None:
    """
    Run the Telegram bot.
    """
    # Your Telegram bot token
    TELEGRAM_TOKEN = "7876191804:AAFV_DzkJRNHEHgVKTH-X3ubHGbDOYCOpYA"

    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("watch", watch))

    # Run the bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
