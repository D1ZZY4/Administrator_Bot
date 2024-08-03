import telebot
from telebot import types
import json
import os

# Token bot Anda
BOT_TOKEN = '7141227909:AAFGsTOp8bPbXzBJXaPq9FEdwg3CuNSmCUY'
bot = telebot.TeleBot(BOT_TOKEN)

# File path for storing admin data
ADMIN_FILE = 'admins.json'

# Load admins from file
def load_admins():
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save admins to file
def save_admins(admins):
    with open(ADMIN_FILE, 'w') as file:
        json.dump(admins, file)

# Load admin data
admins = load_admins()
if 5991733650 not in admins:
    admins[5991733650] = [5991733650, 1274879104, 6499966648, 1077734345]  # Initial data if not present

# Function to handle /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id == 5991733650:  # Admin ID
        markup = types.InlineKeyboardMarkup()
        add_admin_btn = types.InlineKeyboardButton('Add Admin', callback_data='add_admin')
        admin_list_btn = types.InlineKeyboardButton('Admin List', callback_data='admin_list')
        markup.add(add_admin_btn, admin_list_btn)
        bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)
    elif message.from_user.id in admins.get(5991733650, []):  # Other admins
        bot.send_message(message.chat.id, "Welcome back, Admin!")
    else:  # Non-admins
        try:
            if message.chat.type == 'private':
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Rules", callback_data='rules_menu'))
                markup.add(types.InlineKeyboardButton("Log-Fban", url="https://t.me/LogTranssionIndonesia"))
                markup.add(types.InlineKeyboardButton("UnFban-Support", url="https://t.me/FederationTranssionIndonesia"))
                bot.send_message(
                    message.chat.id,
                    "<b><i>Halo dan Salam Kenal! 👋</i></b>\n\n"
                    "<i>Saya adalah Administrator dari Federasi Transsion Indonesia (TFI).</i>\n\n"
                    "• <i>Untuk melaporkan pelanggaran, gunakan perintah</i> <b><i>/report</i></b>.\n\n"
                    "• <i>Untuk aju banding Fban, gunakan perintah</i> <b><i>/appeal</i></b>.\n\n"
                    "• <i>Jika Anda belum mengetahui aturan, klik tombol</i> <b><i>\"Rules\"</i></b> <i>di bawah ini.</i>\n\n"
                    "• <i>Untuk memeriksa status ban Anda, klik tombol</i> <b><i>\"Log Fban\"</i></b>.\n\n"
                    "• <i>Jika Anda membutuhkan dukungan atau ingin bergabung dalam grup, klik tombol</i> <b><i>\"UnFban Support\"</i></b>.",
                    parse_mode='HTML',
                    reply_markup=markup
                )
        except Exception as e:
            print(f"Error in /start command: {e}")

# Function to handle callback queries
@bot.callback_query_handler(func=lambda call: call.data in ['add_admin', 'admin_list'])
def handle_callback_query(call):
    if call.from_user.id == 5991733650:
        if call.data == 'add_admin':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            msg = bot.send_message(call.message.chat.id, "Send the ID or username of the user to add as admin.")
            bot.register_next_step_handler(msg, add_admin)
        elif call.data == 'admin_list':
            admin_list = admins.get(5991733650, [])
            admin_list_str = ', '.join(map(str, admin_list))
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(call.message.chat.id, f"Current admins: {admin_list_str}")
    else:
        bot.send_message(call.message.chat.id, "You are not authorized to use these commands.")

# Function to add admin
def add_admin(message):
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins[5991733650]:
            admins[5991733650].append(new_admin_id)
            save_admins(admins)  # Save the updated admin list to the file
            bot.send_message(message.chat.id, f"User {new_admin_id} has been added as admin.")
        else:
            bot.send_message(message.chat.id, "User is already an admin.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid ID. Please send a numeric ID.")

# Function to handle /report command in private chat
@bot.message_handler(commands=['report'], func=lambda message: message.chat.type == 'private')
def handle_private_report(message):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Spam", callback_data='report_spam_private'),
            types.InlineKeyboardButton("Scam", callback_data='report_scam_private'),
            types.InlineKeyboardButton("Porn", callback_data='report_porn_private'),
            types.InlineKeyboardButton("Rasisme", callback_data='report_rasisme_private'),
            types.InlineKeyboardButton("Rusuh", callback_data='report_rusuh_private'),
            types.InlineKeyboardButton("Cheat", callback_data='report_cheat_private')
        )
        markup.add(types.InlineKeyboardButton("Cancel", callback_data='cancel_report'))
        bot.send_message(message.chat.id, "Silakan pilih jenis laporan atau batalkan:", reply_markup=markup)
    except Exception as e:
        print(f"Error in /report command (private): {e}")

# Function to handle cancel report
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_report')
def cancel_report(call):
    try:
        bot.answer_callback_query(call.id, "Laporan dibatalkan.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Laporan telah dibatalkan.")
    except Exception as e:
        print(f"Error in cancel report: {e}")

