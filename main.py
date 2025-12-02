import logging
import os
import uuid
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)


# --- MENU ---
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📄 Referat yaratish (AI)", callback_data="ref_ai")
    kb.button(text="📊 Prezentatsiya yaratish (AI)", callback_data="ppt_ai")
    kb.adjust(1)
    return kb.as_markup()


@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "Assalomu alaykum! Referat va prezentatsiya PDF yaratadigan bot.\n\nTanlang:",
        reply_markup=main_menu()
    )


ai_state = {}

# ==========================
# REFERAT
# ==========================
@dp.callback_query(lambda c: c.data == "ref_ai")
async def ref_ai_start(call: types.CallbackQuery):
    ai_state[call.from_user.id] = {"mode": "ref"}
    await call.message.answer("✍️ Referat mavzusini kiriting:")
    await call.answer()


@dp.message(lambda m: ai_state.get(m.from_user.id, {}).get("mode") == "ref")
async def ref_generate(msg: types.Message):
    mavzu = msg.text
    ai_state.pop(msg.from_user.id)

    prompt = f"{mavzu} mavzusida 8–15 betlik referat yozing. O'zbek lotin. Xulosa bo‘lmasin."

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content

    file_path = f"/mnt/data/referat_{uuid.uuid4()}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)

    y = 800
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(40, y, line[:120])
        y -= 20

    c.save()

    await msg.answer_document(types.FSInputFile(file_path), caption="📄 Referat tayyor!")


# ==========================
# PREZENTATSIYA
# ==========================
@dp.callback_query(lambda c: c.data == "ppt_ai")
async def ppt_ai_start(call: types.CallbackQuery):
    ai_state[call.from_user.id] = {"mode": "ppt"}
    await call.message.answer("📌 Prezentatsiya mavzusini kiriting:")
    await call.answer()


@dp.message(lambda m: ai_state.get(m.from_user.id, {}).get("mode") == "ppt")
async def ppt_generate(msg: types.Message):
    mavzu = msg.text
    ai_state.pop(msg.from_user.id)

    prompt = f"{mavzu} mavzusida 15–25 slaydli prezentatsiya matni. Har slayd sarlavha + 1–2 jumla."

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    slides = res.choices[0].message.content.split("\n")

    file_path = f"/mnt/data/presentation_{uuid.uuid4()}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)

    for i, line in enumerate(slides):
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, 780, f"Slayd {i+1}")
        c.setFont("Helvetica", 14)
        c.drawString(40, 740, line[:110])
        c.showPage()

    c.save()

    await msg.answer_document(types.FSInputFile(file_path), caption="📊 Prezentatsiya tayyor!")


async def main():
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
