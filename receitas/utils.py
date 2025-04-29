import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import re, decimal
from fuzzywuzzy import process
from receitas.models import Medicamento, Estoque


def extract_tesseract(caminho_pdf, psm=3)-> dict:
    """
    Extracts text from a PDF file using Tesseract OCR.

    Args:
        caminho_pdf (str): The path to the PDF file.

    Returns:
        dict: A dictionary with two keys:
            'text': The extracted text from the PDF.
            'confidence': The confidence level of the OCR process.
    """
    try:
        # Convert the PDF to a list of images
        imagens = convert_from_path(caminho_pdf)
        texto_completo = ""
        confianca_total = 0
        num_imagens = len(imagens)
        for imagem in imagens:
            # Use pytesseract to extract the text from the current image, using 'por' language
            texto = pytesseract.image_to_string(imagem, lang="por", config=f'--psm {psm}')
            # Add the current extracted text to the complete text
            texto_completo += texto + "\n"
            # Get the confidence level of the OCR process
            dados = pytesseract.image_to_data(imagem, output_type=pytesseract.Output.DICT, lang="por", config=f'--psm {psm}')
            confianca_total += sum(int(conf) for conf in dados['conf'] if conf != '-1') / len(dados['conf']) if len(dados['conf']) > 0 else 0
        confianca_media = confianca_total / num_imagens if num_imagens > 0 else 0
        # Return the complete extracted text
        return {'text':texto_completo,'confidence':confianca_media}
    except FileNotFoundError:
        # Handle the case where the PDF file does not exist
        print(f"Error: File not found at path: {caminho_pdf}")
        return {'text':"",'confidence':0}
    except Exception as e:
        # Handle other potential exceptions during OCR
        print(f"Error during Tesseract OCR: {e}")
        return ""


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """
    Extracts text from a PDF file using PyPDF2.
    """
    try:
        # Open the PDF file using PyPDF2's PdfReader
        reader = PdfReader(caminho_pdf)
        texto = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(texto)
    except Exception as e:
        print(f"Error during PDF reading: {e}")
        return ""

def check_medicine_availability(medicine_names):
    """
    Checks the availability of a list of medicines in the database.
    Args:
        medicine_names (list): A list of medicine names to check.
    Returns:
        list: A list of dictionaries with the medicine name and its availability (True/False).
    """
    # Get all medicines that match the names, and prefetch the related Estoque objects
    medicines = Medicamento.objects.filter(nome__in=medicine_names).prefetch_related('estoque_set')
    
    # Create a dictionary to store availability information
    availability_data = {}
    for medicine in medicines:
        #Check if there is any stock for this medicine.
        if medicine.estoque_set.exists():
            availability_data[medicine.nome] = medicine.estoque_set.first().quantidade > 0
        else:
            availability_data[medicine.nome] = False
    
    # Create the final list with availability information for all medicines names
    return [{"nome": name, "disponivel": availability_data.get(name, False)} for name in medicine_names]


def clean_medicine_names(medicine_names):
    """
    Cleans a list of medicine names extracted from the OCR.

    This function uses regular expressions to extract the medicine name and dosage
    from the extracted text. It also corrects common OCR errors, like replacing
    'rn' to 'm' or '0' to 'O'.

    Args:
        medicine_names (list): A list of strings representing the medicine names
                               extracted from the OCR.

    Returns:
        list: A list of strings with the cleaned medicine names.
    """
    cleaned_names = []
    for name in medicine_names:
        # Correct common OCR errors
        name = name.replace("rn", "m").replace("0", "O")

        # Use regex to extract the medicine name and dosage
        match = re.search(r"([a-zA-Z\s]+)\s*([\d.,]+)?", name)
        if match:
            medicine_name = match.group(1).strip()
            # dosage = match.group(2).strip() if match.group(2) else None
            cleaned_names.append(medicine_name)
        else:
            # If no pattern is found, add the original text (after error correction)
            cleaned_names.append(name)

    return cleaned_names

def fuzzy_match_medicine_names(medicine_names):
    """
    Applies fuzzy matching to a list of medicine names to correct slight OCR mistakes.

    Args:
        medicine_names (list): A list of medicine names extracted from the OCR.

    Returns:
        list: A list of medicine names corrected using fuzzy matching.
    """
    all_medicine_names = [medicine.nome for medicine in Medicamento.objects.all()]
    corrected_names = []

    for name in medicine_names:
        # Use fuzzy matching to find the closest match in the database
        best_match = process.extractOne(name, all_medicine_names)
        if best_match:
            # If a good match is found (above a certain threshold), use the corrected name
            corrected_names.append(best_match[0])
        else:
            corrected_names.append(name)  # Keep the original name if no match is found
    return corrected_names

def populate_database():
    """
    Populates the database with some initial data for Medicamento and Estoque.
    """
    medicamentos_data = [
        {"nome": "Dipirona", "codigo_barras": "1234567890", "fabricante": "EMS", "dosagem": "500mg", "forma_farmaceutica": "Comprimido", "preco": decimal.Decimal("10.50"), "quantidade": 100},
        {"nome": "Amoxicilina", "codigo_barras": "9876543210", "fabricante": "Sandoz", "dosagem": "250mg", "forma_farmaceutica": "Cápsula", "preco": decimal.Decimal("15.99"), "quantidade": 50},
        {"nome": "Paracetamol", "codigo_barras": "1122334455", "fabricante": "Medley", "dosagem": "750mg", "forma_farmaceutica": "Comprimido", "preco": decimal.Decimal("8.75"), "quantidade": 75},
        {"nome": "Ibuprofeno", "codigo_barras": "5544332211", "fabricante": "Neo Química", "dosagem": "400mg", "forma_farmaceutica": "Comprimido", "preco": decimal.Decimal("12.30"), "quantidade": 60},
        {"nome": "Loratadina", "codigo_barras": "1020304050", "fabricante": "Eurofarma", "dosagem": "10mg", "forma_farmaceutica": "Comprimido", "preco": decimal.Decimal("20.00"), "quantidade": 40},
    ]

    for data in medicamentos_data:
        # Check if a medicine with the same name already exists
        try:
            medicamento = Medicamento.objects.get(nome=data["nome"])
        except Medicamento.DoesNotExist:
            # Create a new Medicamento object
            medicamento = Medicamento.objects.create(
                nome=data["nome"], codigo_barras=data["codigo_barras"], fabricante=data["fabricante"],
                dosagem=data["dosagem"], forma_farmaceutica=data["forma_farmaceutica"], preco=data["preco"]
            )

        # Check if a stock already exists for this medicine
        try:
            Estoque.objects.get(medicamento=medicamento)
        except Estoque.DoesNotExist:
            # Create a new Estoque object
            Estoque.objects.create(medicamento=medicamento, quantidade=data["quantidade"])