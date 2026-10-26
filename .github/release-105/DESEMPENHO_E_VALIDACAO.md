# Desempenho e validação — Ver+ 1.0.5-mvp (código 17)

26/10/2026. Entrega local de teste. Há correções verificadas no cliente, mas a lentidão do serviço ainda ocorre. Não foi comprovada resolução completa nem redução estável nos três modos.

## Diagnóstico com evidências

A preparação da imagem leva milissegundos; a maior espera observada fica após o envio, entre aguardar o serviço e receber a geração. Como exemplo do ensaio exploratório inicial do Rápido para a rua: preparação 10 ms, fim do envio em 503 ms, cabeçalhos em 9.107 ms, primeira frase completa em 27.237 ms desde a preparação e resposta concluída em 30.931 ms. A API informou 2.046 tokens de entrada e somente 111 de saída, abaixo do teto de 350. O recebimento após os cabeçalhos ocupou 21.809 ms. A coleta externa não separa trânsito de rede, fila interna e inferência no servidor; não há acesso ao painel de operação para atribuir esses intervalos exclusivamente à GPU.

O histórico anterior (1.0.3 → 1.0.4) contém erros HTTP 500 e um timeout de 32,576 s. Na confirmação final, nenhum erro HTTP final foi registrado. Os timeouts estão contados na tabela, inclusive quando a resposta não trouxe conteúdo útil. A chave principal foi aceita em chamadas HTTP 200. Isso não sustenta atribuir a lentidão a uma chave inválida.

Foi identificado e reproduzido um segundo problema no cliente: a versão anterior podia realizar três POSTs e informar apenas duas tentativas quando recebia `503` com `Retry-After: 0`. O reenvio interno da biblioteca somava-se à política do aplicativo. O teste da versão corrigida limita o mesmo cenário a dois POSTs efetivos, com uma medição por tentativa. Esse teste prova a correção do controle de duplicação nesse cenário; não prova que o provedor o provocou nas chamadas reais.

### Modelo, limites e configuração

O modelo principal continua sendo `nvidia/nemotron-3.5-super-vl-120b-a12b`, pela NVIDIA. A alternativa Groq só é habilitada quando o usuário já a configurou. Não há mudança silenciosa de nível ou de provedor. O raciocínio extra permanece desabilitado pelo parâmetro de template já usado anteriormente; o parâmetro duplicado experimentado foi retirado.

As chaves do aparelho continuam protegidas pelo Android Keystore. A chave local usada no ensaio é lida apenas em memória; nenhuma credencial é incluída nos registros, fontes ou APK. A aplicação não envia um identificador de projeto separado nesse fluxo: a associação a conta/projeto pertence à credencial do serviço. Não foi possível auditar o projeto, saldo, contrato ou limites administrativos da conta. Cabeçalhos numéricos de cotas são coletados quando enviados; `-1` significa desconhecido, não cota ilimitada. A ausência de HTTP 429 não exclui fila compartilhada, limitação interna ou capacidade variável.

## Alterações desta revisão

