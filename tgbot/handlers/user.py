from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.handler import ctx_data

from loguru import logger

from tgbot.keyboards.inline import choose_language, cd_choose_lang, menu, gender_kb, marital_status_kb, occupation_kb
from tgbot.keyboards.reply import phone_number
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.misc.api import contact_verify, confirm_contact, parse_news, loyal_cards, post_feedbacks, post_user_details
from tgbot.misc.states import ContactVerify, Feedback, UserDetails
from tgbot.models.models import TGUser
from tgbot.misc.utils import Map, find_button_text
from tgbot.services.database import AsyncSession
from tgbot.translations.transliterate import to_latin


async def user_token(id: str, db_session: AsyncSession, state: FSMContext):
    try:
        data = await state.get_data("token")
        print(type(data))
        print(data.__doc__)
        # token = data["token"]
        print("redis")
    except:
        data = await TGUser.get_user(db_session, telegram_id=id)
        print(type(data))
        print(data)
        token = data.token
        print("db")

    # await m.answer(token)



async def user_start(m: Message, db_session: AsyncSession, texts: Map):
    """User start command handler, ask contact if have not on DB else show menu"""
    user_id = m.chat.id
    user_info = await TGUser.get_user(db_session, telegram_id=user_id)
    await m.answer(texts.user.greeting)
    try:
        if not user_info.is_verify:
            await m.answer(texts.user.send_contact, reply_markup=await phone_number(texts))
        else:
            await m.answer(texts.user.hello.format(user_name=m.chat.first_name))
            await m.answer(texts.user.choose_options, reply_markup=await menu(texts))
    except Exception as err:
        print(f'START : {err}')



async def user_close_reply_keyboard(m: Message, texts: Map):
    """User close reply keyboard button handler"""
    await m.reply(texts.user.close_reply_keyboard, reply_markup=ReplyKeyboardRemove())


