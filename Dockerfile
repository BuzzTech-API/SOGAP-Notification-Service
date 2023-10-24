# Use uma imagem base do Python
FROM python:3.10-alpine AS builder

# Define o diretório de trabalho dentro do contêiner

# Copie o arquivo requirements.txt para o contêiner
WORKDIR /code
COPY ./ /code


# Instale as dependências usando o pip
RUN pip install -r requirements.txt

# Copie todos os arquivos do diretório local para o diretório de trabalho no contêiner
COPY . .

# Exponha a porta em que a aplicação FastAPI será executada (substitua pela porta real, se necessário)
EXPOSE 8000

# Comando para executar a aplicação FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
