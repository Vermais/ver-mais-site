# Site Ver+

Landing page responsiva e acessível do projeto Ver+.

## Publicar uma nova versão do aplicativo

O site oferece diretamente o APK 1.0.5 como **versão de teste**, sem depender da API do GitHub para habilitar o download. Uma consulta opcional pode selecionar um lançamento estável posterior. Uma versão estável mais antiga não substitui a versão de teste exibida, pois o endpoint `releases/latest` exclui pré-lançamentos.

1. Abra **Releases** no GitHub e escolha **Draft a new release**.
2. Crie uma tag, por exemplo `v0.6.0`.
3. Anexe o APK, de preferência com um nome como `ver-mais-v0.6.0.apk`.
4. Publique a release.

Um lançamento estável posterior pode atualizar o botão automaticamente. Ao publicar um pré-lançamento, atualize também o link direto, `data-release-tag`, versão e rótulo no HTML. APKs devem ser anexados à Release.

## Publicação verificada da versão de teste 1.0.5

O fluxo `.github/workflows/publish-android-105.yml` publica o APK já assinado, sem recompilá-lo. Os dados em `.github/release-105/parts` são a diferença binária para o APK público 1.0.4. O publicador verifica os resumos SHA-256 da base e do arquivo reconstruído antes de enviar qualquer APK, inclui o relatório e mantém a release como pré-lançamento. Não contém chave pessoal de IA. Se houver um arquivo com o mesmo nome e conteúdo diferente, a publicação é interrompida sem sobrescrever o arquivo existente.

A versão 1.0.5 não inclui tela de consumo da API. Os dados de tokens disponíveis ficam nos registros técnicos; o site e a release deixam essa limitação explícita. A validação física de câmera, áudio e TalkBack permanece pendente.