# Function to handle /report command in group or supergroup
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'] and '/report' in message.text.lower())
def handle_group_report(message):
    try:
        if message.reply_to_message:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("Spam", callback_data=f'report_spam_group_{message.reply_to_message.message_id}'),
                types.InlineKeyboardButton("Scam", callback_data=f'report_scam_group_{message.reply_to_message.message_id}'),
                types.InlineKeyboardButton("Porn", callback_data=f'report_porn_group_{message.reply_to_message.message_id}'),
                types.InlineKeyboardButton("Rasisme", callback_data=f'report_rasis_group_{message.reply_to_message.message_id}'),
                types.InlineKeyboardButton("Rusuh", callback_data=f'report_rusuh_group_{message.reply_to_message.message_id}'),
                types.InlineKeyboardButton("Cheat", callback_data=f'report_cheat_group_{message.reply_to_message.message_id}')
            )
            markup.add(types.InlineKeyboardButton("Cancel", callback_data='report_cancel'))
            bot.send_message(message.chat.id, "Silakan pilih jenis laporan atau batalkan:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Harap reply ke pesan yang ingin Anda laporkan.")
    except Exception as e:
        print(f"Error in /report command (group): {e}")

# Function to handle cancel report in group or supergroup
@bot.callback_query_handler(func=lambda call: call.data == 'report_cancel')
def cancel_report(call):
    try:
        bot.answer_callback_query(call.id, "Laporan dibatalkan.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Laporan telah dibatalkan.")
    except Exception as e:
        print(f"Error in cancel report: {e}")

# Function to handle callback queries
@bot.callback_query_handler(func=lambda call: call.data.startswith('report_'))
def handle_report_button(call):
    try:
        data_parts = call.data.split('_')
        if len(data_parts) < 3:
            bot.answer_callback_query(call.id, "Data laporan tidak valid.")
            return

        report_type = data_parts[1]
        report_source = data_parts[2]

        admin_ids = admins.get(5991733650, [])

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
                for admin_id in admin_ids:
                    try:
                        bot.send_message(admin_id, caption, reply_markup=markup)
                    except Exception as e:
                        print(f"Error sending report to admin {admin_id}: {e}")
                
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
            bot.register_next_step_handler(call.message, process_evidence, report_type=report_type, admin_ids=admin_ids)

    except Exception as e:
        print(f"Error handling report button: {e}")
        bot.send_message(call.message.chat.id, "Terjadi kesalahan dalam memproses laporan. Silahkan coba lagi nanti.")

def process_evidence(message, report_type, admin_ids):
    try:
        chat_id = message.chat.id
        caption = f"Laporan Baru⚠️ {report_type.upper()}:\n\nBukti:\n"

        # Handle forwarded messages
        if message.forward_from:
            caption += f"Pesan diteruskan dari: {message.forward_from.id} @{message.forward_from.username}\n"

        if message.caption:
            caption += f"\n{message.caption}"
        elif message.text:
            caption += f"\n{message.text}"
        elif message.photo:
            caption += "Foto dilampirkan."
        elif message.video:
            caption += "Video dilampirkan."
        else:
            caption += "Tidak ada bukti yang dilampirkan."

        for admin_id in admin_ids:
            try:
                if message.photo:
                    bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption)
                elif message.video:
                    bot.send_video(admin_id, message.video.file_id, caption=caption)
                elif message.text:
                    bot.send_message(admin_id, caption)
                else:
                    bot.send_message(admin_id, caption)
            except telebot.apihelper.ApiException as e:
                # Handle cases where bot can't send a message
                if e.result_json.get('error_code') == 403:
                    print(f"Bot tidak dapat mengirim pesan ke admin {admin_id}. Admin harus memulai percakapan terlebih dahulu.")
                else:
                    print(f"Error sending evidence to admin {admin_id}: {e}")

        bot.send_message(chat_id, "Laporan diterima. Saya akan mengirimkan informasi ini ke Admin.")
        bot.delete_message(chat_id=chat_id, message_id=message.message_id - 1) # Delete the "kirimkan bukti" message
    
    except Exception as e:
        print(f"Error processing evidence: {e}")
        bot.send_message(message.chat.id, "Terjadi kesalahan dalam memproses bukti. Silahkan coba lagi nanti.")

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
        bot.send_message(call.message.chat.id, "Terjadi kesalahan dalam memeriksa status pemblokiran. Silahkan coba lagi nanti.")

def search_message_in_channel(user_id, username):
    # Implementasi pencarian pesan dalam channel log
    return None

@bot.callback_query_handler(func=lambda call: call.data in ['rules_menu', 'back_to_start'])
def handle_buttons(call):
    try:
        if call.data == 'rules_menu':
            rules_text = (
                "<b><u>📜 Aturan Umum:</u></b>\n\n"
                "1. <b>Konten Negatif:</b> Dilarang menyebar rasisme, provokasi, atau konten negatif. <i>Tindakan:</i> <i>Ban.</i>\n\n"
                "2. <b>Konten Dewasa:</b> Dilarang membagikan konten 18+ termasuk link, foto, video, dan stiker. <i>Tindakan:</i> <i>Ban.</i>\n\n"
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
            bot.edit_message_text(rules_text,
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode='HTML',
                                  reply_markup=markup)
        elif call.data == 'back_to_start':
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            handle_start(call.message)

    except Exception as e:
        print(f"Error handling button callback: {e}")
        bot.send_message(call.message.chat.id, "Terjadi kesalahan dalam memproses tombol. Silahkan coba lagi nanti.")

# Jalankan bot
bot.polling()
