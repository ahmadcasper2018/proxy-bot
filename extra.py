from aiogram import types

usa = [
    "AT&T MOBILITY LLC",
    "COX COMMUNICATIONS INC",
    "COMCAST CABLE COMMUNICATIONS",
    "CENTURYLINK COMMUNICATIONS, LLC",
    "CHARTER COMMUNICATIONS",
    "T-MOBILE USA, INC.",
    "VERIZON BUSINESS",
]
uk = ["VIRGIN MEDIA LIMITED", "VODAFONE"]
germany = ["VERSATEL DEUTSCHLAND GMBH", "VODAFONE"]
canada = [
    "ROGERS COMMUNICATIONS CANADA INC.",
    "BELL CANADA",
    "TELUS COMMUNICATIONS INC",
]

spain = ["VODAFONE ESPANA S.A.U.", "IPCO"]


async def choose_country_isp(bot, query, country):
    states_groups = [country[i : i + 2] for i in range(0, len(country), 2)]

    callback_markup = types.InlineKeyboardMarkup(row_width=2)  # Change row_width to 2
    for group in states_groups:
        callback_options = [
            types.InlineKeyboardButton(text=element.capitalize(), callback_data=element)
            for element in group
        ]
        callback_markup.row(*callback_options)

    await bot.send_message(
        query.from_user.id,
        "اختر المزود:",
        reply_markup=callback_markup,
    )