async def user_phone_sent(m: Message, texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User contact phone receiver handler"""
    user_info = m.contact
    phone = m.contact.phone_number

    # if number not start with +, add +
    if not user_info.phone_number.startswith('+'):
        phone = '+' + phone
    # updating user's phone number
    try:
        await TGUser.update_user(db_session,
                               telegram_id=db_user.telegram_id,
                               updated_fields={
                                   'firstname': user_info.first_name,
                                   'lastname': user_info.last_name,
                                   'lang_code': m.from_user.language_code,
                                   'phone': phone
                               })
        await m.reply(texts.user.phone_saved, reply_markup=ReplyKeyboardRemove())
        # send contact and get token
        send_cont = contact_verify(phone)
        await ContactVerify.token.set()
        if send_cont:
            await m.answer(texts.user.send_code)
            await m.answer(texts.user.enter_code)
            print('Contact is verified')
        else:
            print(f'Do not correct phone number {phone}')
            await m.answer("Sorry we write if this number not from Uzekistance")
    except Exception as err:
        print(f'SENT CONTACT : {err}')


async def user_get_token(m: Message, texts: Map, state: FSMContext, db_session: AsyncSession):
    """send confirm code to get token"""
    code = m.text
    user_info = await TGUser.get_user(db_session, telegram_id=m.chat.id)
    verify = confirm_contact(number=user_info.phone, code=code)
    await state.update_data(token=verify['access_token'])
    await state.reset_state(with_data=False)
    await TGUser.update_user(db_session,
                             telegram_id=m.chat.id,
                             updated_fields={'token': verify['access_token'], 'is_verify': verify['is_verified']}
                             )
    if verify['is_verified']:
        await m.answer(texts.user.choose_options, reply_markup=await menu(texts))
    else:
        await UserDetails.first_name.set()
        await m.answer(texts.user_details.not_registered)
        await m.answer(texts.user_details.first_name)
        print('is_verify False')


async def user_last_news(call: CallbackQuery, state: FSMContext, texts: Map):
    """Get last 3 news from news api and send it to user"""
    token = await state.get_data("token")
    # await call.message.delete()
    await call.message.answer(texts.menu.last_news, reply_markup=ReplyKeyboardRemove())
    try:
        print("gi")
        print(token['token'])
        data = parse_news(token['token'])
        print("hi", data)
        for key, i in data.items():
            text = f'<b>#{i["type"]}</b>\n<b><i>{i["title"]}</i></b>\n{i["description"]}'
            try:
                await call.message.answer_photo(i['image'], caption=text)
            except:
                await call.message.answer(text)
        await call.message.answer(texts.user.choose_optionss, reply_markup=await menu(texts))
    except Exception as err:
        print(f'NEWS : {err}')


async def user_about_bot(call: CallbackQuery, texts: Map):
    """Show information about the company(static)"""
    logo = 'https://yt3.ggpht.com/iMymvKy9AC0c9Tp8Pp2vtqzsn3GLVkkVfjp9ayyL7sxPkkJv4g7flzZvJjEdqqOUns6tBpJM=s900-c-k-c0x00ffffff-no-rj'
    await call.message.answer_photo(logo, texts.menu.about, reply_markup=await menu(texts))
    await call.message.delete()
    await call.answer(cache_time=60)


async def user_balance(call: CallbackQuery, state: FSMContext, db_session: AsyncSession, texts: Map):
    token = await state.get_data("token")
    # user_info = await TGUser.get_user(db_session, telegram_id=call.message.chat.id)
    data = loyal_cards(token["token"])
    await call.message.delete()
    if data:
        balance = data['total_balance']
        card_numb = data['card_encrypted']
        await call.message.answer(texts.menu.card_info.format(balance=balance, card_numb=card_numb))
    else:
        await call.message.answer(texts.menu.card_not_have)

    await call.message.answer(texts.user.choose_options, reply_markup=await menu(texts))


async def user_lang(call: CallbackQuery, texts: Map):
    """User lang command handler"""
    await call.message.delete()
    await call.message.answer(texts.user.lang, reply_markup=await choose_language(texts))


async def user_lang_choosen(cb: CallbackQuery, callback_data: dict,
                            texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User lang choosen handler"""
    code = callback_data.get('lang_code')
    await TGUser.update_user(db_session,
                           telegram_id=db_user.telegram_id,
                           updated_fields={'lang_code': code})

    # manually load translation for user with new lang_code
    texts = await TranslationMiddleware().reload_translations(cb, ctx_data.get(), code)
    btn_text = await find_button_text(cb.message.reply_markup.inline_keyboard, cb.data)
    await cb.message.edit_text(texts.user.lang_choosen.format(lang=btn_text))
    await cb.message.answer(texts.user.choose_options, reply_markup=await menu(texts))


async def user_feedback(call: CallbackQuery, texts: Map):
    await Feedback.feedback.set()
    await call.message.answer(texts.menu.send_feedback)


async def user_feedback_msg(m: Message, state: FSMContext, texts: Map):
    feedback = m.text
    print(feedback)
    token = await state.get_data("token")
    print(post_feedbacks(token['token'], feedback))
    await state.finish()

    await m.answer(texts.menu.sended_feedback)
    await m.answer(texts.user.choose_options, reply_markup=await menu(texts))


async def user_first_name(m: Message, state: FSMContext, texts: Map, ):
    first_name = m.text
    first_name = to_latin(first_name)
    print(first_name)
    await state.update_data(first_name=first_name)
    await UserDetails.next()
    await m.answer(texts.user_details.last_name)


async def user_last_name(m: Message, state: FSMContext, texts: Map, ):
    last_name = m.text
    last_name = to_latin(last_name)
    print(last_name)
    await state.update_data(last_name=last_name)
    await UserDetails.next()
    await m.answer(texts.user_details.dob)
    await m.answer(texts.user_details.dob_formats)


async def user_dob(m: Message, state: FSMContext, texts: Map):
    dob = m.text
    print(dob)
    await state.update_data(dob=dob)
    await UserDetails.next()
    await m.answer(texts.user_details.gender.choose_gender, reply_markup=await gender_kb(texts))


async def user_gender(call: CallbackQuery, state: FSMContext, texts: Map):
    if call.data == "gender:male":
        gender = "male"
    else:
        gender = "female"
    print(gender)
    await state.update_data(gender=gender)
    await UserDetails.next()
    await call.message.delete()
    await call.message.answer(texts.user_details.marital_status.status, reply_markup=await marital_status_kb(texts))


async def user_marital_status(call: CallbackQuery, state: FSMContext, texts: Map):
    if call.data == "marital_status:married":
        status = "married"
    elif call.data == "marital_status:divorced":
        status = "divorced"
    else:
        status = "single"
    print(status)
    await state.update_data(marital_status=status)
    await UserDetails.next()
    await call.message.delete()
    await call.message.answer(texts.user_details.occupation.choose_occupation, reply_markup=await occupation_kb(texts))


async def user_occupation(call: CallbackQuery, db_session: AsyncSession, state: FSMContext, texts: Map, db_user: TGUser ):
    if call.data == call.data == "occupation:":
        occupation = "State service"
    elif call.data == "occupation:private_sector":
        occupation = "Private sector"
    elif call.data == "occupation:social_sphere":
        occupation = "Social sphere"
    elif call.data == "occupation:pensioner":
        occupation = "Pensioner"
    elif call.data == "occupation:student":
        occupation = "Student"
    elif call.data == "occupation:housewife":
        occupation = "Housewife"
    else:
        occupation = "Temporarily unemployed"

    data = await state.get_data("first_name")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    dob = data.get("dob")
    gender = data.get("gender")
    marital_status = data.get("marital_status")

    data ={
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "gender": gender,
        "marital_status": marital_status,
        "occupation": occupation,
        "os": "Telegram"
    }
    await call.message.delete()
    await call.message.answer(str(data))
    token = await state.get_data("token")
    msg = post_user_details(token['token'], data)
    print(msg)
    await state.finish()
    await call.message.answer(texts.user_details.registered)
    await TGUser.update_user(db_session,
                               telegram_id=call.message.chat.id,
                               updated_fields={
                                   "is_verified": True,
                               })
    await call.message.answer(texts.user.choose_options, reply_markup=await menu(texts))

regex_ascii = r'[ -~]'
regex_data = r'(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})'


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(user_token, commands=["token"], state="*")
    dp.register_message_handler(user_get_token, state=ContactVerify.token)
    dp.register_callback_query_handler(user_last_news, text="menu:news", state='*')
    dp.register_callback_query_handler(user_about_bot, text="menu:about", state='*')
    dp.register_callback_query_handler(user_balance, text='menu:card', state='*')
    dp.register_callback_query_handler(user_lang, text="menu:lang", state="*")
    dp.register_callback_query_handler(user_feedback, text="menu:support", state="*" )
    dp.register_message_handler(user_feedback_msg, state=Feedback.feedback)
    dp.register_message_handler(user_first_name, state=UserDetails.first_name)
    dp.register_message_handler(user_last_name, state=UserDetails.last_name)
    dp.register_message_handler(user_dob, state=UserDetails.dob, regexp=regex_data)
    dp.register_callback_query_handler(user_gender, text_contains="gender", state=UserDetails.gender)
    dp.register_callback_query_handler(user_marital_status, text_contains="marital_status", state=UserDetails.marital_status)
    dp.register_callback_query_handler(user_occupation, text_contains="occupation", state=UserDetails.occupation)

    dp.register_message_handler(user_close_reply_keyboard, is_close_btn=True, state="*")
    dp.register_message_handler(user_phone_sent, content_types=["contact"], state="*")
    dp.register_callback_query_handler(user_lang_choosen, cd_choose_lang.filter(), state="*",)
