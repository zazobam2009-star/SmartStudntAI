import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from openai import OpenAI
from io import BytesIO

import os
BOT_TOKEN = os.getenv("7989317008:AAEnH9tJaPt4p5ZWi3K0hJvrmAZA4-qRNoI")
OPENAI_KEY = os.getenv("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")
# --- MENU ---
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Referat", callback_data="ref")
    kb.button(text="📊 Prezentatsiya", callback_data="prez")
    kb.adjust(1)
    return kb.as_markup()


def dizayn_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🖼 Rasmli", callback_data="d_rasm")
    kb.button(text="✨ Zamonaviy", callback_data="d_modern")
    kb.adjust(1)
    return kb.as_markup()


# --- START ---
@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.answer("Assalomu alaykum!\nQuyidagilardan birini tanlang:", reply_markup=main_menu())


USER_STATE = {}
TEMP = {}


# --- REFERAT ---
@dp.callback_query(F.data == "ref")
async def ref_start(q: CallbackQuery):
    USER_STATE[q.from_user.id] = "ref_title"
    await q.message.edit_text("Referat mavzusini kiriting (1–15 bet):")


@dp.message(F.text, lambda msg: USER_STATE.get(msg.from_user.id) == "ref_title")
async def ref_generate(msg: Message):
    title = msg.text
    await msg.answer("⏳ Referat tayyorlanmoqda, biroz kuting...")

    prompt = (
        f"Mavzu: {title}\n"
        "Til: O'zbek lotin.\n"
        "Xulosa bo'lmasin. Eng kamida 1 bet, eng ko‘pi 15 bet.\n"
        "Reja: Kirish → Asosiy qism (3–5 bo‘lim) → Yakun.\n"
    )

    ai = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=7000
    )

    text = ai.choices[0].message.content

    pdf_stream = BytesIO()
    c = canvas.Canvas(pdf_stream, pagesize=A4)
    width, height = A4

    y = height - 40
    for line in text.split("\n"):
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line[:100])
        y -= 18

    c.save()
    pdf_stream.seek(0)

    await msg.answer_document(("referat.pdf", pdf_stream))


# --- PREZENTATSIYA ---
@dp.callback_query(F.data == "prez")
async def prez_start(q: CallbackQuery):
    USER_STATE[q.from_user.id] = "prez_title"
    await q.message.edit_text("Prezentatsiya mavzusini kiriting (1–25 slayd):")


@dp.message(F.text, lambda msg: USER_STATE.get(msg.from_user.id) == "prez_title")
async def prez_dizayn(msg: Message):
    TEMP[msg.from_user.id] = {"title": msg.text}
    USER_STATE[msg.from_user.id] = "prez_dizayn"
    await msg.answer("Dizayn tanlang:", reply_markup=dizayn_menu())


@dp.callback_query(F.data.in_(["d_rasm", "d_modern"]))
async def prez_generate(q: CallbackQuery):
    dizayn = q.data
    title = TEMP[q.from_user.id]["title"]

    await q.message.edit_text("⏳ Prezentatsiya tayyorlanmoqda...")

    prompt = (
        f"Mavzu: {title}\n"
        "Til: O'zbek lotin.\n"
        "1–25 slayd oraliqda bo‘lsin.\n"
        "Har slayd: sarlavha + 2–5 punktli ro‘yxat."
    )

    ai = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5000
    )

    raw = ai.choices[0].message.content.split("\n")
    slides = [x for x in raw if x.strip()]

    pdf_stream = BytesIO()
    c = canvas.Canvas(pdf_stream, pagesize=A4)
    w, h = A4

    for slide in slides:
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, h - 60, slide[:70])

        if dizayn == "d_rasm":
            c.rect(40, h - 200, 200, 120)  # ramka (rasm o‘rniga)
        else:
            c.setFont("Helvetica", 10)
            c.drawString(40, h - 220, "Zamonaviy minimalistik dizayn")

        c.showPage()

    c.save()
    pdf_stream.seek(0)

    await q.message.answer_document(("prezentatsiya.pdf", pdf_stream))


# --- RUN ---
async def main():
    await dp.start_polling(bot)
  if name == "main":
    asyncio.run(main())
