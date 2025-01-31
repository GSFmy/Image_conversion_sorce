import os
import cv2
import numpy as np
from tkinter import Tk, filedialog
from PIL import Image, ImageDraw, ImageFont


# 使用可能な文字のリスト
ASCII_CHARS = " !" + '"#$%&\'()-=^~\\|@`[{*:}],<.>/?_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '

# システムに存在するフォントを使用
def get_font_path():
    common_paths = [
        "C:\\\\Windows\\\\Fonts\\\\consola.ttf",  # Consolas
        "C:\\\\Windows\\\\Fonts\\\\cour.ttf",    # Courier New
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",  # Linux例
        "/Library/Fonts/Andale Mono.ttf",       # macOS例
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("適切なフォントファイルが見つかりません。FONT_PATH を確認してください。")

FONT_PATH = get_font_path()
FONT_SIZE = 10  # 文字サイズ
CHAR_IMG_SIZE = (FONT_SIZE, FONT_SIZE)  # 各文字の画像サイズ

# 文字と画像の対応表を作成
def generate_char_images():
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    char_images = {}
    for char in ASCII_CHARS:
        img = Image.new("L", CHAR_IMG_SIZE, color=255)  # 白背景
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, font=font, fill=0)  # 黒文字
        char_images[char] = np.array(img)
    return char_images

# 入力画像を選択
def select_image():
    Tk().withdraw()  # GUIウィンドウを非表示
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    return file_path


# 画像を線画化
def preprocess_image(image_path):
    # 画像を読み込む
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {image_path}\nファイルパスを確認してください。")

    # 透明部分を白に変換
    if image.shape[2] == 4:  # RGBA画像
        alpha_channel = image[:, :, 3]
        white_background = np.ones_like(image[:, :, :3]) * 255
        image = np.where(alpha_channel[:, :, None] == 0, white_background, image[:, :, :3])

    # グレースケール化
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # エッジ検出
    edges = cv2.Canny(gray_image, 50, 150)

    # 黒と白のピクセルをカウント
    black_pixels = np.sum(edges == 0)  # 黒のピクセル数
    white_pixels = np.sum(edges == 255)  # 白のピクセル数

    # 黒のピクセルが多い場合、白黒を反転
    if black_pixels > white_pixels:
        edges = cv2.bitwise_not(edges)

    return edges

# 画像をアスキーアートに変換
def generate_ascii_art(edges, ascii_chars, output_size=None):
    if output_size is None:
        # 元の画像サイズに基づいて処理
        height, width = edges.shape
    else:
        # 指定されたサイズにリサイズ
        width, height = output_size
        edges = cv2.resize(edges, (width, height), interpolation=cv2.INTER_AREA)

    # ピクセルを文字にマッピング
    ascii_art = []
    for row in edges:
        line = ''.join(ascii_chars[pixel // (256 // len(ascii_chars))] for pixel in row)
        ascii_art.append(line)

    return '\n'.join(ascii_art)


# 画像をアスキーアートに変換
def image_to_ascii(image, char_images):
    ascii_art = []
    height, width = image.shape
    for y in range(0, height, FONT_SIZE+FONT_SIZE):
        row = ""
        for x in range(0, width, FONT_SIZE):
            element = image[y:y+FONT_SIZE, x:x+FONT_SIZE]
            if element.shape != (FONT_SIZE, FONT_SIZE):
                padded = np.ones((FONT_SIZE, FONT_SIZE), dtype=np.uint8) * 255
                padded[:element.shape[0], :element.shape[1]] = element
                element = padded

            # 正規化された類似度で最適な文字を選択
            best_char = min(
                ASCII_CHARS,
                key=lambda char: np.mean(np.abs(char_images[char] - element))
            )
            row += best_char
        ascii_art.append(row)
    return ascii_art

# アスキーアートを保存
def save_ascii_art(ascii_art, output_txt, output_png):
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(ascii_art))

    # フォント設定
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    max_line_length = max(len(line) for line in ascii_art)  # 最長行の文字数

    # フォントの1文字幅と高さを正確に計算
    font_width, font_height = font.getbbox("A")[2], font.getbbox("A")[3]
    img_width = max_line_length * font_width  # 最長行に基づく画像幅
    img_height = len(ascii_art) * font_height  # 行数に基づく画像高さ

    # 空の画像を作成
    img = Image.new("L", (img_width, img_height), color=255)
    draw = ImageDraw.Draw(img)

    # 行ごとに文字を描画
    for y, row in enumerate(ascii_art):
        draw.text((0, y * font_height), row, font=font, fill=0)

    img.save(output_png)


# メイン処理
def main():
    print("画像を選択してください...")
    image_path = select_image()
    print("画像を処理中...")

    try:
        edges = preprocess_image(image_path)

        # 線画が正常に生成されているか確認（必要がなくなればコメントアウト）
        # cv2.imshow("Edges", edges)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # アスキーアート生成（元画像サイズで出力）
        char_images = generate_char_images()
        ascii_art = image_to_ascii(edges, char_images)

        output_txt = os.path.splitext(image_path)[0] + "_ascii.txt"
        output_png = os.path.splitext(image_path)[0] + "_ascii.png"
        save_ascii_art(ascii_art, output_txt, output_png)

        print(f"アスキーアートを保存しました: {output_txt}, {output_png}")

    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
