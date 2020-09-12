# originally created by
# https://github.com/Total-Noob-69/X-tra-Telegram/blob/master/userbot/plugins/webupload.py

import asyncio
import json
import os
import re
import subprocess

import requests

from userbot import CMD_HELP
from userbot.utils import admin_cmd


@borg.on(admin_cmd(pattern="labstack ?(.*)"))
async def labstack(event):
    if event.fwd_from:
        return
    await event.edit("Processing...")
    input_str = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if input_str:
        filebase = input_str
    elif reply:
        filebase = await event.client.download_media(
            reply.media, Var.TEMP_DOWNLOAD_DIRECTORY
        )
    else:
        await event.edit(
            "Reply to a media file or provide a directory to upload the file to labstack"
        )
        return
    filesize = os.path.getsize(filebase)
    filename = os.path.basename(filebase)
    headers2 = {"Up-User-ID": "IZfFbjUcgoo3Ao3m"}
    files2 = {
        "ttl": 604800,
        "files": [{"name": filename, "type": "", "size": filesize}],
    }
    r2 = requests.post(
        "https://up.labstack.com/api/v1/links", json=files2, headers=headers2
    )
    r2json = json.loads(r2.text)

    url = "https://up.labstack.com/api/v1/links/{}/send".format(r2json["code"])
    max_days = 7
    command_to_exec = [
        "curl",
        "-F",
        "files=@" + filebase,
        "-H",
        "Transfer-Encoding: chunked",
        "-H",
        "Up-User-ID: IZfFbjUcgoo3Ao3m",
        url,
    ]
    try:
        logger.info(command_to_exec)
        t_response = subprocess.check_output(command_to_exec, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        logger.info("Status : FAIL", exc.returncode, exc.output)
        await event.edit(exc.output.decode("UTF-8"))
        return
    else:
        logger.info(t_response)
        t_response_arry = "https://up.labstack.com/api/v1/links/{}/receive".format(
            r2json["code"]
        )
    await event.edit(
        t_response_arry + "\nMax Days:" + str(max_days), link_preview=False
    )


@borg.on(
    admin_cmd(
        pattern="webupload ?(.+?|) --(fileio|oload|anonfiles|transfer|filebin|anonymousfiles|vshare|bayfiles)"
    )
)
async def _(event):
    await event.edit("processing ...")
    input_str = event.pattern_match.group(1)
    selected_transfer = event.pattern_match.group(2)
    catcheck = None
    if input_str:
        file_name = input_str
    else:
        reply = await event.get_reply_message()
        file_name = await event.client.download_media(
            reply.media, Config.TMP_DOWNLOAD_DIRECTORY
        )
        catcheck = True
    # a dictionary containing the shell commands
    CMD_WEB = {
        "fileio": 'curl -F "file=@{full_file_path}" https://file.io',
        "oload": 'curl -F "file=@{full_file_path}" https://api.openload.cc/upload',
        "anonfiles": 'curl -F "file=@{full_file_path}" https://anonfiles.com/api/upload',
        "transfer": 'curl --upload-file "{full_file_path}" https://transfer.sh/'
        + os.path.basename(file_name),
        "filebin": 'curl -X POST --data-binary "@{full_file_path}" -H "filename: {bare_local_name}" "https://filebin.net"',
        "anonymousfiles": 'curl -F file="@{full_file_path}" https://api.anonymousfiles.io/',
        "vshare": 'curl -F "file=@{full_file_path}" https://api.vshare.is/upload',
        "bayfiles": 'curl -F "file=@{full_file_path}" https://bayfiles.com/api/upload',
    }
    filename = os.path.basename(file_name)
    try:
        selected_one = CMD_WEB[selected_transfer].format(
            full_file_path=file_name, bare_local_name=filename
        )
    except KeyError:
        await event.edit("Invalid selected Transfer")
        return
    cmd = selected_one
    # start the subprocess $SHELL
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    error = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if t_response:
        try:
            t_response = json.dumps(json.loads(t_response), sort_keys=True, indent=4)
        except Exception:
            # some sites don't return valid JSONs
            pass
        urls = re.findall("(?P<url>https?://[^\s]+)", t_response)
        result = ""
        for i in urls:
            if result:
                result += "\n" + i
            else:
                result = f"the uploaded links of {selected_transfer} are :"
                result = "\n" + i
        await event.edit(result)
    else:
        await event.edit(error)
    if catcheck:
        os.remove(file_name)


CMD_HELP.update(
    {
        "webupload": "__**PLUGIN NAME :** __ `webupload`\
    \n\n**Syntax : **`.webupload` --(`fileio`|`oload`|`anonfiles`|`transfer`|`filebin`|`anonymousfiles`|`vshare`|`bayfiles`) or \
    \n         `.webuplod` (path of file) --(`fileio`|`oload`|`anonfiles`|`transfer`|`filebin`|`anonymousfiles`|`vshare`|`bayfiles`)\
    \n**Usage : **Upload the file to web according to your choice\
    \n**Example : **`.webupload --anonfiles` tag this to a file\
    \n\n**Syntax :** `.labstack` Reply to a media file or provide a directory\
    \n**Usage : **Upload the file to labstack for 7 days."
    }
)
