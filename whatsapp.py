from fastapi import FastAPI, Request
from fastapi.responses import Response
import requests
import os


app = FastAPI(title="BankPhoenix WhatsApp Gateway")


# ============================================================
# 1. TWILIO CONFIGURATION
# ============================================================

TWILIO_ACCOUNT_SID = "ACeb4e269e0ab55cbb4e8cea399e040dab"
TWILIO_AUTH_TOKEN = "c83d207bef6518eabca9e6180de0a970"


# ============================================================
# 2. FRIEND'S AI AGENT
# ============================================================

# Keep None until your friend gives you the endpoint.

FRIEND_AGENT_URL = None

# Example:
# FRIEND_AGENT_URL = "http://192.168.1.10:8001/agent/input"


# ============================================================
# 3. HEALTH CHECK
# ============================================================

@app.get("/")
async def home():

    return {
        "status": "online",
        "service": "BankPhoenix WhatsApp Gateway",
        "provider": "Twilio"
    }


# ============================================================
# 4. TWILIO WHATSAPP WEBHOOK
# ============================================================

@app.post("/webhook")
async def receive_whatsapp_message(request: Request):

    try:

        # Twilio sends form-urlencoded data
        form = await request.form()

        data = dict(form)

        print("\n")
        print("=" * 60)
        print("        INCOMING TWILIO WHATSAPP MESSAGE")
        print("=" * 60)

        for key, value in data.items():
            print(f"{key}: {value}")

        print("=" * 60)


        # ----------------------------------------------------
        # Basic message information
        # ----------------------------------------------------

        message_sid = data.get("MessageSid")
        sender = data.get("From")
        receiver = data.get("To")
        body = data.get("Body", "")

        num_media = int(
            data.get("NumMedia", "0")
        )


        print("\n========== MESSAGE INFO ==========")
        print("Message SID :", message_sid)
        print("Sender      :", sender)
        print("Receiver    :", receiver)
        print("Body        :", body)
        print("Media count :", num_media)
        print("==================================\n")


        # ====================================================
        # TEXT MESSAGE
        # ====================================================

        if num_media == 0:

            normalized_json = {

                "channel": "whatsapp",

                "provider": "twilio",

                "message_id": message_sid,

                "sender": sender,

                "receiver": receiver,

                "type": "text",

                "text": body,

                "audio": None
            }


            print("\n========== NORMALIZED TEXT ==========")
            print(normalized_json)
            print("=====================================\n")


            # Send to friend's agent
            await send_to_friend(
                normalized_json
            )


        # ====================================================
        # MEDIA / VOICE MESSAGE
        # ====================================================

        else:

            media_url = data.get("MediaUrl0")

            media_content_type = data.get(
                "MediaContentType0"
            )


            print("\n========== MEDIA MESSAGE ==========")
            print("Media URL  :", media_url)
            print("Media Type :", media_content_type)
            print("===================================\n")


            audio_file = None


            # ------------------------------------------------
            # Download audio
            # ------------------------------------------------

            if (
                media_content_type
                and media_content_type.startswith("audio")
            ):

                audio_file = download_twilio_media(
                    media_url,
                    media_content_type
                )


            # ------------------------------------------------
            # Normalize audio message
            # ------------------------------------------------

            normalized_json = {

                "channel": "whatsapp",

                "provider": "twilio",

                "message_id": message_sid,

                "sender": sender,

                "receiver": receiver,

                "type": "audio" if audio_file else "media",

                "text": body if body else None,

                "audio": {

                    "media_url": media_url,

                    "mime_type": media_content_type,

                    "file_path": audio_file

                } if audio_file else None
            }


            print("\n========== NORMALIZED AUDIO ==========")
            print(normalized_json)
            print("======================================\n")


            # Send to friend's agent
            await send_to_friend(
                normalized_json
            )


        # ====================================================
        # TWILIO RESPONSE
        # ====================================================

        twiml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response></Response>
        """

        return Response(
            content=twiml,
            media_type="application/xml"
        )


    except Exception as e:

        print("\n========== WEBHOOK ERROR ==========")
        print(str(e))
        print("===================================\n")


        # Still return 200 so Twilio doesn't keep retrying
        twiml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response></Response>
        """

        return Response(
            content=twiml,
            media_type="application/xml"
        )


# ============================================================
# 5. DOWNLOAD TWILIO MEDIA
# ============================================================

def download_twilio_media(
    media_url,
    mime_type
):

    print("\n========== DOWNLOADING MEDIA ==========")
    print("Media URL :", media_url)
    print("MIME type :", mime_type)


    try:

        response = requests.get(

            media_url,

            auth=(
                TWILIO_ACCOUNT_SID,
                TWILIO_AUTH_TOKEN
            ),

            timeout=30
        )


        print(
            "Download status:",
            response.status_code
        )


        if response.status_code != 200:

            print(
                "Download failed:"
            )

            print(
                response.text
            )

            return None


        # ----------------------------------------------------
        # Determine extension
        # ----------------------------------------------------

        extension = ".bin"


        if "ogg" in mime_type:
            extension = ".ogg"

        elif "mpeg" in mime_type:
            extension = ".mp3"

        elif "wav" in mime_type:
            extension = ".wav"

        elif "mp4" in mime_type:
            extension = ".mp4"


        # ----------------------------------------------------
        # Create directory
        # ----------------------------------------------------

        os.makedirs(
            "received_audio",
            exist_ok=True
        )


        # ----------------------------------------------------
        # Create filename
        # ----------------------------------------------------

        existing_files = os.listdir(
            "received_audio"
        )

        filename = (
            f"received_audio/"
            f"audio_{len(existing_files)}"
            f"{extension}"
        )


        # ----------------------------------------------------
        # Save audio
        # ----------------------------------------------------

        with open(
            filename,
            "wb"
        ) as audio_file:

            audio_file.write(
                response.content
            )


        print(
            "Audio saved:",
            filename
        )

        print(
            "========================================\n"
        )


        return filename


    except Exception as e:

        print(
            "Media download error:",
            str(e)
        )

        return None


# ============================================================
# 6. SEND NORMALIZED JSON TO FRIEND
# ============================================================

async def send_to_friend(data):

    print("\n========== FORWARDING TO FRIEND ==========")

    print(data)

    print("===========================================\n")


    # --------------------------------------------------------
    # Friend endpoint not configured yet
    # --------------------------------------------------------

    if not FRIEND_AGENT_URL:

        print(
            "Friend endpoint is not configured yet."
        )

        print(
            "Message received successfully."
        )

        return


    try:

        response = requests.post(

            FRIEND_AGENT_URL,

            json=data,

            timeout=30
        )


        print(
            "Friend response:",
            response.status_code
        )

        print(
            response.text
        )


    except Exception as e:

        print(
            "Error forwarding to friend:",
            str(e)
        )
