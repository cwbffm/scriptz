# CrashNative v0.1 — Crash Bandicoot 1 PS1 analysis

Projeto experimental e independente para analisar o Crash Bandicoot 1 (SCUS-94900) e preparar um futuro port nativo Windows.

**Estado:** extrator NSD/NSF e visualizador Win32. Nao e o jogo, nao reproduz as fases em 3D, nao e emulador e nao contem recursos do jogo.

## O que foi implementado

- tools/crashnative.py: le Crash.zip contendo SCUS_949.00 e S0-S3/NSD/NSF; identifica NSD v0/v1, blocos NSF normais ou comprimidos, arquivos GOOL, metadados do executavel e gera relatorios JSON.
- Exporta imagens de tela de carregamento NSD como BMP (PS1 RGB555).
- Option --dump-gool exporta registros binarios brutos do jogo APENAS para seu computador, nao para este repositorio.
- src/inspector.cpp: programa nativo Win32 que abre os relatorios e exibe os BMPs extraidos.
- tests/test_crashnative.py: testes com dados artificiais. Nenhum recurso comercial esta incluido.
- workflow Windows: build e teste automatico em GitHub Actions.

## Uso no Windows

Python 3.10+ para a extracao. Visual Studio com compilador C++ e CMake para criar o aplicativo Windows.

    py -3 CrashNative/tools/crashnative.py C:\Jogos\Crash.zip --out C:\CrashNative-output
    py -3 -m unittest discover -s CrashNative/tests -v
    cmake -S CrashNative -B CrashNative/build -A x64
    cmake --build CrashNative/build --config Release
    .\CrashNative\build\Release\CrashNativeInspector.exe

O padrao analisa todos os pares de NSD/NSF. Para so o primeiro, acrescente --limit 1. Para extrair os registros GOOL brutos no disco local, acrescente --dump-gool.

Abra CrashNative-output/summary.txt ou CrashNative-output/previews/*.bmp no aplicativo.

## Limites atuais

Este projeto foi produzido a partir de documentacao publica e de um inventario de nomes dos arquivos fornecido pelo usuario. **Nao foi executado no ZIP original neste ambiente.** Os resultados reais podem requerer ajustes nos offsets e nos formatos de arquivo. Mesmo se o build Windows passar, isso so valida o programa de inspecao e NAO comprova que um jogo nativo existe.

Port completo requer: descompilar o executavel MIPS e GOOL, reconstruir modelo de mundo/camera/colisoes, decodificar TGEO/WGEO e animacoes, implementar renderer, audio e controles, e validar cada nivel.

## Fontes tecnicas

- https://psx-spx.consoledev.net/dev/ps1/cdr/cdromfileformats/archives/
- https://wiki.cbhacks.com/w/NSD
- https://wiki.cbhacks.com/w/Chunk
- https://github.com/cbhacks/CrashEdit

## Direito autoral

Nao publique nem compartilhe copias de arquivos originais do jogo; forneca sua propria copia para a analise local. Este repositorio contem somente ferramentas independentes.
