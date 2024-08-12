import os
import telebot
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
import json
import time
from telebot import types
import re
from telebot.apihelper import ApiTelegramException
import logging

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API = '7000129653:AAENjsi7v1NK0dQKO5Z10RmkNX3BiCL5AO0'
bot = telebot.TeleBot(API)
    
OWNER = 5991733650
user_history = {}

def get_admin_list():
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            return data.get('main_admin', [])
    except FileNotFoundError:
        print("File Administrator_All.json tidak ditemukan. Mengembalikan list kosong.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error saat membaca file JSON: {e}. Mengembalikan list kosong.")
        return []
    except Exception as e:
        print(f"Terjadi kesalahan tidak terduga: {e}. Mengembalikan list kosong.")
        return []

def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Selamat pagi"
    elif 12 <= current_hour < 15:
        return "Selamat siang"
    elif 15 <= current_hour < 18:
        return "Selamat sore"
    else:
        return "Selamat malam"

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "Mohon maaf, saya tidak akan merespon perintah ini dalam grup, dan hanya bisa digunakan dalam chat pribadi.")
        return
    
    user_id = message.from_user.id
    admin_list = get_admin_list()
    greeting = get_greeting()

    if user_id == OWNER:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("👥 Kelola Admin", callback_data="manage_admin"),
                     InlineKeyboardButton("🤖 Kelola Bot", callback_data="manage_bot"))
        keyboard.row(InlineKeyboardButton("⚙️ Kelola Fitur", callback_data="manage_feature"),
                     InlineKeyboardButton("📊 Laporan", callback_data="report"))
        keyboard.row(InlineKeyboardButton("⚙️ Pengaturan", callback_data="settings"))
        
        bot.reply_to(message, f"{greeting}, Owner!, Silahkan pilih menu yang ingin Anda akses.", reply_markup=keyboard)
        
    elif user_id in admin_list:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("📜 Rules", callback_data="rules"),
                     InlineKeyboardButton("📋 Log-Fban", url="https://t.me/LogTranssionIndonesia"))
        keyboard.row(InlineKeyboardButton("📊 Laporan", callback_data="report"))
        
        bot.reply_to(message, f"{greeting}, Admin Utama! 👋  Anda memiliki akses penuh ke panel kontrol bot. Silahkan pilih menu yang ingin Anda gunakan.", reply_markup=keyboard)
        
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("📜 Rules", callback_data="rules"),
                     InlineKeyboardButton("📢 Channel TFI", url="https://t.me/OfficialTFI"))
        keyboard.row(InlineKeyboardButton("📋 Log-Fban", url="https://t.me/LogTranssionIndonesia"),
                     InlineKeyboardButton("🚨 Report To Admin", callback_data="report_to_admin"))
        
        bot.reply_to(message, f"{greeting}, Baca aturan grup dengan menekan tombol 'Rules' jika Anda belum mengetahui rules/aturan.  Jika Anda ingin melaporkan pelanggaran aturan, silakan tekan tombol 'Report To Admin'.!", reply_markup=keyboard)

def get_bot_groups():
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            manual_groups = data.get('manual_groups', [])
        
        logging.info(f"Total grup yang disimpan: {len(manual_groups)}")
        return manual_groups
    except Exception as e:
        logging.error(f"Error saat mendapatkan daftar grup: {e}")
        return []

@bot.callback_query_handler(func=lambda call: call.data == "manage_bot")
def manage_bot_callback(call):
    try:
        groups = get_bot_groups()
        text = "Berikut grup yang dikelola oleh bot ini:\n\n"
        keyboard = InlineKeyboardMarkup()
        
        if not groups:
            text += "Tidak ada grup yang ditambahkan."
        else:
            for group in groups:
                text += f"• {group.get('name', 'Nama tidak tersedia')}\n"
                if 'link' in group and group['link']:
                    keyboard.row(InlineKeyboardButton(group['name'], url=group['link']))
                else:
                    keyboard.row(InlineKeyboardButton(group.get('name', 'Nama tidak tersedia'), callback_data=f"no_link_{group.get('name', 'unknown')}"))
        
        keyboard.row(InlineKeyboardButton("➕ Add Grup", callback_data="add_group_manual"))
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat menampilkan daftar grup: {e}")
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat menampilkan daftar grup.")
        bot.send_message(call.message.chat.id, f"Maaf, terjadi kesalahan: {str(e)}. Silakan coba lagi nanti.")

