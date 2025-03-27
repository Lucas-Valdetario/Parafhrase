import os
import time
import docx
import pypdf
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
api_key= os.getenv("OPENAI_API_KEY")

class PDFProcessingSystem:
    def __init__(self):
        self.client = OpenAI()
        self.chat_model = ChatOpenAI(model="gpt-4o")
        self.md_converter = MarkdownIt()
        
    def extract_text_from_pdf(self, pdf_path):
        """Agente 1: Extrair texto do PDF"""
        print("🔍 Agente 1: Extraindo texto do PDF...")
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        print("✅ Texto extraído com sucesso!")
        return text
    
    def split_text(self, text, max_chunk_size=4000):
        """Agente 2: Dividir texto em chunks menores"""
        print("✂️ Agente 2: Dividindo o texto...")
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < max_chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                chunks.append(current_chunk)
                current_chunk = paragraph + '\n\n'
        if current_chunk:
            chunks.append(current_chunk)
        print(f"✅ Texto dividido em {len(chunks)} partes!")
        return chunks
    
    def paraphrase_chunk(self, chunk):
        """Agente 3: Parafrasear chunk de texto"""
        print("🔄 Agente 3: Parafraseando texto...")
        prompt = f"""
        Parafraseie o texto mantendo o significado original mas elevando o nível de linguagem:
        {chunk}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Parafraseador profissional"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000
        )
        return response.choices[0].message.content
    
    def generate_qa(self, text):
        """Agente 4: Gerar Perguntas e Respostas"""
        print("❓ Agente 4: Gerando Q&A...")
        chunks = self.split_text(text, 3000)
        qa_list = []
        
        for i, chunk in enumerate(chunks):
            print(f"   📝 Processando parte {i+1}/{len(chunks)} para Q&A...")
            prompt = f"""
            Gere 3 perguntas e respostas detalhadas sobre este texto.
            Formato exigido:
            P: [pergunta]
            R: [resposta]
            
            Texto:
            {chunk}
            """
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Especialista em criação de Q&A educacional"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            qa_list.append(response.choices[0].message.content)
            time.sleep(1)
        
        return "\n\n".join(qa_list)
    
    def paraphrase_all_chunks(self, chunks):
        """Agente 5: Coordenar paráfrase"""
        print("🧩 Agente 5: Coordenando paráfrase...")
        paraphrased = []
        for i, chunk in enumerate(chunks):
            print(f"   📝 Parafraseando parte {i+1}/{len(chunks)}...")
            paraphrased.append(self.paraphrase_chunk(chunk))
            time.sleep(1)
        return "\n\n".join(paraphrased)
    
    def generate_output_files(self, content, base_name, suffix):
        """Agente 6: Gerar arquivos de saída"""
        print(f"📄 Agente 6: Gerando arquivos {suffix}...")
        base = os.path.splitext(os.path.basename(base_name))[0]
        
        # TXT
        txt_path = f"{base}_{suffix}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # DOCX
        docx_path = f"{base}_{suffix}.docx"
        doc = docx.Document()
        for line in content.split('\n'):
            if line.strip():
                doc.add_paragraph(line.strip())
        doc.save(docx_path)
        
        print(f"✅ Arquivos {suffix} gerados: {txt_path}, {docx_path}")
        return {"txt": txt_path, "docx": docx_path}
    
    def process_pdf(self, pdf_path):
        """Fluxo principal de processamento"""
        print("\n🚀 Iniciando processamento...\n")
        
        # Extração e processamento
        text = self.extract_text_from_pdf(pdf_path)
        
        # Dividir e parafrasear o texto
        chunks = self.split_text(text)
        paraphrased = self.paraphrase_all_chunks(chunks)
        
        # Gerar Q&A a partir do texto parafraseado
        qa_content = self.generate_qa(paraphrased)
        
        # Geração de arquivos
        output_files = self.generate_output_files(paraphrased, pdf_path, "parafraseado")
        qa_files = self.generate_output_files(qa_content, pdf_path, "Q&A")
        
        # Resultado combinado
        combined = {**output_files, **qa_files}
        
        print("\n✨ Processamento concluído!")
        print("📂 Arquivos gerados:")
        for k, v in combined.items():
            print(f"  - {k.upper()}: {v}")
        
        return combined

def processar_pdf(pdf_path):
    system = PDFProcessingSystem()
    return system.process_pdf(pdf_path)

if __name__ == "__main__":
    arquivo = input("Digite o caminho do PDF: ")
    processar_pdf(arquivo)
