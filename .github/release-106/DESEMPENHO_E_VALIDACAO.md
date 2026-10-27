# Ver+ 1.0.6 — descrições mais objetivas

27/10/2026. Revisão de teste, código 18. A solicitação foi esclarecida: o incômodo é o texto extenso. A alteração concentra-se em descrições mais naturais, curtas e úteis, preservando o modo escolhido e as preferências. Não é uma certificação de precisão visual ou de tempo garantido de resposta.

## O que encontrei nas versões antigas

Examinei os identificadores dos modelos nos 12 APKs principais do acervo e os clientes de IA em 12 arquivos compactados de fontes. Os resultados completos estão em `auditoria-apks.json` e `auditoria-fontes.json`, sem chaves. Nomes e datas de arquivos não foram usados para afirmar velocidade ou correspondência exata de fontes com APKs.

| Versão declarada no índice conferido | Modelos encontrados nos APKs |
|---|---|
| 0.1-mvp | `meta-llama/llama-4-scout-17b-16e-instruct`, `meta/llama-3.2-11b-vision-instruct` |
| 0.2-accessibility | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b` |
| 0.3-brand | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b` |
| 0.4 | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b` |
| 0.5 | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b` |
| 0.6-prototipo | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b`, `qwen/qwen3.8-27b` |
| 0.7-bateria | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b`, `qwen/qwen3.8-27b` |
| 0.8-bluetooth | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b`, `qwen/qwen3.8-27b` |
| 0.9-esp32cam | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b`, `qwen/qwen3.8-27b` |
| 0.11-camera-usb | `meta/llama-3.2-11b-vision-instruct`, `qwen/qwen3.6-27b`, `qwen/qwen3.8-27b` |
| 1.0.0-mvp | `nvidia/nemotron-3.5-super-vl-120b-a12b`, `qwen/qwen3.8-27b` |
| 1.0.1-mvp | `nvidia/nemotron-3.5-super-vl-120b-a12b`, `qwen/qwen3.8-27b` |

As versões 0.1 a 0.6 continham pedidos de descrições curtas, em geral 1–3 frases e tetos de 260–400 tokens. A versão 1.0 introduziu o modelo principal atual; os níveis e as orientações extensas cresceram depois. A presença de um identificador no APK não prova qual serviço foi usado em cada análise do aparelho. Não há registros antigos de latência que permitam confirmar os tempos históricos; o serviço e a rede também mudam.