@bot.callback_query_handler(func=lambda call: call.data == "add_group_manual")
def add_group_manual_callback(call):
    bot.answer_callback_query(call.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_add_group"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Silakan kirim informasi grup dalam format:\n"
             "Nama Grup | Link Grup\n\n"
             "Contoh: Nama Grub | https://t.me/LinkGrub\n\n"
             "Jika tidak ada link, cukup kirim nama grup saja.",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(call.message, process_add_group_manual)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_add_group")
def cancel_add_group(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.answer_callback_query(call.id)
    manage_bot_callback(call)

def process_add_group_manual(message):
    try:
        input_text = message.text.strip()
        parts = input_text.split('|')
        
        if len(parts) == 2:
            name = parts[0].strip()
            link = parts[1].strip()
        elif len(parts) == 1:
            name = parts[0].strip()
            link = None
        else:
            raise ValueError("Format tidak valid. Gunakan: 'Nama Grup | Link' atau 'Nama Grup'")
        
        new_group = {'name': name, 'link': link}
        
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            if 'manual_groups' not in data:
                data['manual_groups'] = []
            if not any(group['name'] == name for group in data['manual_groups']):
                data['manual_groups'].append(new_group)
                file.seek(0)
                json.dump(data, file, indent=2)
                file.truncate()
                
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton("🔙 Kembali ke Kelola Bot", callback_data="manage_bot"))
                
                if link:
                    confirmation_text = f"Oke👌 Saya sudah menambahkan [{name}]({link}) dalam daftar grup."
                else:
                    confirmation_text = f"Oke👌 Saya sudah menambahkan {name} dalam daftar grup."
                
                bot.send_message(
                    chat_id=message.chat.id,
                    text=confirmation_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(message.chat.id, f"Grup '{name}' sudah ada dalam daftar.")
    except ValueError as e:
        bot.send_message(message.chat.id, str(e))
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan saat menambahkan grup: {str(e)}")
    finally:
        try:
            bot.delete_message(message.chat.id, message.message_id - 1)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("no_link_"))
def no_link_callback(call):
    group_name = call.data.split("_", 2)[2]
    bot.answer_callback_query(call.id, text=f"Maaf, tidak ada link tersedia untuk grup {group_name}.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "manage_admin":
        manage_admin_callback(call)
    elif call.data == "add_admin":
        add_admin_callback(call)
    elif call.data == "remove_admin":
        remove_admin_callback(call)
    elif call.data == "cancel_add_admin":
        cancel_add_admin(call)
    elif call.data == "back_to_main":
        send_owner_menu(call.message)
    elif call.data.startswith("remove_admin_"):
        remove_specific_admin(call)
    elif call.data == "back_to_manage_admin":
        manage_admin_callback(call)
    elif call.data == "manage_bot":
        manage_bot_callback(call)
    elif call.data.startswith("no_link_"):
        no_link_callback(call)
    elif call.data == "manage_feature":
        manage_feature_callback(call)
    elif call.data == "edit_rules":
        edit_rules_callback(call)
    elif call.data == "set_rules":
        set_rules_callback(call)
    elif call.data == "cancel_set_rules":
        cancel_set_rules(call)
    elif call.data == "check_rules":
        check_rules_callback(call)
    elif call.data == "rules":
        rules_callback(call)
    elif call.data in ["rules_on", "rules_off"]:
        toggle_rules_status(call)
    elif call.data == "back_to_main_admin":
        send_main_admin_menu(call.message)
    elif call.data == "back_to_owner":
        send_owner_menu(call.message)
    elif call.data == "back_to_user":
        send_user_menu(call.message)
    elif call.data == "rules_on_group":
        rules_on_group_callback(call)
    elif call.data in ["rules_group_on", "rules_group_off"]:
        toggle_rules_group_status(call)
    elif call.data == "rules":
        show_rules_command(call.message)
    elif call.data == "clean_rules_on_group":
        clean_rules_on_group_callback(call)
    elif call.data in ["clean_rules_group_on", "clean_rules_group_off"]:
        toggle_clean_rules_group_status(call)
    elif call.data.startswith("clean_rules_"):
        clean_rules_callback(call)
    elif call.data == "edit_mute":
        edit_mute_callback(call)
    elif call.data in ["mute_on", "mute_off"]:
        toggle_mute_status(call)
    elif call.data == "mute_group_on":
        toggle_mute_group_status(call)
    elif call.data == "mute_group_off":
        toggle_mute_group_status(call)
    elif call.data == "edit_mute_minutes":
        edit_mute_minutes_callback(call)
    elif call.data in ["mute_minutes_on", "mute_minutes_off"]:
        toggle_mute_minutes_status(call)
    elif call.data == "report_to_admin":
        report_to_admin_callback(call)
    elif call.data.startswith("report_option_"):
        handle_report_option(call)
    elif call.data == "cancel_report":
        cancel_report(call)
    elif call.data == "report":
        show_reports(call)
    elif call.data.startswith("next_report_") or call.data.startswith("prev_report_"):
        navigate_reports(call)
    elif call.data == "back_to_owner":
        send_owner_menu(call.message)
    elif call.data.startswith("report_") and call.data != "report_cancel":
        handle_report_button(call)
    elif call.data == "report_cancel":
        cancel_report(call)

def manage_admin(message):
    admin_list = get_admin_list()
    admin_text = "Berikut daftar Admin Utama dalam Transsion Federation Indonesia:\n"
    for i, admin in enumerate(admin_list, 1):
        admin_text += f"{i}. {admin}\n"
    
    admin_text += "\nSilahkan pilih opsi menu untuk mengelola Daftar Admin Utama"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
                 InlineKeyboardButton("➖ Remove Admin", callback_data="remove_admin"))
    keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main"))
    
    return admin_text, keyboard

@bot.callback_query_handler(func=lambda call: call.data == "manage_admin")
def manage_admin_callback(call):
    try:
        admin_text, keyboard = manage_admin(call.message)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=admin_text,
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengelola admin.")
        bot.send_message(call.message.chat.id, f"Terjadi kesalahan saat mengelola admin: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "add_admin")
def add_admin_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_add_admin"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Silakan kirim ID User untuk menambahkan dalam daftar Admin Utama.",
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler(call.message, process_add_admin)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_add_admin")
def cancel_add_admin(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.answer_callback_query(call.id)
    admin_text, keyboard = manage_admin(call.message)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=admin_text,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "remove_admin")
def remove_admin_callback(call):
    admin_list = get_admin_list()
    keyboard = InlineKeyboardMarkup()
    
    for admin_id in admin_list:
        keyboard.row(InlineKeyboardButton(f"Hapus Admin {admin_id}", callback_data=f"remove_admin_{admin_id}"))
    
    keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_manage_admin"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Silakan pilih ID admin mana yang ingin dihapus:",
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

def remove_specific_admin(call):
    admin_to_remove = int(call.data.split("_")[-1])
    try:
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            if 'main_admin' in data and admin_to_remove in data['main_admin']:
                data['main_admin'].remove(admin_to_remove)
                file.seek(0)
                json.dump(data, file, indent=2)
                file.truncate()
                
                bot.answer_callback_query(call.id, text=f"Admin {admin_to_remove} berhasil dihapus.")
                
                manage_admin_callback(call)
            else:
                bot.answer_callback_query(call.id, text="Admin tidak ditemukan dalam daftar.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat menghapus admin.")
        bot.send_message(call.message.chat.id, f"Terjadi kesalahan: {str(e)}")

def process_add_admin(message):
    try:
        new_admin_id = int(message.text)
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            if 'main_admin' not in data:
                data['main_admin'] = []
            if new_admin_id not in data['main_admin']:
                data['main_admin'].append(new_admin_id)
                file.seek(0)
                json.dump(data, file, indent=2)
                file.truncate()
                
                admin_list = data['main_admin']
                admin_text = "Berikut daftar Admin Utama dalam Transsion Federation Indonesia:\n"
                for i, admin in enumerate(admin_list, 1):
                    admin_text += f"{i}. {admin}\n"
                
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton("🔙 Kembali ke Kelola Admin", callback_data="manage_admin"))
                
                confirmation_text = f"Sip, saya sudah menambahkan ID {new_admin_id} dalam daftar Admin Utama.\n\n{admin_text}"
                
                bot.delete_message(message.chat.id, message.message_id - 1)
                
                bot.send_message(
                    chat_id=message.chat.id,
                    text=confirmation_text,
                    reply_markup=keyboard
                )
            else:
                bot.send_message(message.chat.id, "ID ini sudah terdaftar sebagai admin.")
    except ValueError:
        bot.send_message(message.chat.id, "Mohon masukkan ID yang valid (angka).")
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")
    finally:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

def send_owner_menu(message):
    greeting = get_greeting()
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("👥 Kelola Admin", callback_data="manage_admin"),
                 InlineKeyboardButton("🤖 Kelola Bot", callback_data="manage_bot"))
    keyboard.row(InlineKeyboardButton("⚙️ Kelola Fitur", callback_data="manage_feature"),
                 InlineKeyboardButton("📊 Laporan", callback_data="report"))
    keyboard.row(InlineKeyboardButton("⚙️ Pengaturan", callback_data="settings"))
    
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=f"{greeting}, Owner!, Silahkan pilih menu yang ingin Anda akses.",
                          reply_markup=keyboard)

