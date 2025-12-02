import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
import asyncio
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import uuid


# ==============================
#  BU YERGA TELEGRAM BOT TOKENI
# ==============================
BOT_TOKEN = "7989317008:AAGhfJXyWOmPJolIUi44Uknp-9xVwpxzVas"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


# ==============================
#  BU YERGA OPENAI API KEY
# ==============================
client = OpenAI(
    api_key="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"
)


# --- ASOSIY MENU ---
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📄 Referat yaratish (AI)", callback_data="ref_ai")
    kb.button(text="📊 Prezentatsiya yaratish (AI)", callback_data="ppt_ai")
    kb.adjust(1)
    return kb.as_markup()


# ========================
#       /start
# ========================
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "Assalomu alaykum!\n"
        "Men AI yordamida referat va prezentatsiya matni yaratib beraman.\n"
        "Quyidan tanlang:",
        reply_markup=main_menu()
    )


# ========================
# REFERAT YARATISH (AI)
# ========================
ai_state = {}


@dp.callback_query(lambda c: c.data == "ref_ai")
async def ref_ai_start(call: types.CallbackQuery):
    ai_state[call.from_user.id] = {"mode": "ref"}
    await call.message.answer("✍️ AI orqali referat yaratish.\n\nMavzuni kiriting:")
    await call.answer()


@dp.message(lambda m: ai_state.get(m.from_user.id, {}).get("mode") == "ref")
async def ref_ai_generate(msg: types.Message):
    mavzu = msg.text
    ai_state.pop(msg.from_user.id)

    # AI dan referat so‘rash
    prompt = f"'{mavzu}' mavzusida 8–15 betlik referat yozing. Sarlavhalar, bo‘limlar bo‘lsin."

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content

    # PDF yaratamiz
    file_path = f"/mnt/data/referat_{uuid.uuid4()}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)
    story = [Paragraph(text.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)

    await msg.answer_document(types.FSInputFile(file_path), caption="📄 AI yaratgan REFERAT tayyor!")


# ========================
# PREZENTATSIYA YARATISH (AI)
# ========================
@dp.callback_query(lambda c: c.data == "ppt_ai")
async def ppt_ai_start(call: types.CallbackQuery):
    ai_state[call.from_user.id] = {"mode": "ppt"}
    await call.message.answer("📌 AI orqali prezentatsiya yaratish.\n\nMavzuni kiriting:")
    await call.answer()


@dp.message(lambda m: ai_state.get(m.from_user.id, {}).get("mode") == "ppt")
async def ppt_ai_generate(msg: types.Message):
    mavzu = msg.text
    ai_state.pop(msg.from_user.id)

    # AI slaydlar yozadi
    prompt = f"'{mavzu}' mavzusida 15–25 slaydli prezentatsiya matnini tuzing. Har slayd alohida bo‘lsin."

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    slides = response.choices[0].message.content

    # PDF yaratamiz
    file_path = f"/mnt/data/presentation_{uuid.uuid4()}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)
    story = [Paragraph(slides.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)

    await msg.answer_document(types.FSInputFile(file_path), caption="📊 AI yaratgan PREZENTATSIYA tayyor!")


# ========================
# POLLING
# ========================
async def main():
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
