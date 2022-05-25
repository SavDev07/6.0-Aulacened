from MoodleClient import MoodleClient
from NexCloudClient import NexCloudClient

import os

import ProxyCloud

from utils import get_file_size,sizeof_fmt,nice_time,text_progres,porcent,b_to_str
from telethon import Button,TelegramClient

async def progress_upload(filename, currentBits, totalBits, speed , time, args, stop=False):
    try:
        bot = args[0]
        message = args[1]
        text = '<b>'
        text += '📡 Subiendo Archivo....\n\n'
        text += '➤ Archivo: '+filename+'\n'
        text += text_progres(currentBits,totalBits)+'\n'
        text += '➤ Porcentaje: '+str(porcent(currentBits,totalBits))+'%\n\n'
        text += '➤ Total: '+sizeof_fmt(totalBits)+'\n\n'
        text += '➤ Descargado: '+sizeof_fmt(currentBits)+'\n\n'
        text += '➤ Velocidad: '+sizeof_fmt(speed)+'/s\n\n'
        text += '➤ Tiempo de Descarga: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
        text += '</b>'
        await message.edit(text,parse_mode='HTML')
    except Exception as ex:
        print(str(ex))
    pass

async def upload(ev,bot,jdb,message_edited=None):
    message = await bot.send_message(ev.sender_id,'⏳Procesando...')

    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    path = user_data['path']

    tokens = text.split(' ')

    index = -1
    cloudtype = 'moodle'
    uptype = 'draft'
    splitsize = -1
    buttons = None

    if len(tokens)>1:
        index = int(tokens[1])
    if len(tokens)>2:
        cloudtype = tokens[2]
    if len(tokens)>3:
        uptype = tokens[3]
    if len(tokens)>4:
        splitsize = int(tokens[4])

    if index!=-1:
         if path=='/':
             path = 'root'
         list = os.listdir(path)
         if path[-1]!='/':
             path+='/'
         item = path + list[index]
         if cloudtype == 'moodle':
             proxy = None
             if user_data['proxy']!='':
                 proxy = ProxyCloud.parse(user_data['proxy'])
             client = MoodleClient(
                 user_data['moodle_user'],
                           user_data['moodle_password'],
                           user_data['moodle_host'],
                           user_data['moodle_repo_id'],
                           proxy)
             loged = client.login()
             if loged:
                 if uptype == 'draft':
                     data = await client.upload_file_draft(item,progress_upload,(bot,message))
                     text = '<b>'
                     text += '💚 Descargado con Éxito 💚\n\n'
                     filename = str(item).split('/')[-1]
                     text += '👨🏻‍💻 '+filename+'\n'
                     text += '📦Tamaño Total: '+sizeof_fmt(filesize)+' \n'
                     text += '</b>'
                     buttons = [[Button.url('🔗Link De Descarga🔗',data['url'])]]
                 if uptype == 'evidencia':
                     filename = str(item).split('/')[-1]
                     evidence = client.createEvidence(filename)
                     data = client.upload_file(item,evidence,progress_upload,(bot,message))
                     text = '<b>'
                     text += '💚 Descargado con Éxito 💚\n\n'
                     text += '👨🏻‍💻 '+filename+'\n'
                     text += '📦Tamaño Total: '+sizeof_fmt(filesize)+' \n'
                     text += '</b>'
                     buttons = [[Button.url('🔗Link De Descarga🔗',data['url'])]]
                 if uptype == 'blog':
                     filename = str(item).split('/')[-1]
                     data = client.upload_file_draft(item,progress_upload,(bot,message))
                     client.createBlog(filename,data['id'])
                     text = '<b>'
                     text += '💚 Descargado con Éxito 💚\n\n'
                     text += '👨🏻‍💻 '+filename+'\n'
                     text += '📦Tamaño Total: '+sizeof_fmt(filesize)+' \n'
                     text += '</b>'
                     buttons = [[Button.url('🔗Link De Descarga🔗',data['url'])]]
             else:
                 text = '❌Error En La Autenticacion❌'
         if cloudtype == 'nexcloud':
             proxy = None
             if user_data['proxy']!='':
                 proxy = ProxyCloud.parse(user_data['proxy'])
             client = NexCloudClient(
                 user_data['moodle_user'],
                           user_data['moodle_password'],
                           user_data['moodle_host'],
                           proxy)
             loged = client.login()
             if loged:
                data = client.upload_file(item)
                filename = str(item).split('/')[-1]
                client.createBlog(filename,data['id'])
                text = '<b>'
                text += '💚 Descargado con Éxito 💚\n\n'
                text += '👨🏻‍💻 '+filename+'\n'
                text += '📦Tamaño Total: '+sizeof_fmt(filesize)+' \n'
                text += '</b>'
                buttons = [[Button.url('🔗Link De Descarga🔗',data['url'])]]
    try:
        await message.edit(text,buttons=buttons)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text,buttons=buttons)
    pass