def get_user_status(chat_id, user_id):
    if user_id == OWNER:
        return "owner"
    if user_id in get_admin_list():
        return "main_admin"
    member = bot.get_chat_member(chat_id, user_id)
    if member.status in ['administrator', 'creator']:
        return "admin_grup"
    return "member"

def toggle_mute_status(call):
    try:
        new_status = 'on' if call.data == "mute_on" else 'off'
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['mute_status'] = new_status
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        edit_mute_callback(call)
        bot.answer_callback_query(call.id, text=f"Status Mute telah diubah menjadi {new_status.upper()}.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengubah status Mute.")
        logging.error(f"Terjadi kesalahan saat mengubah status Mute: {str(e)}")

@bot.message_handler(commands=['m'])
def mute_user(message):
    chat_id = message.chat.id
    admin_id = message.from_user.id
    admin_status = get_user_status(chat_id, admin_id)

    if admin_status not in ["owner", "main_admin", "admin_grup"]:
        bot.reply_to(message, "Anda tidak memiliki izin untuk melakukan tindakan ini.")
        return

    with open('Administrator_All.json', 'r') as file:
        data = json.load(file)
        mute_status = data.get('mute_status', 'off')

    if mute_status == 'off':
        bot.reply_to(message, "Perintah Mute sedang dinonaktifkan.")
        return

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.first_name
    else:
        command_args = message.text.split()[1:]
        if not command_args:
            bot.reply_to(message, "Silakan gunakan format: /m ID atau balas pesan pengguna yang ingin di-mute.")
            return
        
        try:
            user_id = int(command_args[0])
            chat_member = bot.get_chat_member(chat_id, user_id)
            user_name = chat_member.user.first_name
        except ValueError:
            bot.reply_to(message, "ID pengguna tidak valid. Gunakan angka untuk ID.")
            return
        except ApiTelegramException as e:
            bot.reply_to(message, f"Tidak dapat menemukan pengguna dengan ID {user_id}")
            return

    try:
        bot.restrict_chat_member(chat_id, user_id, ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        ))

        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            if 'mute_user' not in data or not isinstance(data['mute_user'], list):
                data['mute_user'] = []
            str_user_id = str(user_id)
            if str_user_id not in data['mute_user']:
                data['mute_user'].append(str_user_id)
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        bot.reply_to(message, f"Pengguna {user_name} telah di-mute.")
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan saat mute pengguna: {str(e)}")

@bot.message_handler(commands=['um'])
def unmute_user(message):
    chat_id = message.chat.id
    admin_id = message.from_user.id
    admin_status = get_user_status(chat_id, admin_id)

    if admin_status not in ["owner", "main_admin", "admin_grup"]:
        bot.reply_to(message, "Anda tidak memiliki izin untuk melakukan tindakan ini.")
        return

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.first_name
    else:
        command_args = message.text.split()[1:]
        if not command_args:
            bot.reply_to(message, "Silakan gunakan format: /um ID atau balas pesan pengguna yang ingin di-unmute.")
            return
        
        try:
            user_id = int(command_args[0])
            chat_member = bot.get_chat_member(chat_id, user_id)
            user_name = chat_member.user.first_name
        except ValueError:
            bot.reply_to(message, "ID pengguna tidak valid. Gunakan angka untuk ID.")
            return
        except ApiTelegramException as e:
            bot.reply_to(message, f"Tidak dapat menemukan pengguna dengan ID {user_id}")
            return

    try:
        chat_permissions = bot.get_chat(chat_id).permissions

        bot.restrict_chat_member(
            chat_id, 
            user_id, 
            permissions=chat_permissions
        )

        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            if 'mute_user' in data and isinstance(data['mute_user'], list):
                str_user_id = str(user_id)
                if str_user_id in data['mute_user']:
                    data['mute_user'].remove(str_user_id)
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        bot.reply_to(message, f"Pengguna {user_name} telah di-unmute.")
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan saat unmute pengguna: {str(e)}")
        logging.error(f"Error saat unmute pengguna: {str(e)}")

def manage_feature_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("📜 Rules", callback_data="edit_rules"),
                 InlineKeyboardButton("🔇 Mute", callback_data="edit_mute"))
    keyboard.row(InlineKeyboardButton("⏱ Mute with Minutes", callback_data="edit_mute_minutes"))
    keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Silakan pilih opsi menu untuk mengelola fitur:",
        reply_markup=keyboard
    )

