import telebot
from telebot import types

# Token bot Anda
BOT_TOKEN = '7141227909:AAFGsTOp8bPbXzBJXaPq9FEdwg3CuNSmCUY'
bot = telebot.TeleBot(BOT_TOKEN)

# Mendefinisikan ID admin dan channel log
ADMIN_ID = 5991733650
LOG_CHANNEL = '@LogTranssionIndonesia'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        if message.chat.type == 'private':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Rules", callback_data='rules_menu'))
            markup.add(types.InlineKeyboardButton("Log-Fban", url="https://t.me/LogTranssionIndonesia"))
            markup.add(types.InlineKeyboardButton("UnFban-Support", url="https://t.me/FederationTranssionIndonesia"))
            bot.send_message(
                message.chat.id, 
                "Halo dan Salam Kenal! 👋\n\n"
                "Saya adalah Administrator dari Federasi Transsion Indonesia (TFI).\n\n"
                "• Untuk melaporkan pelanggaran, gunakan perintah /report.\n\n"
                "• Untuk aju banding Fban, gunakan perintah /appeal.\n\n"
                "• Jika Anda belum mengetahui aturan, klik tombol \"Rules\" di bawah ini.\n\n"
                "• Untuk memeriksa status ban Anda, klik tombol \"Log-Fban\".\n\n"
                "• Jika Anda membutuhkan dukungan atau ingin bergabung dalam grup, klik tombol \"UnFban-Support\".", 
                reply_markup=markup, 
                parse_mode='HTML'
            )
    except Exception as e:
        print(f"Error in /start command: {e}")

