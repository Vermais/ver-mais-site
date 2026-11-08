# Ver+ 1.2.0 - Assistente Guia (teste)

Comandos de voz para abrir a c�mera ESP por Bluetooth, c�mera Wi-Fi, c�mera do celular e leitura offline. Nas telas de c�mera, � poss�vel pedir descri��o, perguntar sobre a imagem em duas etapas, repetir o resultado, parar e voltar.

Para come�ar, toque em **Ligar Guia**, permita o microfone e diga **"Ei, Guia, abra a c�mera ESP"**. Depois, diga **"Ei, Guia, quero perguntar sobre a imagem"**, aguarde o convite e fale sua pergunta.

## Compatibilidade e limites

- Aplicativo: Android 9 ou superior.
- Ativa��o "Ei, Guia": Android 12 ou superior, com reconhecedor local dispon�vel e portugu�s instalado. Funciona com o aplicativo aberto; n�o escuta em segundo plano.
- Sem esse suporte, use **Falar**. Nesse modo, o servi�o de voz do Android pode precisar de internet e enviar o �udio ao provedor, conforme aviso apresentado no aplicativo.
- Descri��es e perguntas com IA exigem internet e a configura��o pessoal do servi�o. Texto e cores continuam dispon�veis offline.
- Esta implementa��o usa sess�es locais de reconhecimento em primeiro plano; n�o � um detector dedicado de palavra-chave de baixo consumo. A precis�o e o consumo de bateria precisam de teste no aparelho.

## Valida��o

APK compilado e assinado com o mesmo certificado da vers�o 1.1.2. Foram aprovados 133 testes locais; an�lise est�tica sem erros. Outros 44 testes que exigem rede local e 3 benchmarks opcionais n�o foram executados. Microfone real, precis�o da chamada, ESP, TalkBack e servi�o de IA ainda precisam de valida��o f�sica.

O APK publicado � o arquivo j� verificado, sem recompila��o. SHA-256: `45311cde13e74f875146c8e316acd9e942755a2be3c214dd50d01deaf6f26d24`.

