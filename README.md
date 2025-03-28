# 🏥 MedFinder

## 📖 Descrição
O **MedFinder** é um sistema de consulta de medicamentos que permite aos usuários fazer o **upload de receitas médicas em PDF**. Utilizando **Tesseract OCR**, o sistema extrai informações do documento e verifica a disponibilidade dos medicamentos no estoque. 

O objetivo é fornecer uma plataforma eficiente para **farmácias e profissionais da saúde**, facilitando o acesso às informações dos medicamentos de forma rápida e automatizada.

---

## 🚀 Funcionalidades
✅ **Upload de Receitas** – Permite o envio de documentos em PDF.
✅ **Extração de Dados via OCR** – Utiliza **Tesseract OCR** para identificar os medicamentos na receita.
✅ **Consulta de Estoque** – Verifica a disponibilidade dos medicamentos no banco de dados.
✅ **API para Integração** – Disponibiliza endpoints para integração com outros sistemas.

---

## 🛠️ Tecnologias Utilizadas
🔹 **Back-end**: Python (Django)  
🔹 **OCR**: Tesseract OCR  
🔹 **Banco de Dados**: PostgreSQL ou SQLite  
🔹 **Front-end**:Html, Css, Javascript , Bootstrap
🔹 **API de Referência**: Integração com bases de dados de medicamentos  

---

## 📦 Instalação
### 1️⃣ Clone o repositório
```bash
git clone https://github.com/usuario/medifinder.git
cd medifinder
```

### 2️⃣ Crie um ambiente virtual e instale as dependências
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3️⃣ Instale o Tesseract OCR
#### 🔹 Linux
```bash
sudo apt install tesseract-ocr
```
#### 🔹 macOS
```bash
brew install tesseract
```
#### 🔹 Windows
```bash
choco install tesseract
```

### 4️⃣ Execute o servidor Django
```bash
python manage.py runserver
```

---

## 🌐 Uso da API
🔹 **`POST /upload`** – Faz o upload da receita e retorna os medicamentos identificados.  

---

## 🤝 Contribuição
Sinta-se à vontade para contribuir com melhorias! Basta abrir um **issue** ou enviar um **pull request**. 💡

---

## 📜 Licença
Este projeto está sob a licença **MIT**. Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.

---

💙 **Desenvolvido com dedicação para facilitar o acesso a medicamentos!** 🚀