@bot.message_handler(commands=['report'], func=lambda message: message.chat.type == 'private')
def handle_private_report(message):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Cheat", callback_data='report_cheat_private'),
            types.InlineKeyboardButton("Scam", callback_data='report_scam_private')
        )
        bot.send_message(message.chat.id, "Silakan pilih jenis laporan:", reply_markup=markup)
    except Exception as e:
        print(f"Error in /report command (private): {e}")

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'] and '/report' in message.text.lower())
def handle_group_report(message):
    try:
        if message.reply_to_message:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("Cheat", callback_data=f'report_cheat_group_{message.reply_to_message.message_id}'),
                types.InlineKeyboardButton("Scam", callback_data=f'report_scam_group_{message.reply_to_message.message_id}')
            )
            bot.send_message(message.chat.id, "Silakan pilih jenis laporan:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Harap reply ke pesan yang ingin Anda laporkan.")
    except Exception as e:
        print(f"Error in /report command (group): {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('report_'))
def handle_report_button(call):
    try:
        data_parts = call.data.split('_')
        if len(data_parts) < 3:
            bot.answer_callback_query(call.id, "Data laporan tidak valid.")
            return

        report_type = data_parts[1]
        report_source = data_parts[2]

        if report_source == 'group':
            if len(data_parts) == 4:
                message_id = int(data_parts[3])
                chat_id = call.message.chat.id
                user_id = call.from_user.id
                username = call.from_user.username if call.from_user.username else call.from_user.first_name
                chat_name = call.message.chat.title

                # Kirimkan format laporan ke admin
                caption = (
                    f"Laporan Baru⚠️ ({report_type.upper()})\n\n"
                    f"ID: {user_id}\n"
                    f"Username: @{username}\n"
                    f"Pada Grup: {chat_name}\n"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("Lihat Pesan🧐", 
                                               url=f"https://t.me/{call.message.chat.username}/{message_id}" if call.message.chat.username 
                                               else f"https://t.me/c/{chat_id}/{message_id}")
                )
                bot.send_message(ADMIN_ID, caption, reply_markup=markup)

                # Ganti tombol dengan pesan laporan diterima
                bot.edit_message_text("Laporan diterima. Saya akan mengirimkan informasi ini kepada Admin.",
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id)
            else:
                bot.send_message(call.message.chat.id, "Terjadi kesalahan dalam memproses laporan dari grup. Silakan coba lagi nanti.")

        elif report_source == 'private':
            bot.answer_callback_query(call.id)
            bot.edit_message_text("Kirimkan bukti berupa foto / video / username / id / link chat", 
                                  chat_id=call.message.chat.id, 
                                  message_id=call.message.message_id)
            bot.register_next_step_handler(call.message, process_evidence, report_type=report_type)

    except Exception as e:
        print(f"Error handling report button: {e}")
        bot.send_message(call.message.chat.id, "Terjadi kesalahan dalam memproses laporan. Silakan coba lagi nanti.")

def process_evidence(message, report_type):
    try:
        chat_id = message.chat.id

        if message.photo:
            caption = f"Laporan {report_type.upper()}:\n\nPesan:\n{message.caption if message.caption else 'Tidak ada pesan yang dikirim'}"
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
        elif message.video:
            caption = f"Laporan {report_type.upper()}:\n\nPesan:\n{message.caption if message.caption else 'Tidak ada pesan yang dikirim'}"
            bot.send_video(ADMIN_ID, message.video.file_id, caption=caption)
        elif message.text:
            caption = f"Laporan {report_type.upper()}:\n\nPesan:\n{message.text}"
            bot.send_message(ADMIN_ID, caption)
        else:
            bot.send_message(ADMIN_ID, f"Laporan Baru⚠️ {report_type.upper()}:\n\nTidak ada bukti yang dilampirkan.")

        bot.send_message(chat_id, "Laporan diterima. Saya akan mengirimkan informasi ini ke Admin.")
        bot.delete_message(chat_id=chat_id, message_id=message.message_id - 1)  # Delete the "kirimkan bukti" message

    except Exception as e:
        print(f"Error processing evidence: {e}")
        bot.send_message(message.chat.id, "Terjadi kesalahan dalam memproses bukti. Silakan coba lagi nanti.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('check_ban_'))
def handle_check_ban(call):
    try:
        data_parts = call.data.split('_')
        if len(data_parts) < 4:
            bot.answer_callback_query(call.id, "Data permintaan tidak valid.")
            return

        user_id = data_parts[2]
        username = data_parts[3]

        # Simulasi pencarian pesan di channel log
        found_message_id = search_message_in_channel(user_id, username)  # Fungsi pencarian pesan

        if found_message_id:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("See your ban", url=f"https://t.me/{LOG_CHANNEL[1:]}/{found_message_id}"))
            bot.edit_message_text("Pesan pemblokiran ditemukan. Klik tombol di bawah untuk melihat detailnya.",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=markup)
        else:
            bot.edit_message_text("Pemblokiran tidak ditemukan. Mohon Dipertahankan!!😆.",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)

    except Exception as e:
        print(f"Error handling check ban callback: {e}")
        bot.send_message(call.message.chat.id, "Terjadi kesalahan dalam memeriksa status pemblokiran. Silakan coba lagi nanti.")

def search_message_in_channel(user_id, username):
    # Dummy function for searching the message in the channel log
    return None

@bot.callback_query_handler(func=lambda call: call.data in ['rules_menu', 'back_to_start'])
def handle_buttons(call):
    try:
        if call.data == 'rules_menu':
            rules_text = (
                "<b><u>📜 Aturan Umum:</u></b>\n\n"
                "1. <b>Konten Negatif:</b> Dilarang menyebar rasisme, provokasi, atau konten negatif. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "2. <b>Konten Dewasa:</b> Dilarang membagikan konten 18+ termasuk link, foto, video, dan lain-lain. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "3. <b>Promosi Judi:</b> Tidak boleh mempromosikan judi. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "4. <b>Jasa Scam:</b> Dilarang mempromosikan jasa scam. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "5. <b>Promosi Togel:</b> Dilarang membagikan informasi togel. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "6. <b>Penggunaan Cheat:</b> Dilarang menggunakan cheat. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "7. <b>Share Bot Crypto:</b> Tidak boleh berbagi bot crypto. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "8. <b>Promosi Tidak Sah:</b> Tidak boleh mempromosikan produk tanpa izin. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "9. <b>Perdagangan Ilegal:</b> Tidak boleh mempromosikan perdagangan ilegal. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "10. <b>Jasa Share Ilegal:</b> Tidak boleh mempromosikan jasa share ilegal. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "11. <b>Meminjamkan Dana:</b> Dilarang meminjamkan dana. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "12. <b>Phishing:</b> Dilarang melakukan phishing atau membagikan link phishing. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "13. <b>Pembobolan Akun:</b> Dilarang melakukan pembobolan akun. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "14. <b>Mengadu Tanpa Alasan:</b> Tidak boleh mengadu tanpa alasan jelas. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "15. <b>Menyerang Pengguna:</b> Dilarang menyerang pengguna lain. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "16. <b>Penyebaran Hoax:</b> Dilarang menyebar berita bohong. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "17. <b>Spam:</b> Tidak boleh melakukan spam. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "18. <b>Rasisme:</b> Dilarang segala bentuk rasisme. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "19. <b>Share Akun Ilegal:</b> Tidak boleh berbagi akun ilegal. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "20. <b>Scam:</b> Dilarang melakukan penipuan. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "21. <b>Download Konten Ilegal:</b> Tidak boleh membagikan link download konten ilegal. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "22. <b>Menyebar Virus:</b> Dilarang menyebar virus atau malware. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "23. <b>Jual Akun:</b> Tidak boleh memperjualbelikan akun. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "24. <b>Menyebar Data Pribadi:</b> Dilarang menyebar data pribadi pengguna lain. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "25. <b>Narkoba:</b> Tidak boleh menyebar informasi atau promosi narkoba. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "26. <b>Melanggar Hak Cipta:</b> Dilarang melanggar hak cipta. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "27. <b>Pornografi Anak:</b> Segala bentuk pornografi anak dilarang. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "<b><u>🛡️ Aturan Khusus untuk Admin:</u></b>\n\n"
                "1. <b>Kepentingan Pribadi:</b> Gunakan kekuasaan administratif dengan tanggung jawab.\n\n"
                "2. <b>Penghormatan terhadap Admin:</b> Hormati keputusan admin lain. Jangan unban atau unmute tanpa izin.\n\n"
                "3. <b>Transparansi Tindakan:</b> Jelaskan tindakan dengan rinci.\n\n"
                "4. <b>Tindakan terhadap Spam:</b> Hapus pesan spam dan laporan terkait.\n\n"
                "<b><u>🤝 Aturan untuk Semua Member & Admin:</u></b>\n\n"
                "1. <b>Menghargai Sesama:</b> Hormati semua anggota dan jaga ketertiban.\n\n"
                "2. <b>Sopan Santun:</b> Berbicara dengan sopan dan hindari permusuhan.\n\n"
                "3. <b>Toxic Sewajarnya:</b> Sikap toxic harus dalam batas wajar.\n\n"
                "<b><u>-{ Pembaruan Aturan 30 - 07 - 2024 }-</u></b>"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Back to Menu", callback_data='back_to_start'))
            bot.edit_message_text(rules_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode='HTML')
        elif call.data == 'back_to_start':
            send_welcome(call.message)

    except Exception as e:
        print(f"Error handling buttons: {e}")

if __name__ == '__main__':
    bot.polling(none_stop=True)
