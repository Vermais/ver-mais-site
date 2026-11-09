# Ver+ 1.2.1 — correção da chamada Ei, Guia

1. Instale a atualização sobre o Ver+ anterior.
2. Toque uma vez em **Ativar Ei, Guia** e permita o microfone.
3. Aguarde **Aguardando: Ei, Guia**. A primeira preparação do modelo pode levar alguns segundos.
4. Diga **Ei, Guia**.
5. Aguarde a fala **Ouvindo, diga seu comando** e só então diga **abra a câmera ESP**.
6. Para perguntar, chame novamente, aguarde o convite para o comando e diga **quero perguntar sobre a imagem**. Aguarde **O que você quer saber sobre a imagem?** e fale sua pergunta.

O botão Falar é opcional. Após cada pedido, o Guia volta a esperar a chamada sem precisar tocar nele. A escolha de ativação fica salva; a escuta é retomada quando você volta ao aplicativo e para quando sai, apaga a tela ou desativa a função.

## O que foi corrigido

- A chamada não depende mais do serviço local do Android nem de instalar português nele. O modelo acompanha o aplicativo e usa o microfone continuamente, no próprio aparelho, enquanto o app está aberto.
- A resposta falada e a escuta do comando são etapas separadas. O tempo para falar começa depois do término da confirmação.
- O áudio da confirmação não é capturado como se fosse seu pedido.
- Falhas do reconhecedor de pedidos não apagam mais a preferência de ativação.
- A escuta se recupera de interrupções de microfone e é retomada após trocar de tela ou retornar de um diálogo.
- Sessões antigas não podem executar comandos depois de sair da tela.

## Compatibilidade e limites

Aplicativo e chamada: Android 9 ou superior, com microfone autorizado. A chamada usa Vosk e um modelo pequeno de português da Alpha Cephei. A escuta dos pedidos usa o serviço de voz do Android, que pode exigir internet e enviar o áudio ao provedor. As descrições com IA mantêm a configuração pessoal existente. A escuta não funciona em segundo plano.

A instalação ficou maior porque agora inclui o modelo de português e as bibliotecas de reconhecimento. O primeiro preparo exige espaço para extrair o modelo. O consumo de bateria e a precisão em ambientes ruidosos precisam de avaliação no aparelho real.

Foram acrescentados testes do fluxo completo com detectores e áudio simulados. O fluxo automatizado passou nos testes locais. Em 14 amostras sintetizadas com duas vozes do Windows em português brasileiro, o modelo reconheceu as quatro chamadas e ignorou as dez frases de controle. Outra voz sintetizada, do eSpeak, não foi reconhecida. Esses testes não substituem a validação do microfone e da chamada no Android físico.

## Componentes

- Vosk Android 0.3.75: Apache License 2.0 — https://github.com/alphacep/vosk-api
- Modelo vosk-model-small-pt-0.3: Apache License 2.0 — https://alphacephei.com/vosk/models
- JNA 5.18.1: disponibilizado sob Apache License 2.0 ou LGPL 2.1; esta distribuição utiliza a opção Apache — https://github.com/java-native-access/jna

Os avisos e textos de licença acompanham o aplicativo em assets/guia-licenses.

O APK de teste tem 80,4 MB. Seu SHA-256 é `58a233ddb24779002a4cf4991b8768645a6b64a465049ff219d752176182c0d5`.
