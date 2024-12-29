from pptx import Presentation

def extract_text_from_pptx(file_path):
    # プレゼンテーションを読み込む
    presentation = Presentation(file_path)
    all_text = []

    # スライドごとにテキストを抽出
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:  # テキストフレームを持っている場合
                for paragraph in shape.text_frame.paragraphs:
                    all_text.append(paragraph.text)

    return all_text

# ファイルパスを指定してテキストを抽出
pptx_file = "example.pptx"
text_list = extract_text_from_pptx(pptx_file)

# 抽出結果を表示
for idx, text in enumerate(text_list):
    print(f"Text {idx + 1}: {text}")
