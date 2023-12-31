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


async def choose_country_isp(bot, query, country, country_name):
    states_groups = [country[i : i + 2] for i in range(0, len(country), 2)]

    callback_markup = types.InlineKeyboardMarkup(row_width=2)  # Change row_width to 2
    for group in states_groups:
        callback_options = [
            types.InlineKeyboardButton(
                text=element.capitalize(),
                switch_inline_query_current_chat=f"SOCKS5 | ISP | {country_name} |{element}",
            )
            for element in group
        ]

        callback_markup.row(*callback_options)
    callback_markup.row(types.InlineKeyboardButton(text="back", callback_data="back"))

    await query.message.edit_reply_markup(reply_markup=callback_markup)


prem_mapper = {
    "UNITED STATES": "US",
    "CANADA": "CA",
    "SPAIN": "ES",
    "GERMANY": "DE",
    "UNITED KINGDOM": "GB",
}
