import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_styled_qr(data: str, title: str, subtitle: str, filename: str, accent_color: tuple = (6, 182, 212)):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Base QR image with dark background and vibrant foreground
    qr_img = qr.make_image(fill_color="#06B6D4" if accent_color == (6, 182, 212) else "#10B981", back_color="#090E1A").convert("RGBA")
    
    card_width = qr_img.width + 80
    card_height = qr_img.height + 140

    card = Image.new("RGBA", (card_width, card_height), "#0D1527")
    draw = ImageDraw.Draw(card)

    # Rounded outer border / card styling
    draw.rectangle([(0, 0), (card_width - 1, card_height - 1)], outline=accent_color, width=3)

    # Paste QR Code in center
    qr_x = (card_width - qr_img.width) // 2
    card.paste(qr_img, (qr_x, 40))

    # Text annotations
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_sub = ImageFont.truetype("arial.ttf", 15)
        font_url = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_url = font_title

    # Header Title
    draw.text((card_width // 2, 20), title, fill=(248, 250, 252), font=font_title, anchor="mm")
    
    # Subtitle
    draw.text((card_width // 2, card_height - 75), subtitle, fill=(148, 163, 184), font=font_sub, anchor="mm")
    
    # URL snippet
    draw.text((card_width // 2, card_height - 40), data, fill=accent_color, font=font_url, anchor="mm")

    card.save(filename, "PNG")
    print(f"Generated: {filename} ({card_width}x{card_height})")

if __name__ == "__main__":
    os.makedirs("demo_assets", exist_ok=True)
    
    apk_url = "https://github.com/kanka-317/WeatherGPT/releases/download/v1.0.1/app-arm64-v8a-release.apk"
    web_url = "https://weathergpt-mobile.netlify.app"

    generate_styled_qr(
        data=apk_url,
        title="📱 Scan to Download Android APK",
        subtitle="Full-Parity Flutter Release (ARM64-v8a)",
        filename="demo_assets/qr_weathergpt_apk.png",
        accent_color=(6, 182, 212), # Cyan
    )

    generate_styled_qr(
        data=web_url,
        title="🌐 Scan for Zero-Install Web Demo",
        subtitle="Instant Mobile Browser Client",
        filename="demo_assets/qr_weathergpt_web.png",
        accent_color=(16, 185, 129), # Emerald
    )
