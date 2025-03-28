import pytesseract
from pdf2image import convert_from_path

# Caso necessário, defina o caminho para o executável do Tesseract:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extrair_texto_pdf(caminho_pdf):
    imagens = convert_from_path(caminho_pdf)
    texto_completo = ""
    for imagem in imagens:
        texto = pytesseract.image_to_string(imagem, lang='por')
        texto_completo += texto + "\n"
    return texto_completo
