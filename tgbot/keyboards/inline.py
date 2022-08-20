from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.misc.utils import Map

cd_choose_lang = CallbackData("choosen_language", "lang_code")


async def choose_language(texts: Map):
    """Choose language inline keyboard"""
    # get languages from translation texts
    langs: Map = texts.user.kb.inline.languages
    keyboard = []
    for k, v in langs.items():
        keyboard.append(InlineKeyboardButton(
            v.text, callback_data=cd_choose_lang.new(lang_code=k)))
    return InlineKeyboardMarkup(
        inline_keyboard=[keyboard], row_width=len(langs.items())
    )


async def menu(texts: Map):
    """Main menu"""
    Menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=texts.menu.loyal_cards, callback_data="menu:card"),
                InlineKeyboardButton(text=texts.menu.news, callback_data="menu:news"),
            ],
            [
                InlineKeyboardButton(text=texts.menu.support, callback_data="menu:support"),
                InlineKeyboardButton(text=texts.menu.about_bot, callback_data="menu:about"),
            ],
            [
                InlineKeyboardButton(text=texts.menu.lang, callback_data="menu:lang"),

            ],
        ]
    )
    return Menu


async def gender_kb(texts: Map):
    """ single/married/divorced """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=texts.user_details.gender.male, callback_data="gender:male"),
            InlineKeyboardButton(text=texts.user_details.gender.female, callback_data="gender:female"),
        ]],
    )
    return keyboard


async def marital_status_kb(texts: Map):
    """ single/married/divorced """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=texts.user_details.marital_status.single, callback_data="marital_status:single"),
            InlineKeyboardButton(text=texts.user_details.marital_status.married, callback_data="marital_status:married"),
            InlineKeyboardButton(text=texts.user_details.marital_status.divorced, callback_data="marital_status:divorced")
        ]],
        resize_keyboard=True,
    )
    return keyboard




async def occupation_kb(texts: Map):
    """ State service/Private sector/Social sphere/Pensioner/Student/Housewife/Temporarily unemployed """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts.user_details.occupation.state_service, callback_data="occupation:state_service")],
            [InlineKeyboardButton(text=texts.user_details.occupation.private_sector, callback_data="occupation:private_sector")],
            [InlineKeyboardButton(text=texts.user_details.occupation.social_sphere, callback_data="occupation:social_sphere")],
            [InlineKeyboardButton(text=texts.user_details.occupation.pensioner, callback_data="occupation:pensioner")],
            [InlineKeyboardButton(text=texts.user_details.occupation.student, callback_data="occupation:student")],
            [InlineKeyboardButton(text=texts.user_details.occupation.housewife, callback_data="occupation:housewife")],
            [InlineKeyboardButton(text=texts.user_details.occupation.temporarily_unemployed, callback_data="occupation:temporarily_unemployed")],
        ],
        resize_keyboard=True,
    )
    return keyboard


