import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

# Caso necessário, defina o caminho para o executável do Tesseract:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_tesseract(caminho_pdf):
    imagens = convert_from_path(caminho_pdf)
    texto_completo = ""
    for imagem in imagens:
        texto = pytesseract.image_to_string(imagem, lang='por')
        texto_completo += texto + "\n"
    return texto_completo

def extrair_texto_pdf(caminho_pdf: str) -> str:
    reader = PdfReader(caminho_pdf)
    texto = []
    for page in reader.pages:
        # extract_text() retorna None se não conseguir extrair
        page_text = page.extract_text() or ""
        texto.append(page_text)
    return "\n".join(texto)