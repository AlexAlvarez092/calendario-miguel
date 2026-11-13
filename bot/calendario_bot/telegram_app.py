"""Telegram layer: access restriction (NFR-005) and routing to the Flow."""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import Settings
from .events import EventStore
from .flow import Flow, Reply
from .gemini import GeminiReader
from .health import ping_forever
from .publisher import Publisher

logger = logging.getLogger(__name__)


def _markup(reply: Reply) -> Optional[InlineKeyboardMarkup]:
    if not reply.buttons:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=data)] for label, data in reply.buttons])


async def _send(update: Update, replies: List[Reply]) -> None:
    for reply in replies:
        await update.effective_chat.send_message(reply.text, reply_markup=_markup(reply))


def build_application(settings: Settings) -> Application:
    store = EventStore(settings.events_path)
    reader = GeminiReader(settings.gemini_api_key, settings.gemini_model)
    holder: dict = {}

    async def notify(text: str) -> None:
        await holder["app"].bot.send_message(settings.allowed_user_id, text)

    publisher = Publisher(settings.repo_dir, notify=notify)
    flow = Flow(store, publisher, reader)
    allowed = filters.User(user_id=settings.allowed_user_id)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.effective_chat.send_message(
            "Hola. Envíame la foto del cuadrante del mes, o usa /add o /modify para un día concreto. /cancel cancela lo que esté en curso."
        )

    async def health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.effective_chat.send_message("Estoy funcionando.")

    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _send(update, [flow.cancel()])

    def command(kind: str):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await _send(update, [flow.start_command(kind)])

        return handler

    async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.effective_message
        if message.photo:
            file = await message.photo[-1].get_file()
            mime = "image/jpeg"
        else:
            file = await message.document.get_file()
            mime = message.document.mime_type
        image = bytes(await file.download_as_bytearray())
        await update.effective_chat.send_message("Foto recibida, la estoy leyendo…")
        await _send(update, await flow.start_photo(image, mime))

    async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _send(update, await flow.handle_text(update.effective_message.text))

    async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        await _send(update, await flow.handle_callback(query.data))

    async def post_init(app: Application) -> None:
        holder["app"] = app
        holder["tasks"] = [asyncio.create_task(publisher.retry_forever())]
        if settings.healthcheck_url:
            holder["tasks"].append(asyncio.create_task(ping_forever(settings.healthcheck_url)))

    async def post_shutdown(app: Application) -> None:
        for task in holder.get("tasks", []):
            task.cancel()

    app = (
        ApplicationBuilder()
        .token(settings.telegram_token)
        .concurrent_updates(True)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    app.add_handler(CommandHandler("start", start, filters=allowed))
    app.add_handler(CommandHandler("health", health, filters=allowed))
    app.add_handler(CommandHandler("cancel", cancel, filters=allowed))
    app.add_handler(CommandHandler("add", command("add"), filters=allowed))
    app.add_handler(CommandHandler("modify", command("modify"), filters=allowed))
    app.add_handler(MessageHandler(allowed & (filters.PHOTO | filters.Document.IMAGE), photo))
    app.add_handler(MessageHandler(allowed & filters.TEXT & ~filters.COMMAND, text))
    app.add_handler(CallbackQueryHandler(callback, pattern=r"^\d+:", block=False))
    return app