def edit_rules_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("✏️ Set Rules", callback_data="set_rules"),
                 InlineKeyboardButton("👀 Cek Rules", callback_data="check_rules"))
    keyboard.row(InlineKeyboardButton("📢 Rules on Grup", callback_data="rules_on_group"),
                 InlineKeyboardButton("🧹 Clean Rules on Grup", callback_data="clean_rules_on_group"))
    keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="manage_feature"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Pilih opsi menu untuk mengatur rules:",
        reply_markup=keyboard
    )

def set_rules_callback(call):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_set_rules"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Silakan kirim teks rules untuk ᴛғɪ | ᴛʀᴀɴssɪᴏɴ ғᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴᴅᴏɴᴇsɪᴀ 🇮🇩.",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(call.message, process_set_rules)

def process_set_rules(message):
    try:
        new_rules = message.text.strip()
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['rules'] = new_rules
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("✏️ Set Rules", callback_data="set_rules"),
                     InlineKeyboardButton("👀 Cek Rules", callback_data="check_rules"))
        keyboard.row(InlineKeyboardButton("📢 Rules on Grup", callback_data="rules_on_group"),
                     InlineKeyboardButton("🧹 Clean Rules on Grup", callback_data="clean_rules_on_group"))
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="manage_feature"))
        
        confirmation_text = "Sip, Saya sudah meng-update Rules. Silakan pilih opsi menu untuk mengatur rules:"
        
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id - 1,
                text=confirmation_text,
                reply_markup=keyboard
            )
        except ApiTelegramException as e:
            if e.error_code == 400:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=confirmation_text,
                    reply_markup=keyboard
                )
            else:
                raise e
        
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan saat menyimpan rules: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_set_rules")
def cancel_set_rules(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.answer_callback_query(call.id)
    
    edit_rules_callback(call)

def check_rules_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            rules = data.get('rules', 'Belum ada rules yang disimpan.')

        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="edit_rules"))

        text = f"Berikut Rules ᴛғɪ | ᴛʀᴀɴssɪᴏɴ ғᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴᴅᴏɴᴇsɪᴀ 🇮🇩 untuk saat ini:\n\n{rules}"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengambil rules.")
        logging.error(f"Terjadi kesalahan saat mengambil rules: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "rules")
def rules_callback(call):
    try:
        user_id = call.from_user.id
        admin_list = get_admin_list()

        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            rules = data.get('rules', 'Belum ada rules yang disimpan.')
            rules_status = data.get('rules_status', 'off')

        if user_id == OWNER:
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("✏️ Set Rules", callback_data="set_rules"),
                         InlineKeyboardButton("👀 Cek Rules", callback_data="check_rules"))
            keyboard.row(InlineKeyboardButton("📢 Rules on Grup", callback_data="rules_on_group"),
                         InlineKeyboardButton("🧹 Clean Rules on Grup", callback_data="clean_rules_on_group"))
            keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="manage_feature"))
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Pilih opsi menu untuk mengatur rules:",
                reply_markup=keyboard
            )
        elif user_id in admin_list:
            text = f"Berikut Rules ᴛғɪ | ᴛʀᴀɴssɪᴏɴ ғᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴᴅᴏɴᴇsɪᴀ 🇮🇩 untuk saat ini:\n\n{rules}"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main_admin"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=keyboard
            )
        else:
            text = f"Berikut Rules ᴛғɪ | ᴛʀᴀɴssɪᴏɴ ғᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴᴅᴏɴᴇsɪᴀ 🇮🇩:\n\n{rules}"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_user"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=keyboard
            )

        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat menampilkan rules.")
        logging.error(f"Terjadi kesalahan saat menampilkan rules: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_user")
def back_to_user_callback(call):
    try:
        send_user_menu(call.message)
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat kembali ke menu utama.")
        logging.error(f"Terjadi kesalahan saat kembali ke menu utama: {str(e)}")

def send_user_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("📜 Rules", callback_data="rules"),
                 InlineKeyboardButton("📢 Channel TFI", url="https://t.me/OfficialTFI"))
    keyboard.row(InlineKeyboardButton("📋 Log-Fban", url="https://t.me/LogTranssionIndonesia"),
                 InlineKeyboardButton("🚨 Report To Admin", callback_data="report_to_admin"))
    
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"{get_greeting()}!",
        reply_markup=keyboard
    )