- Uma única política controla os reenvios. POST é marcado como envio único para a biblioteca; reconexões automáticas e redirecionamentos são desabilitados. O aplicativo permite no máximo uma tentativa extra, somente antes de texto útil, para os erros transitórios previstos. Não repete autenticação inválida nem HTTP 429. `Retry-After` positivo impede repetição imediata no mesmo serviço; 501/505 não são tratados como falhas transitórias genéricas.
- Medições por tentativa: preparação do pedido, fila local, DNS, conexão, TLS, envio, espera pelos cabeçalhos, primeiro token, primeira frase completa, fim da geração, tokens, estado HTTP, motivo de término e cotas numéricas disponíveis. Conexão inclui TLS, portanto esses intervalos não devem ser somados como etapas disjuntas.
- Leitura do uso real de tokens no SSE/JSON. O cliente aceita o bloco de uso que pode vir depois de `finish_reason`; a espera opcional por esse bloco é limitada a 100 ms, sem outro timeout longo. Um `[DONE]` isolado não transforma uma geração sem confirmação em sucesso.
- Instruções pessoais redundantes foram reduzidas. O pedido orienta reservar espaço para pontuar a última frase e fechar o JSON, reduzindo detalhes secundários antes de encerrar. A resposta não é cortada localmente para caber. `finish_reason=length` continua sendo interrupção, com aviso e nova tentativa acessível.
- Instrumentação das duas câmeras: conversão e idade do quadro no celular; captura/transferência/decodificação no protótipo; fila e preparação antes do envio. A narração registra entrega à fila, primeiro bloco de síntese e callback de início do mecanismo. Avisos de espera/erro não são contados como início de uma descrição. Os eventos locais `VerMaisLatency` contêm apenas tempos, contagens, níveis e modelos conhecidos, sem imagens, texto da descrição, perguntas, preferências, chaves, URLs ou identificadores de conta/projeto.
- Corrigido o aviso sonoro de erro no fluxo do protótipo quando não há leitor de tela. Com TalkBack detectado, o retorno fica com o leitor. A medição não acrescenta anúncios nem altera a velocidade ou a voz escolhida.

O fluxo progressivo por frases completas, a validação prévia de confiança/limitações, o cancelamento por geração, o bloqueio de toques duplicados, a reutilização do cliente, a suspensão da conversão contínua durante o pedido e a fila de voz sem repetição já existiam na 1.0.4 e foram mantidos/retestados.

## Limites por modalidade e teste isolado

| Modo | Limite total de saída | Entrada observada pela API | Saída observada pela API |
|---|---:|---:|---:|
| Rápido | 350 | 1569–2027 | 106–147 |
| Médio | 500 | 1567–2025 | 112–155 |
| Detalhado | 750 | 1573–2031 | 133–213 |

Os limites de 350/500/750 já estavam configurados na 1.0.4; foram mantidos após esta rodada. Incluem os metadados, além do texto falado. Rápido pede 1–2 frases e cerca de 35 palavras; Médio, 2–3 frases e cerca de 65; Detalhado, 4–6 frases e cerca de 110. A escolha continua salva e enviada em todas as tentativas. São instruções ao modelo, não um truncamento do texto nem garantia de que ele seguirá exatamente as contagens.

No ensaio exploratório inicial, o controle elevou `max_tokens` para 650/850/1.100, mantendo imagem, modelo, instruções de conteúdo e transmissão progressiva. Foram 12 chamadas de controle, intercaladas com os dois clientes. O controle usa uma tentativa; comparações causais excluem respostas atuais com repetição. Restaram 8 pares aceitos com uma única tentativa de cada lado. As conexões são reutilizadas em cada variante, com ordem invertida na segunda rodada. O cliente de controle é um executor direto de HTTP; a amostra não elimina diferenças de conexão, tentativas e carga do serviço.

Houve 0 términos `length` na variante candidata do experimento inicial. Na confirmação final, foram obtidas contagens reais de saída em 11 tentativas atuais. Tempos oscilam fortemente entre chamadas, inclusive com saída muito abaixo do limite. Esta amostra não comprova que diminuir o teto tornou o serviço mais rápido. O teto limita a geração possível; não deve ser apresentado como a causa resolvida. O preço efetivo e a cobrança das tentativas que terminaram sem uso informado não estão disponíveis.

## Comparação antes e depois

Foram realizadas 36 chamadas exploratórias: 12 com cliente 1.0.4, 12 com a primeira variante candidata e 12 com teto maior. Essa variante piorou a mediana do primeiro conteúdo nos três modos: Rápido 4,39 → 26,93 s; Médio 5,92 → 9,11 s; Detalhado 5,43 → 12,73 s. Não se atribuiu a piora a um parâmetro isolado nem se omitiu a rodada. Foram retirados o parâmetro de raciocínio duplicado e a instrução experimental de contar um número explícito de tokens; permaneceu a orientação simples de concluir frases e o JSON. As demais correções de reenvio e medição foram mantidas.