Alguns modelos antigos não são uma opção segura de simples restauração: a [documentação de descontinuações da Groq](https://console.groq.com/docs/deprecations) registra o desligamento de Llama 4 Scout e Qwen 3.6 para os planos comuns. O código antigo foi usado como referência de estilo; o serviço configurado pelo usuário e o modelo atual não foram trocados silenciosamente.

## Por que a descrição estava cansativa

A 1.0.5 gerava sete campos, incluindo quatro metadados de pessoa que não são consumidos pelas telas atuais. Esses campos vinham antes da descrição, atrasando o primeiro trecho. A aplicação também acrescentava o título “Limitação da imagem” e o texto de incerteza antes da frase. Isso produziu avisos como falta de expressão facial ou distância exata em uma pergunta que não pedia essas informações, além de casos como “Limitação da imagem: Não há incertezas relevantes”.

O aviso de espera falado depois de dez segundos somava outra frase à fala inicial. Os pedidos também incentivavam inventário de contexto e repetiam instruções. Foram preservadas as regras de evidência, orientação, confiança e segurança, mas com foco mais concreto na pergunta e no assunto principal.

## Alterações implementadas

- Resposta compacta com `confianca`, `incertezas` e `frase`, nessa ordem. A confiança e a limitação continuam sendo validadas antes da primeira frase narrada. Respostas legadas completas continuam aceitas e seus metadados contraditórios são rejeitados; o formato parcial antigo não é liberado sem validação.
- Remoção do cabeçalho automático “Limitação da imagem”. Incertezas realmente informadas continuam antes da descrição, em linguagem natural, sem repetir o mesmo aviso no início. Apenas marcadores vazios inequívocos, como “Nenhuma” e “Não há”, são tratados como ausência de limitação; “Não há luz suficiente” continua sendo comunicado.
- Instruções para não listar detalhes não solicitados nem repetir a incerteza na frase. Nenhum texto é truncado localmente para atingir uma contagem de palavras. Se o serviço interrompe a geração, o aplicativo continua avisando sobre a interrupção.
- **Rápida:** uma frase direta, cerca de 25 palavras; segunda frase somente para informação essencial. **Média:** duas frases, cerca de 45 palavras. **Detalhada:** três ou quatro frases curtas, cerca de 80 palavras e mais contexto útil. A IA pode não seguir exatamente essas contagens; detalhes críticos não devem ser omitidos para encurtar.
- Tetos totais de saída: **240 / 360 / 560 tokens**, incluindo os metadados. Os resultados reais desta amostra não atingiram os tetos. A melhora não é atribuída isoladamente ao limite de tokens; a mudança principal foi reduzir conteúdo e metadados redundantes.
- A confirmação inicial de processamento ficou em “Analisando.”. O aviso posterior atualiza a informação de estado acessível, sem acrescentar outra fala automática. Mensagens de erro, ação de parar e nova tentativa continuam disponíveis.
- Câmeras, resolução/JPEG, preferências pessoais, voz e velocidade salvas, uso com leitor de tela e recursos offline foram preservados. A escolha de Rápida/Média/Detalhada não foi alterada.

## Comparação real de antes e depois

24 chamadas sequenciais: duas cenas fixas, três modos, duas rodadas e duas versões. A ordem foi invertida na segunda rodada. Usei o cliente 1.0.5 preservado em testes e o cliente novo, mesmo serviço NVIDIA/modelo `nvidia/nemotron-3.5-super-vl-120b-a12b`, mesma preferência de teste e os mesmos JPEGs. Uma cena é o [exemplo público da NVIDIA](https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1a.jpg); a outra contém figuras/etiquetas sintéticas. Nenhuma foto pessoal foi enviada.

Medianas das respostas aceitas pelo formato e confiança, não por certificação factual. O tempo começa com a imagem já disponível em memória; captura física e início sonoro real não foram medidos.

| Modo | Palavras antes → depois | Primeiro trecho antes → depois | Texto concluído antes → depois | Respostas aceitas |
|---|---:|---:|---:|---:|
| Rápida | 45,5 → 22,5 | 1,39 s → 1,31 s | 1,54 s → 1,40 s | 4/4 → 4/4 |
| Média | 61,5 → 25,5 | 1,50 s → 1,52 s | 2,14 s → 1,61 s | 4/4 → 4/4 |
| Detalhada | 76,0 → 43,5 | 2,06 s → 1,20 s | 2,37 s → 2,09 s | 4/4 → 4/4 |

Nos 12 resultados atuais, houve zero cabeçalhos automáticos de limitação e zero menções não solicitadas a expressão/gesto/distância exata nos textos dessas duas cenas. Houve zero falhas por prazo e zero términos por corte de tokens nesta rodada. Os resultados brutos, inclusive trechos progressivos, estão em `comparacao-natural.json`; estatísticas em `resumo-comparacao.json`.

A API esteve mais rápida nesta rodada que nos ensaios de 26/10. Isso não foi atribuído à alteração local: por isso o comparativo usa a 1.0.5 novamente, intercalada no mesmo período. O primeiro trecho da Média não ficou mais rápido na mediana. Também houve uma resposta Detalhada atual de **18,795 s**, apesar do texto curto. O serviço ainda pode oscilar; não há promessa de resposta sempre em poucos segundos.

### Exemplo real de redução de texto

Na cena de figuras, a Rápida nova respondeu: “À esquerda, um retângulo azul com a palavra CAIXA acima. À direita, um círculo vermelho com a palavra BOLA acima.” A anterior acrescentava “Limitação da imagem: Não há incertezas relevantes” antes da mesma informação.

## Validação e limites

Os testes automatizados verificam o formato compacto, confiança insuficiente, incertezas relevantes, ausência de cabeçalho e duplicação, compatibilidade com metadados legados, fala de espera sem repetição, cancelamento, níveis, preferências, orientação das câmeras e velocidade de voz. A contagem final de testes e a análise estática ficam em `verificacao.json`.

Ainda há imprecisões factuais: na foto da rua, o modelo usou verbos como “cruza” ou “passando” e algumas formulações ambíguas de quantidade, apesar das instruções. A confiança autodeclarada não resolve esse problema. Texto mais curto não significa precisão visual certificada. As heurísticas de revisão no relatório JSON são apenas indicações, não uma aprovação automática de segurança.

Nenhum Android estava conectado na verificação. Captura física, reprodução sonora, uso real com TalkBack, fila de anúncios e BLE permanecem pendentes. Os testes com leitor simulado e fila de voz não medem a experiência acústica do aparelho. A velocidade e as preferências foram preservadas no código e nas verificações automatizadas.

Saldo, cotas e custo real da conta não foram auditados; não há uma nova tela de consumo de API nesta revisão. Credenciais continuam fora do APK público e dos relatórios. A alteração não modifica chave ou projeto para tentar contornar limites.

## Reproduzir

`verificar.ps1` executa testes locais, análise estática e build sem API. `verificar.ps1 -MedirApi` executa a comparação real opt-in e exige o arquivo local de credencial e as duas imagens de teste. Os testes históricos continuam desativados por padrão, evitando cobranças ou reexecuções inesperadas. Os clientes anteriores preservados ficam somente nas fontes de teste.
