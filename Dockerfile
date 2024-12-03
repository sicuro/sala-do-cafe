# Use uma imagem base de servidor web leve
FROM nginx:alpine

# Copiar arquivos do projeto para o diretório padrão do nginx
COPY . /usr/share/nginx/html

# Expor a porta padrão do nginx
EXPOSE 80

# Comando padrão para iniciar o nginx
CMD ["nginx", "-g", "daemon off;"]
