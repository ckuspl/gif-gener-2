# ✅ 適用 Vercel 的 Flask 網頁應用
from flask import Flask, request, send_file, Response
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_GIF = "static/animated_output.gif"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>圖片轉動畫生成器</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; padding: 30px; background-color: #f7f7f7; }}
        h2 {{ color: #333; }}
        input[type=file] {{ margin: 10px; }}
        .btn {{ padding: 10px 20px; font-size: 16px; background: #2e86de; color: white; border: none; cursor: pointer; border-radius: 5px; }}
        .btn:hover {{ background: #1e6bb8; }}
        img {{ margin-top: 20px; max-width: 100%; height: auto; border: 1px solid #ccc; }}
    </style>
</head>
<body>
    <h2>圖片轉動畫生成器</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="images" multiple required accept="image/*">
        <br>
        <button class="btn" type="submit">生成動畫</button>
    </form>
    {{content}}
</body>
</html>
'''

@app.route("/", methods=['GET', 'POST'])
def upload():
    gif_ready = False
    error_message = ""
    content = ""

    if request.method == 'POST':
        files = request.files.getlist("images")
        if not files or all(f.filename == '' for f in files):
            error_message = "請選擇至少一張圖片。"
        else:
            images = []
            for file in files:
                if allowed_file(file.filename):
                    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(filepath)
                    try:
                        with Image.open(filepath) as img:
                            img = img.convert("RGB").resize((512, 512))
                            images.append(img)
                    except Exception as e:
                        print(f"圖片讀取錯誤: {e}")
            if len(images) > 0:
                try:
                    images[0].save(
                        OUTPUT_GIF,
                        save_all=True,
                        append_images=images[1:],
                        duration=200,
                        loop=0
                    )
                    gif_ready = True
                except Exception as e:
                    error_message = f"GIF 生成錯誤: {e}"
            else:
                error_message = "無法處理上傳的圖片，請檢查檔案格式與內容。"

    if gif_ready:
        content = f'''<h3>動畫預覽：</h3>
        <img src="/{OUTPUT_GIF}"><br><br>
        <a href="/{OUTPUT_GIF}" download class="btn">下載動畫 GIF</a>'''
    elif error_message:
        content = f'<p style="color: red;">{error_message}</p>'

    return Response(HTML_PAGE.format(content=content), content_type='text/html')

app = app
