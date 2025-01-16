import asyncio
from playwright.async_api import async_playwright
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# قائمة User-Agent لمحاكاة التصفح الطبيعي
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5043.102 Mobile Safari/537.36",
]

async def watch_youtube_video(video_url, proxy=None):
    """
    محاكاة مشاهدة فيديو على YouTube لضمان تسجيل مشاهدة.
    
    Args:
        video_url (str): رابط الفيديو.
        proxy (str): إعدادات البروكسي (اختياري).
    """
    async with async_playwright() as p:
        # إعداد المتصفح
        browser_args = ["--no-sandbox", "--disable-setuid-sandbox"]
        if proxy:
            # إعداد البروكسي إذا تم تمريره
            browser_args.append(f"--proxy-server={proxy}")

        # تشغيل المتصفح في وضع headless
        browser = await p.chromium.launch(headless=True, args=browser_args)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        try:
            # فتح الفيديو
            print(f"🌐 فتح الفيديو: {video_url}")
            await page.goto(video_url, timeout=60000)
            print("✅ تم فتح الفيديو بنجاح.")

            # الانتظار قليلاً لتأكد من تحميل الفيديو
            await asyncio.sleep(5)

            # تشغيل الفيديو
            print("🎥 تشغيل الفيديو...")
            play_button = await page.query_selector("button[aria-label='Play']")
            if play_button:
                await play_button.click()

            # مشاهدة الفيديو لمدة 35-50 ثانية
            watch_time = random.randint(35, 50)
            print(f"⏳ مشاهدة الفيديو لمدة {watch_time} ثانية...")
            await asyncio.sleep(watch_time)

            # التفاعل مع الفيديو (اختياري)
            if random.choice([True, False]):
                print("🔄 تغيير جودة الفيديو...")
                quality_menu = await page.query_selector("button[aria-label='Settings']")
                if quality_menu:
                    await quality_menu.click()
                    await asyncio.sleep(2)  # انتظار قائمة الجودة
                    quality_option = await page.query_selector("span:has-text('480p')")
                    if quality_option:
                        await quality_option.click()

            print("✅ تم إنهاء المشاهدة بنجاح.")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء المشاهدة: {e}")
        finally:
            # إغلاق المتصفح
            await browser.close()

def start(update: Update, context: CallbackContext) -> None:
    """
    أمر /start لعرض رسالة ترحيب.
    """
    update.message.reply_text(
        "👋 أهلاً بك في روبوت مشاهدات YouTube.\n"
        "أرسل رابط فيديو YouTube لبدء مشاهدة تلقائية."
    )

def watch(update: Update, context: CallbackContext) -> None:
    """
    أمر لاستقبال رابط الفيديو وبدء المشاهدة.
    """
    if len(context.args) < 1:
        update.message.reply_text("❌ يرجى إرسال رابط الفيديو بعد الأمر.")
        return

    video_url = context.args[0]
    update.message.reply_text(f"🚀 بدء المشاهدة للفيديو: {video_url}")

    # تشغيل وظيفة المشاهدة باستخدام asyncio
    asyncio.run(watch_youtube_video(video_url))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    أمر /start لعرض رسالة ترحيب.
    """
    await update.message.reply_text(
        "👋 أهلاً بك في روبوت مشاهدات YouTube.\n"
        "أرسل رابط فيديو YouTube لبدء مشاهدة تلقائية."
    )

# وظيفة أمر /watch
async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    أمر /watch لاستقبال رابط الفيديو وبدء المشاهدة.
    """
    if not context.args:
        await update.message.reply_text("❌ يرجى إرسال رابط الفيديو بعد الأمر.")
        return

    video_url = context.args[0]
    await update.message.reply_text(f"🚀 بدء المشاهدة للفيديو: {video_url}")

    # هنا يمكنك استدعاء وظيفة مشاهدة الفيديو (watch_youtube_video)
    # مثال:
    # await watch_youtube_video(video_url)

# الوظيفة الرئيسية لتشغيل الروبوت
def main() -> None:
    """
    تشغيل الروبوت.
    """
    # ضع هنا توكن البوت الخاص بك
    TELEGRAM_TOKEN = "    TELEGRAM_TOKEN = "7876191804:AAFV_DzkJRNHEHgVKTH-X3ubHGbDOYCOpYA"

    # إعداد التطبيق
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("watch", watch))

    # تشغيل الروبوت
    print("🤖 يعمل الروبوت الآن...")
    application.run_polling()

if __name__ == "__main__":
    main()