A tabela abaixo usa uma **confirmação separada com 24 novas chamadas**: cliente 1.0.4 preservado contra a revisão final 1.0.5, nas duas cenas fixas, nos três modos e em duas rodadas, invertendo a ordem antes/depois. A rua é uma [imagem pública de exemplo da NVIDIA](https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1a.jpg); a outra cena tem figuras e etiquetas sintéticas. Nenhuma foto pessoal foi enviada. Confirmação final: `matriz-final-api.json` e `resumo-final-medicoes.json`. Experimento inicial completo, incluindo pioras: `matriz-api.json` e `resumo-medicoes.json`. Histórico separado: `historico-1.0.3-1.0.4.json`.

Medianas das respostas aceitas pelo formato/confiança, somando as duas cenas. Aceitação técnica não certifica verdade visual. Resultados incompletos e falhas não entram nos tempos, mas permanecem na contagem. Não são medidas de captura física, som real ou TalkBack. A contagem de prazo inclui timeouts identificados na exceção ou na medição por tentativa; no cliente anterior, uma falha parcial devolvida ao esgotar 48 s também conta como orçamento esgotado, sem inferir a causa interna. O relatório JSON separa essas classificações medidas e inferidas pelo orçamento. O erro parcial pode encobrir o tipo de causa no campo original `error_type`; a versão do ensaio entregue já percorre a cadeia de causas para futuras execuções.

| Modo | Primeiro conteúdo útil antes → depois | Conclusão antes → depois | Respostas aceitas antes → depois | Falhas por prazo antes → depois |
|---|---:|---:|---:|---:|
| Rápido | 17,35 s → 10,29 s | 18,67 s → 10,66 s | 4/4 → 4/4 | 0 → 0 |
| Médio | 6,32 s → 3,63 s | 8,18 s → 4,54 s | 4/4 → 3/4 | 0 → 1 |
| Detalhado | 5,13 s → 5,49 s | 11,24 s → 9,49 s | 3/4 → 4/4 | 1 → 0 |

Separação por cena (primeiro conteúdo / conclusão; aceitas / tentativas):

| Cena | Modo | Antes | Depois |
|---|---|---:|---:|
| Rua | Rápido | 26,39 s / 27,61 s (2/2) | 10,94 s / 10,94 s (2/2) |
| Rua | Médio | 16,04 s / 18,73 s (2/2) | 6,07 s / 7,45 s (1/2) |
| Rua | Detalhado | 6,89 s / 12,68 s (2/2) | 10,70 s / 12,72 s (2/2) |
| Figuras e etiquetas | Rápido | 8,97 s / 12,73 s (2/2) | 9,96 s / 10,66 s (2/2) |
| Figuras e etiquetas | Médio | 4,89 s / 6,40 s (2/2) | 3,21 s / 4,27 s (2/2) |
| Figuras e etiquetas | Detalhado | 2,88 s / 6,42 s (1/2) | 2,78 s / 6,06 s (2/2) |

“Primeiro conteúdo útil” é uma frase completa liberada pelo parser após validar os metadados; não é o primeiro token. O cronômetro do ensaio começa no bitmap já disponível. A API pode continuar inferindo após o cliente cancelar; as medidas do cliente não provam a ausência de fila no servidor. O orçamento de chamadas segue em 48 s e a proteção da interface em 52 s; não foi aumentado para produzir uma melhora aparente.

### Avaliação de outro modelo

Foram executadas 6 chamadas exploratórias com `nvidia/nemotron-nano-12b-v2-vl`, nas mesmas cenas. Foram obtidas 0 descrições aceitas tecnicamente. Os resultados brutos estão em `modelo-candidato.json`. O serviço respondeu HTTP 410 em todas as chamadas: o candidato estava indisponível nesse endpoint. Não foi possível medir sua velocidade, qualidade ou custo. O modelo não foi adotado. Faltam acesso funcional, auditoria factual ampliada, cotação/custo real e validação de acessibilidade em aparelho.

