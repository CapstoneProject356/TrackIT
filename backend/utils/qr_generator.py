import qrcode

def generate_qr(token):
    img = qrcode.make(token)
    path = f"static/qr/{token}.png"
    img.save(path)
    return path
