@echo off
echo ===================================
echo   NewCars - Inicialização Docker
echo ===================================
echo.

REM Verificar se .env existe
if not exist .env (
    echo [!] Arquivo .env não encontrado!
    echo [*] Criando .env a partir do .env.example...
    copy .env.example .env
    
    echo [OK] Arquivo .env criado!
    echo [!] IMPORTANTE: Edite o arquivo .env e configure suas variáveis antes de prosseguir!
    echo.
    pause
)

echo.
echo [*] Construindo imagens Docker...
docker-compose build

echo.
echo [*] Iniciando serviços...
docker-compose up -d

echo.
echo [*] Aguardando serviços iniciarem...
timeout /t 10 /nobreak > nul

echo.
echo [*] Status dos containers:
docker-compose ps

echo.
echo ================================
echo [OK] Deploy concluído com sucesso!
echo ================================
echo.
echo Aplicação disponível em: http://localhost
echo Superusuário padrão: admin / admin123
echo.
echo Comandos úteis:
echo   - Ver logs:           docker-compose logs -f
echo   - Parar serviços:     docker-compose stop
echo   - Reiniciar:          docker-compose restart
echo   - Remover tudo:       docker-compose down -v
echo.
echo Consulte DEPLOY.md para mais informações
echo.
pause
