#!/bin/bash

echo "==================================="
echo "  NewCars - Inicialização Docker  "
echo "==================================="
echo ""

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Criando .env a partir do .env.example..."
    cp .env.example .env
    
    # Gerar SECRET_KEY aleatória
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || openssl rand -base64 50)
    
    # Substituir no .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|your-secret-key-here-change-in-production|$SECRET_KEY|g" .env
    else
        sed -i "s|your-secret-key-here-change-in-production|$SECRET_KEY|g" .env
    fi
    
    echo "✅ Arquivo .env criado!"
    echo "⚠️  IMPORTANTE: Edite o arquivo .env e configure suas variáveis antes de prosseguir!"
    echo ""
    read -p "Pressione ENTER para continuar após editar o .env..."
fi

echo ""
echo "🔨 Construindo imagens Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando serviços..."
docker-compose up -d

echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

echo ""
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "================================"
echo "✅ Deploy concluído com sucesso!"
echo "================================"
echo ""
echo "🌐 Aplicação disponível em: http://localhost"
echo "👤 Superusuário padrão: admin / admin123"
echo ""
echo "📝 Comandos úteis:"
echo "  - Ver logs:           docker-compose logs -f"
echo "  - Parar serviços:     docker-compose stop"
echo "  - Reiniciar:          docker-compose restart"
echo "  - Remover tudo:       docker-compose down -v"
echo ""
echo "📖 Consulte DEPLOY.md para mais informações"
echo ""
