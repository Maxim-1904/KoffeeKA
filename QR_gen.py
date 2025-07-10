import qrcode


BOT_USERNAME = "HakopitelnaSistemaKOFEKA_bot"


def generate_stamp_qr(output_path: str):
    '''
    генерирует QR code для печати
    '''
    link = f"https://t.me/{BOT_USERNAME}?start=get_stamp"
    qr = qrcode.QRCode(version=1,box_size=10,border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(output_path)


if __name__ == "__main__":
    generate_stamp_qr("stamp_qr_1.png")
    print("QR сгенерирован")