def rules_menu_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            rules_status = data.get('rules_status', 'off')

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🟢 On" if rules_status == 'on' else "On", callback_data="rules_on"),
            InlineKeyboardButton("🔴 Off" if rules_status == 'off' else "Off", callback_data="rules_off")
        )
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main"))

        text = "Silakan pilih opsi menu Aktifkan / Nonaktifkan perintah Rules dalam grup:"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat memuat menu Rules.")
        logging.error(f"Terjadi kesalahan saat memuat menu Rules: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data in ["rules_on", "rules_off"])
def toggle_rules_status(call):
    try:
        new_status = 'on' if call.data == "rules_on" else 'off'
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['rules_status'] = new_status
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        rules_menu_callback(call)
        bot.answer_callback_query(call.id, text=f"Status Rules telah diubah menjadi {new_status.upper()}")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengubah status Rules.")
        logging.error(f"Terjadi kesalahan saat mengubah status Rules: {str(e)}")

def send_main_admin_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("📜 Rules", callback_data="rules"),
                 InlineKeyboardButton("📋 Log-Fban", callback_data="log_fban"))
    keyboard.row(InlineKeyboardButton("📊 Laporan", callback_data="report"))
    
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"{get_greeting()}, Admin Utama! 👋  Anda memiliki akses penuh ke panel kontrol bot. Silahkan pilih menu yang ingin Anda gunakan.",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "rules_on_group")
def rules_on_group_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            rules_status = data.get('rules_status', 'off')

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🟢 On" if rules_status == 'on' else "On", callback_data="rules_group_on"),
            InlineKeyboardButton("🔴 Off" if rules_status == 'off' else "Off", callback_data="rules_group_off")
        )
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="edit_rules"))

        text = "Silakan pilih opsi menu Aktifkan / Nonaktifkan perintah /rules dalam grup:"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat memuat menu Rules on Grup.")
        logging.error(f"Terjadi kesalahan saat memuat menu Rules on Grup: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data in ["rules_group_on", "rules_group_off"])
def toggle_rules_group_status(call):
    try:
        new_status = 'on' if call.data == "rules_group_on" else 'off'
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['rules_status'] = new_status
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        rules_on_group_callback(call)
        bot.answer_callback_query(call.id, text=f"Perintah /rules dalam grup telah {new_status.upper()}.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengubah status Rules dalam grup.")
        logging.error(f"Terjadi kesalahan saat mengubah status Rules dalam grup: {str(e)}")

@bot.message_handler(commands=['rules'])
def show_rules_command(message):
    try:
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "Perintah ini hanya dapat digunakan dalam grup.")
            return

        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            rules_status = data.get('rules_status', 'off')
            clean_rules_status = data.get('clean_rules_status', 'off')

        if rules_status == 'off':
            bot.reply_to(message, "Perintah Rules sedang dinonaktifkan.")
            return

        rules = data.get('rules', 'Belum ada rules yang disimpan.')

        text = f"Berikut Rules ᴛғɪ | ᴛʀᴀɴssɪᴏɴ ғᴇᴅᴇʀᴀᴛɪᴏɴ ɪɴᴅᴏɴᴇsɪᴀ 🇮🇩 untuk saat ini:\n\n{rules}"
        
        keyboard = InlineKeyboardMarkup()
        if clean_rules_status == 'on':
            keyboard.row(InlineKeyboardButton("🧹 Clean", callback_data=f"clean_rules_{message.message_id}"))
        
        sent_message = bot.reply_to(message, text, reply_markup=keyboard)

        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['last_rules_message_id'] = sent_message.message_id
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

    except Exception as e:
        bot.reply_to(message, "Terjadi kesalahan saat menampilkan rules.")
        logging.error(f"Terjadi kesalahan saat menampilkan rules: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("clean_rules_"))
def clean_rules_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            clean_rules_status = data.get('clean_rules_status', 'off')

        if clean_rules_status == 'off':
            bot.answer_callback_query(call.id, text="Fitur Clean Rules sedang dinonaktifkan.")
            return

        bot.delete_message(call.message.chat.id, call.message.message_id)

        trigger_message_id = int(call.data.split('_')[-1])
        bot.delete_message(call.message.chat.id, trigger_message_id)

        bot.answer_callback_query(call.id, text="Rules telah dibersihkan.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat membersihkan rules.")
        logging.error(f"Terjadi kesalahan saat membersihkan rules: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "clean_rules_on_group")
def clean_rules_on_group_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            clean_rules_status = data.get('clean_rules_status', 'off')

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🟢 On" if clean_rules_status == 'on' else "On", callback_data="clean_rules_group_on"),
            InlineKeyboardButton("🔴 Off" if clean_rules_status == 'off' else "Off", callback_data="clean_rules_group_off")
        )
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="edit_rules"))

        text = "Silakan pilih opsi menu untuk Aktifkan / Nonaktifkan Clean Rules dalam grup:"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat memuat menu Clean Rules on Grup.")
        logging.error(f"Terjadi kesalahan saat memuat menu Clean Rules on Grup: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data in ["clean_rules_group_on", "clean_rules_group_off"])
def toggle_clean_rules_group_status(call):
    try:
        new_status = 'on' if call.data == "clean_rules_group_on" else 'off'
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['clean_rules_status'] = new_status
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        clean_rules_on_group_callback(call)
        bot.answer_callback_query(call.id, text=f"Clean Rules dalam grup telah {new_status.upper()}.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengubah status Clean Rules dalam grup.")
        logging.error(f"Terjadi kesalahan saat mengubah status Clean Rules dalam grup: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "edit_mute")
def edit_mute_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            mute_status = data.get('mute_status', 'off')

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🟢 On" if mute_status == 'on' else "On", callback_data="mute_group_on"),
            InlineKeyboardButton("🔴 Off" if mute_status == 'off' else "Off", callback_data="mute_group_off")
        )
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="manage_feature"))

        text = "Silakan pilih opsi menu untuk Aktifkan / Nonaktifkan perintah /mute dalam grup:"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat memuat menu Mute.")
        logging.error(f"Terjadi kesalahan saat memuat menu Mute: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data in ["mute_group_on", "mute_group_off"])
def toggle_mute_group_status(call):
    try:
        new_status = 'on' if call.data == "mute_group_on" else 'off'
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['mute_status'] = new_status
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        edit_mute_callback(call)
        bot.answer_callback_query(call.id, text=f"Perintah /mute dalam grup telah {new_status.upper()}.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengubah status Mute dalam grup.")
        logging.error(f"Terjadi kesalahan saat mengubah status Mute dalam grup: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "edit_mute_minutes")
def edit_mute_minutes_callback(call):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
            mute_minutes_status = data.get('mute_minutes_status', 'off')

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🟢 On" if mute_minutes_status == 'on' else "On", callback_data="mute_minutes_on"),
            InlineKeyboardButton("🔴 Off" if mute_minutes_status == 'off' else "Off", callback_data="mute_minutes_off")
        )
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="manage_feature"))

        text = "Silakan pilih opsi menu untuk Aktifkan / Nonaktifkan perintah /mute dengan durasi dalam menit:"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat memuat menu Mute with Minutes.")
        logging.error(f"Terjadi kesalahan saat memuat menu Mute with Minutes: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data in ["mute_minutes_on", "mute_minutes_off"])
def toggle_mute_minutes_status(call):
    try:
        new_status = 'on' if call.data == "mute_minutes_on" else 'off'
        with open('Administrator_All.json', 'r+') as file:
            data = json.load(file)
            data['mute_minutes_status'] = new_status
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        edit_mute_minutes_callback(call)
        bot.answer_callback_query(call.id, text=f"Perintah /mute dengan durasi dalam menit telah {new_status.upper()}.")
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat mengubah status Mute with Minutes.")
        logging.error(f"Terjadi kesalahan saat mengubah status Mute with Minutes: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "report_to_admin")
def report_to_admin_callback(call):
    try:
        keyboard = InlineKeyboardMarkup(row_width=2)
        report_options = [
            "Spam", "Scam", "Porn", "Racis", 
            "Judi/Gambling", "Promotion", "Pishing", 
            "Cheat", "Rusuh/Riot", "HakCipta/Kanger", 
            "Other"
        ]
        buttons = [InlineKeyboardButton(option, callback_data=f"report_option_{option}") for option in report_options]
        keyboard.add(*buttons)
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_user"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Silakan pilih menu laporan yang ingin Anda laporkan:",
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat membuka menu Report to Admin.")
        logging.error(f"Terjadi kesalahan saat membuka menu Report to Admin: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("report_option_"))
def handle_report_option(call):
    try:
        option = call.data.split("_")[2]
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_report"))
        
        new_text = (f"Anda memilih untuk melaporkan '{option}'.\n\n"
                    "Silakan balas dengan pesan, pesan terusan, foto / video sebagai bukti laporan Anda.")
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=new_text,
            reply_markup=keyboard
        )
        
        bot.answer_callback_query(call.id, text=f"Anda memilih untuk melaporkan {option}")
        bot.register_next_step_handler(call.message, process_report_evidence, option)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat memproses pilihan laporan.")
        logging.error(f"Terjadi kesalahan saat memproses pilihan laporan: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_report")
def cancel_report(call):
    try:
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id)
        send_user_menu(call.message)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat membatalkan laporan.")
        logging.error(f"Terjadi kesalahan saat membatalkan laporan: {str(e)}")

def process_report_evidence(message, report_type):
    try:
        if message.content_type == 'text' and message.text == '/start':
            bot.send_message(message.chat.id, "Proses pelaporan dibatalkan.")
            return

        evidence = None
        evidence_type = None

        if message.forward_from or message.forward_from_chat:
            evidence = message.text or "Pesan Terusan"
            evidence_type = "Pesan Terusan"
        elif message.photo:
            evidence = message.photo[-1].file_id
            evidence_type = "Foto"
        elif message.video:
            evidence = message.video.file_id
            evidence_type = "Video"
        elif message.text:
            evidence = message.text
            evidence_type = "Pesan"
        else:
            bot.reply_to(message, "Mohon kirim bukti berupa pesan, pesan terusan, foto, atau video.")
            return

        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_report"))

        new_text = ("Sip, Tolong sertakan ID dan Username dengan format sebagai berikut:\n"
                    "ID: (id yang dilaporkan)\n"
                    "Username: (username yang dilaporkan)")

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        sent_message = bot.send_message(
            chat_id=message.chat.id,
            text=new_text,
            reply_markup=keyboard
        )

        bot.register_next_step_handler(sent_message, process_report_details, report_type, evidence, evidence_type)
    except AttributeError:
        bot.send_message(message.chat.id, "Pesan tidak valid atau telah dihapus. Silakan mulai proses pelaporan dari awal.")
        return
    except Exception as e:
        bot.send_message(message.chat.id, "Terjadi kesalahan saat memproses bukti laporan.")
        logging.error(f"Terjadi kesalahan saat memproses bukti laporan: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_report_options")
def back_to_report_options(call):
    try:
        keyboard = InlineKeyboardMarkup(row_width=2)
        report_options = [
            "Spam", "Scam", "Porn", "Racis", 
            "Judi/Gambling", "Promotion", "Pishing", 
            "Cheat", "Rusuh/Riot", "Hak Cipta/Kanger", 
            "Other"
        ]
        buttons = [InlineKeyboardButton(option, callback_data=f"report_option_{option}") for option in report_options]
        keyboard.add(*buttons)
        keyboard.row(InlineKeyboardButton("🔙 Kembali", callback_data="back_to_report_options"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Silakan pilih menu laporan yang ingin Anda laporkan:",
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.answer_callback_query(call.id, text="Terjadi kesalahan saat kembali ke menu laporan.")
        logging.error(f"Terjadi kesalahan saat kembali ke menu laporan: {str(e)}")

def notify_admins(report_type):
    try:
        with open('Administrator_All.json', 'r') as file:
            data = json.load(file)
        
        owner_id = OWNER
        main_admin_list = data.get('main_admin', [])
        
        recipients = [owner_id] + main_admin_list
        
        for admin_id in recipients:
            try:
                bot.send_message(admin_id, f"Laporan Baru ({report_type}). Cek di menu laporan untuk selengkapnya.")
            except Exception as e:
                logging.error(f"Gagal mengirim notifikasi ke admin {admin_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat membaca data admin: {str(e)}")

def process_report_details(message, report_type, evidence, evidence_type):
    try:
        if message.content_type == 'text' and message.text == '/start':
            bot.send_message(message.chat.id, "Proses pelaporan dibatalkan.")
            return

        report_text = message.text
        user_id = message.from_user.id

        reported_id = None
        reported_username = None
        for line in report_text.split('\n'):
            if line.startswith("ID:"):
                reported_id = line.split(":", 1)[1].strip()
            elif line.startswith("Username:"):
                reported_username = line.split(":", 1)[1].strip()

        if not reported_id or not reported_username:
            bot.reply_to(message, "Format ID dan Username tidak valid. Mohon kirim ulang dengan format yang benar.")
            bot.register_next_step_handler(message, process_report_details, report_type, evidence, evidence_type)
            return

        updated_text = (f"Detail Laporan: {evidence_type}\n"
                        f"Type: {report_type}\n"
                        f"ID: {reported_id}\n"
                        f"Username: {reported_username}\n\n"
                        "Laporan anda diterima. Saya akan mengirimkan laporan ini kepada Admin.")

        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🔙 Kembali ke Menu Utama", callback_data="back_to_user"))

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.send_message(
            chat_id=message.chat.id,
            text=updated_text,
            reply_markup=keyboard
        )

        save_report(report_type, reported_id, reported_username, evidence, evidence_type, user_id)
        notify_admins(report_type)
    except AttributeError:
        bot.send_message(message.chat.id, "Pesan tidak valid atau telah dihapus. Silakan mulai proses pelaporan dari awal.")
        return
    except Exception as e:
        bot.reply_to(message, "Terjadi kesalahan saat memproses laporan.")
        logging.error(f"Terjadi kesalahan saat memproses laporan: {str(e)}")

def save_report(report_type, reported_id, reported_username, evidence, evidence_type, reporter_id):
    try:
        try:
            with open('reports.json', 'r') as file:
                reports = json.load(file)
                if not isinstance(reports, list):
                    reports = []
        except (FileNotFoundError, json.JSONDecodeError):
            reports = []

        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M - %A, %d %B %Y")

        new_report = {
            "type": report_type,
            "evidence": evidence,
            "evidence_type": evidence_type,
            "reported_id": reported_id,
            "reported_username": reported_username,
            "reporter_id": reporter_id,
            "timestamp": formatted_time
        }

        reports.append(new_report)

        with open('reports.json', 'w') as file:
            json.dump(reports, file, indent=2)
        
        logging.info(f"Laporan baru disimpan. Total laporan: {len(reports)}")
        logging.info(f"Isi laporan baru: {json.dumps(new_report, indent=2)}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat menyimpan laporan: {str(e)}")
        with open('failed_reports.json', 'a') as file:
            json.dump(new_report, file)
            file.write('\n')
            
@bot.callback_query_handler(func=lambda call: call.data == "report")
def show_reports(call):
    try:
        with open('reports.json', 'r') as file:
            reports = json.load(file)
            if not isinstance(reports, list):
                reports = []
        
        if not reports:
            bot.answer_callback_query(call.id, "Tidak ada laporan saat ini.")
            return

        show_reports_by_index(call, 0, edit_message=True)
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat menampilkan laporan: {str(e)}")
        bot.answer_callback_query(call.id, "Terjadi kesalahan saat menampilkan laporan.")

def show_reports_by_index(call, index, edit_message=False):
    try:
        with open('reports.json', 'r') as file:
            reports = json.load(file)

        if index >= len(reports) or index < 0:
            bot.answer_callback_query(call.id, "Tidak ada laporan lagi.")
            return

        report = reports[index]
        formatted_time = report['timestamp']

        report_text = f"Laporan #{index + 1} dari {len(reports)}:\n"
        report_text += f"Type: {report['type']}\n"
        report_text += f"ID: {report['reported_id']}\n"
        report_text += f"Username: {report['reported_username']}\n"
        report_text += f"Waktu laporan: {formatted_time}\n\n"
        report_text += "Detail Laporan:"

        keyboard = InlineKeyboardMarkup()
        
        if index == 0:
            user_id = call.from_user.id
            if user_id == OWNER:
                back_callback = "back_to_owner"
            else:
                back_callback = "back_to_main_admin"
            keyboard.row(InlineKeyboardButton("🔙 Kembali ke Menu Utama", callback_data=back_callback))
            
            if len(reports) > 1:
                keyboard.row(InlineKeyboardButton("Berikutnya ➡️", callback_data=f"next_report_1"))
        else:
            nav_buttons = []
            nav_buttons.append(InlineKeyboardButton("⬅️ Sebelumnya", callback_data=f"prev_report_{index - 1}"))
            if index < len(reports) - 1:
                nav_buttons.append(InlineKeyboardButton("Berikutnya ➡️", callback_data=f"next_report_{index + 1}"))
            keyboard.row(*nav_buttons)

        if report['evidence_type'] in ['Foto', 'Video']:
            media_type = types.InputMediaPhoto if report['evidence_type'] == 'Foto' else types.InputMediaVideo
            if edit_message:
                try:
                    bot.edit_message_media(
                        media=media_type(report['evidence'], caption=report_text),
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=keyboard
                    )
                except ApiTelegramException:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    if report['evidence_type'] == 'Foto':
                        bot.send_photo(
                            chat_id=call.message.chat.id,
                            photo=report['evidence'],
                            caption=report_text,
                            reply_markup=keyboard
                        )
                    else:
                        bot.send_video(
                            chat_id=call.message.chat.id,
                            video=report['evidence'],
                            caption=report_text,
                            reply_markup=keyboard
                        )
            else:
                if report['evidence_type'] == 'Foto':
                    bot.send_photo(
                        chat_id=call.message.chat.id,
                        photo=report['evidence'],
                        caption=report_text,
                        reply_markup=keyboard
                    )
                else:
                    bot.send_video(
                        chat_id=call.message.chat.id,
                        video=report['evidence'],
                        caption=report_text,
                        reply_markup=keyboard
                    )
        else:
            full_text = f"{report_text}\n\n{report['evidence']}"
            if edit_message:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=full_text,
                        reply_markup=keyboard
                    )
                except ApiTelegramException:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(
                        chat_id=call.message.chat.id,
                        text=full_text,
                        reply_markup=keyboard
                    )
            else:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=full_text,
                    reply_markup=keyboard
                )
        
        logging.info(f"Berhasil menampilkan laporan index: {index}")
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat menampilkan laporan: {str(e)}")
        bot.answer_callback_query(call.id, "Terjadi kesalahan saat menampilkan laporan.")
                
@bot.callback_query_handler(func=lambda call: call.data.startswith("next_report_") or call.data.startswith("prev_report_"))
def navigate_reports(call):
    try:
        logging.info(f"Navigasi laporan dipanggil dengan data: {call.data}")
        _, _, index = call.data.split("_")
        index = int(index)
        logging.info(f"Navigasi ke laporan index: {index}")
        show_reports_by_index(call, index, edit_message=True)
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat navigasi laporan: {str(e)}")
        bot.answer_callback_query(call.id, "Terjadi kesalahan saat navigasi laporan.")

def track_user_changes(user):
    user_id = user.id
    current_time = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    
    if user_id not in user_history:
        user_history[user_id] = {
            'create_time': current_time,
            'names': [],
            'usernames': []
        }
    
    last_name = user_history[user_id]['names'][-1] if user_history[user_id]['names'] else None
    last_username = user_history[user_id]['usernames'][-1] if user_history[user_id]['usernames'] else None
    
    if not last_name or user.first_name != last_name['name']:
        user_history[user_id]['names'].append({
            'time': current_time,
            'name': user.first_name
        })
    
    if not last_username or user.username != last_username['username']:
        user_history[user_id]['usernames'].append({
            'time': current_time,
            'username': user.username
        })

@bot.message_handler(commands=['uh'])
def user_history_command(message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        command_args = message.text.split()[1:]
        if not command_args:
            bot.reply_to(message, "Silakan gunakan format: /uh [ID] atau balas pesan pengguna.")
            return
        try:
            user_id = int(command_args[0])
            user = bot.get_chat_member(message.chat.id, user_id).user
        except ValueError:
            bot.reply_to(message, "ID pengguna tidak valid. Gunakan angka untuk ID.")
            return
        except telebot.apihelper.ApiException:
            bot.reply_to(message, "Pengguna tidak ditemukan.")
            return

    track_user_changes(user)

    response = f"Informasi Pengguna:\n\n"
    response += f"ID: {user.id}\n"
    response += f"Nama: {user.first_name}"
    if user.last_name:
        response += f" {user.last_name}"
    response += f"\nUsername: @{user.username}\n" if user.username else "\nUsername: Tidak ada\n"
    response += f"Bahasa: {user.language_code}\n" if user.language_code else ""
    response += f"Bot: {'Ya' if user.is_bot else 'Tidak'}\n"
    response += f"Premium: {'Ya' if user.is_premium else 'Tidak'}\n\n"

    response += f"History for {user.id}\n\n"

    if user.id in user_history:
        response += "Names\n"
        for i, name_change in enumerate(reversed(user_history[user.id]['names']), 1):
            response += f"{i}. [{name_change['time']}] {name_change['name']}\n"
        
        response += "\nUsernames\n"
        for i, username_change in enumerate(reversed(user_history[user.id]['usernames']), 1):
            response += f"{i}. [{username_change['time']}] @{username_change['username'] or 'None'}\n"
    else:
        response += "Tidak ada riwayat yang tercatat.\n"

    bot.reply_to(message, response)

@bot.message_handler(commands=['report'])
def report_command(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "Perintah ini hanya dapat digunakan dalam grup.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Silakan balas pesan yang ingin Anda laporkan dengan perintah /report.")
        return

    try:
        bot.delete_message(message.chat.id, message.message_id)

        reported_message = message.reply_to_message
        reported_user = reported_message.from_user
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        report_options = [
            "Spam", "Scam", "Porn", "Racis", 
            "Judi/Gambling", "Promotion", "Pishing", 
            "Cheat", "Rusuh/Riot", "HakCipta/Kanger", 
            "Other"
        ]
        buttons = [InlineKeyboardButton(option, callback_data=f"report_{option}_{reported_message.message_id}") for option in report_options]
        keyboard.add(*buttons)
        keyboard.row(InlineKeyboardButton("❌ Cancel", callback_data="cancel_report"))

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Anda melaporkan pesan dari {reported_user.id} - {reported_user.first_name}. Silakan pilih jenis laporan:",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat memproses perintah /report: {str(e)}")
        bot.send_message(message.chat.id, "Terjadi kesalahan saat memproses laporan.")

@bot.callback_query_handler(func=lambda call: call.data == 'report_cancel')
def cancel_report(call):
    try:
        bot.answer_callback_query(call.id, "Laporan dibatalkan.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Laporan telah dibatalkan.")
    except Exception as e:
        logging.error(f"Error in cancel report: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('report_') and not call.data == 'report_cancel')
def handle_report_button(call):
    logging.debug(f"Received callback data: {call.data}")
    logging.debug(f"Message text: {call.message.text}")
    try:
        data_parts = call.data.split('_')
        if len(data_parts) < 3:
            bot.answer_callback_query(call.id, "Data laporan tidak valid.")
            return

        report_type = data_parts[1]
        message_id = int(data_parts[2])

        chat = call.message.chat
        reported_user_id = call.message.text.split()[4]
        reported_user_name = call.message.text.split('-')[1].strip().split('.')[0]

        admin_list = get_admin_list()
        if OWNER not in admin_list:
            admin_list.append(OWNER)
        logging.debug(f"Admin list: {admin_list}")
        
        if not admin_list:
            logging.warning("Daftar admin kosong.")
            bot.answer_callback_query(call.id, "Tidak dapat mengirim laporan. Daftar admin kosong.")
            return

        message_link = f"https://t.me/c/{str(chat.id)[4:]}/{message_id}"
        
        report_text = (f"Laporan Baru 🚨\n\n"
                       f"Laporan: {report_type}\n"
                       f"pada grup: {chat.title}\n"
                       f"Pesan dari: {reported_user_id} ({reported_user_name})")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Lihat Pesan", url=message_link))
        
        sent_to_admins = []
        for admin_id in admin_list:
            try:
                bot.send_message(admin_id, report_text, reply_markup=markup)
                bot.forward_message(admin_id, chat.id, message_id)
                sent_to_admins.append(admin_id)
            except Exception as e:
                logging.error(f"Gagal mengirim laporan ke admin {admin_id}: {str(e)}")

        if sent_to_admins:
            bot.answer_callback_query(call.id, f"Laporan {report_type} telah dikirim ke admin.")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Laporan {report_type} untuk pesan dari {reported_user_name} telah dikirim ke admin. Terima kasih atas laporannya."
            )
        else:
            bot.answer_callback_query(call.id, "Gagal mengirim laporan ke semua admin.")

    except Exception as e:
        logging.error(f"Terjadi kesalahan saat memproses laporan: {str(e)}", exc_info=True)
        bot.answer_callback_query(call.id, "Terjadi kesalahan saat memproses laporan.")

bot.polling()
