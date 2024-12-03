#!/bin/bash

# Criar diretório de deploy se não existir
mkdir -p dist

# Copiar arquivos HTML
cp templates/*.html dist/

# Copiar arquivos CSS
mkdir -p dist/css
cp css/*.css dist/css/

# Copiar arquivos JavaScript
mkdir -p dist/js
cp js/*.js dist/js/

# Copiar ícones e outros recursos
mkdir -p dist/assets
cp -r assets/* dist/assets/ 2>/dev/null || true

# Criar arquivo de configuração do Netlify
cat > dist/netlify.toml << EOL
[build]
  publish = "."
  command = "echo 'Site estático'"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    Content-Security-Policy = "default-src 'self'; script-src 'self' https://kit.fontawesome.com"
EOL

echo "Build concluído. Arquivos no diretório dist/"