## Qualidade, narração e acessibilidade

As imagens continuam limitadas a 1600 px, JPEG 84; acima de 1 MB há segunda compressão em 76, e acima de 1,5 MB há erro claro. As imagens da nova comparação têm os mesmos bytes antes/depois: 147.863 bytes (rua, 1300×876) e 16.218 bytes (figuras, 960×720). Não foi adotada redução adicional de resolução: a preparação já ficou na ordem de milissegundos e detalhes pequenos exigem validação visual mais ampla. A medição histórica de JPEG 90 → 84 reduziu 161.820 para 147.863 bytes (8,6%); não demonstrou aceleração mensurável de preparação.

Os testes de integração percorrem bitmap → HTTP/SSE → tela/fila de voz, nos três modos, com preferências e velocidade 1,5×. Verificam cancelamento, recuperação, ausência de pedidos duplicados e ausência de repetição do texto já narrado. O leitor de tela é simulado nesses testes; isso não executa o serviço TalkBack.

Persistiram falhas factuais do modelo principal: respostas atuais para a foto da rua afirmaram carro “em movimento” e pessoa “caminhando”, apesar da regra para não inferir movimento a partir de foto. Algumas formulações de quantidade/posição também exigem revisão. A confiança autodeclarada não elimina esses erros. Os tempos “aceitos” da tabela não devem ser confundidos com aprovação factual ou garantia de orientação segura.

Não foi medido início sonoro real: não há Android conectado nem imagem de emulador disponível. `voice_start_callback_ms` é callback do TTS, não medição acústica. `synthesis_callback_ms` marca o primeiro áudio de síntese; não é reprodução concluída. Com TalkBack, o aplicativo não pode medir o início da fala do serviço por esses callbacks. Não se inventa um valor de narração a partir da primeira frase recebida.

## Pendências para validar a experiência completa

1. Android físico: captura até primeira frase, primeira síntese, início sonoro e término da voz; três modos, perguntas, frontal/traseira, rede estável/lenta e protótipo BLE quando disponível. Repetir com voz local e a voz já escolhida pelo usuário, sem alterar sua preferência silenciosamente.
2. TalkBack real: navegação/foco, espera, erro, parar, nova captura, interrupção e fila de trechos; conferir perda por agrupamento de anúncios e sobreposição. As verificações automatizadas de semântica não certificam esse comportamento.
3. Conta do serviço: confirmar projeto associado, quotas, preço, concorrência e capacidade/filas no painel. Nenhuma alteração de chave, projeto ou saldo foi feita como suposta correção.
4. Ampliar cenas reais, contraste, pequenos rótulos e obstáculos; revisão factual independente e mais repetições. Só depois considerar troca de modelo ou novas reduções de imagem/limites.

## Reprodução e arquivos

`verificar.ps1`: testes locais, análise estática e APK, sem API. `verificar.ps1 -ConfirmarApi`: comparação final de 24 chamadas; `-MedirApi`: matriz de 36 chamadas com controle de teto maior. Requerem credencial local e cenas de teste. `verificar.ps1 -AvaliarModelo`: ensaio exploratório do modelo menor, sem alterar o aplicativo. Os ensaios reais não são reaproveitados do cache de testes. O ambiente não incorpora credencial ao build. `empacotar.py` verifica os relatórios e procura os valores conhecidos das credenciais locais nos artefatos, sem imprimi-los. A entrega final registra a contagem de testes, análise estática e hashes em `verificacao.json`.

Referências técnicas consultadas: [API do modelo principal: streaming, uso e limite de tokens](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3_5-super-vl-120b-a12b-infer), [API do modelo candidato](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-nano-12b-v2-vl-infer) e [observabilidade administrativa da NVIDIA](https://docs.nvidia.com/nvcf/overview/managed-observability). O serviço documenta que o teto interrompe a geração; por isso são necessárias instruções de fechamento e validação de término.
