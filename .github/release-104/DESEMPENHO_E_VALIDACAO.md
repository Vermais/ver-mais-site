# Desempenho e validação — Ver+ 1.0.4-mvp (código 16)

Entrega de 26/10/2026. As alterações estão no projeto Android existente. Esta entrega é uma versão para validação. A validação integral em aparelho ainda está pendente; não foi comprovada entrega consistente em todas as condições.

## Causa encontrada

O cliente anterior solicitava `stream=false` e esperava o corpo JSON inteiro. A tela e a narração só recebiam o resultado após o fim da geração. O Detalhado permitia 1.100 tokens, até oito frases e 160 palavras; também havia repetição de orientações. Isso aumenta o trabalho possível, mas o tamanho não explica sozinho as falhas.

A API principal apresentou HTTP 500 repetidamente, tanto antes quanto depois. Houve também um timeout real de 32,58 s no cliente anterior, no modo Rápido. Portanto, o problema não é exclusivo do Detalhado. Com apenas uma configuração de serviço, o cliente anterior não repetia uma falha transitória. Os limites por chamada eram 34 s (leitura de 32 s), orçamento de tentativas de 50 s e proteção da interface de 55 s.

A imagem era JPEG 90, limitada a 1600 px. A preparação concorria com conversões periódicas de novos quadros. No fluxo do protótipo, criar um cliente por captura impedia reaproveitar conexões. A captura e transferência BLE possuem uma espera própria, anterior à IA; sem o protótipo físico, sua duração não foi medida.

## Alterações

- Recebimento progressivo via SSE. Só são liberadas frases completas, após validar os metadados, sua coerência e a confiança mínima já usada pelo aplicativo (0,68). As limitações declaradas são apresentadas antes do primeiro trecho. Metadados ausentes/contraditórios, confiança baixa e frases incompletas não são narrados progressivamente. O final ainda é validado; se falhar depois de um trecho, a descrição é identificada como interrompida, sem misturar outra resposta.
- Fila de voz recebe apenas o trecho novo. A conclusão não repete tudo. Fragmentos aguardam a inicialização do mecanismo sem se perderem. A velocidade salva é aplicada a cada fala. O conteúdo não é resumido para falar mais rápido.
- Cancelamento por geração e bloqueio de pedidos simultâneos. Uma nova sessão ou saída da tela invalida resultados anteriores. Não há retomada automática com outra cena após um trecho já entregue.
- Imagem até 1600 px em todos os níveis, JPEG 84. Acima de 1 MB, uma segunda compressão usa 76; acima de 1,5 MB há erro claro, sem envio excessivo. Não se espelha a imagem nem se corta seu enquadramento para acelerar. A conversão periódica de quadros é suspensa enquanto há uma descrição em andamento. Mantém-se o cliente durante a sessão.
- Rápida: 350 tokens, uma ou duas frases, cerca de 35 palavras, foco no essencial e prioridades. Média: 500 tokens, duas ou três frases, cerca de 65 palavras, contexto necessário. Detalhada: 750 tokens, quatro a seis frases, cerca de 110 palavras, contexto e relações/detalhes úteis. São orientações ao modelo, que pode não segui-las perfeitamente; não há corte local que esconda alertas. Preferências e pergunta continuam combinadas, subordinadas à evidência e à segurança.
- Uma tentativa extra para falha transitória de transporte/servidor, somente antes de qualquer trecho útil. No máximo duas tentativas, incluindo alternativa explicitamente configurada. Não se repete automaticamente a mesma credencial inválida ou um limite 429.
- Novo orçamento total de 48 s, leitura ociosa de 20 s, conexão de 4 s e envio de 8 s. A chamada pode continuar recebendo trechos além dos antigos 34 s, mas as tentativas compartilham os 48 s e a interface tem proteção de 52 s. Isso dá espaço a uma geração ativa sem simplesmente ampliar a espera total anterior de 50/55 s.
- Estado de preparação acessível, um único aviso adicional de espera, botão **Tentar novamente** após falha e liberação dos controles. A nova tentativa captura uma imagem atual. A descrição automática pausa após falha, evitando repetição indefinida.
- Com leitor de tela detectado, a voz automática do aplicativo é suprimida. Os trechos novos e os erros usam retorno acessível, sem anunciar novamente o texto acumulado. Navegar para outro controle interrompe a voz e silencia os próximos anúncios daquela solicitação. A ação de parar permanece disponível.

## Medição real da API

Foram executadas 12 chamadas na última comparação: dois testes por nível e versão, alternando antes/depois e invertendo a ordem na segunda rodada. Mesmo provedor NVIDIA/modelo, mesma pergunta e preferências, mesma cena pública. O cliente anterior foi preservado nos testes; o atual usou a implementação do aplicativo. Não foram enviadas fotos pessoais. Credenciais não constam dos relatórios nem do APK.

Cena pública usada: [exemplo de visão hospedado pela NVIDIA](https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1a.jpg). O ensaio roda no computador com as classes Android de imagem em Robolectric. Inclui preparação JPEG e chamada real, desde o bitmap em memória. Exclui captura física, transferência BLE, reprodução sonora e serviço TalkBack. Os tempos não são uma medição completa de uso no celular.

“Primeiro útil” significa primeira frase completa aprovada pelo formato/confiança do aplicativo; não é uma certificação de verdade da descrição. Respostas de baixa confiança e falhas são excluídas das médias e estão contadas na última coluna.

| Nível | Primeiro útil antes | Primeiro útil depois | Texto completo antes | Texto completo depois | Entregas aceitas antes → depois |
|---|---:|---:|---:|---:|---:|
| Rápida | nenhuma | 3,33 s | nenhuma | 3,59 s | 0/2 → 2/2 |
| Média | 6,59 s | 2,85 s | 6,59 s | 3,45 s | 2/2 → 1/2 |
| Detalhada | 3,99 s | 3,45 s | 3,99 s | 4,44 s | 1/2 → 2/2 |

Médias somente das entregas aceitas, amostra muito pequena e com quantidades diferentes. Não comprovam redução estável, confiabilidade em produção ou um prazo garantido. A conclusão do Detalhado ficou mais lenta nesta rodada, embora a primeira frase tenha chegado antes.

| Rodada | Nível | Antes: primeiro / total | Depois: primeiro / total | Falhas |
|---|---|---:|---:|---|
| 1 | Rápida | — / 3,678 s | 2,163 / 2,405 s | Antes: confiança 0, resposta segura sem descrição |
| 1 | Média | 10,665 / 10,665 s | — / 3,079 s | Depois: HTTP 500 nas duas tentativas |
| 1 | Detalhada | — / 1,696 s | 3,910 / 4,812 s | Antes: HTTP 500 |
| 2 | Rápida | — / 32,576 s | 4,505 / 4,769 s | Antes: timeout |
| 2 | Média | 2,522 / 2,522 s | 2,853 / 3,452 s | Nenhuma falha de entrega |
| 2 | Detalhada | 3,990 / 3,990 s | 2,992 / 4,073 s | Nenhuma falha de entrega |

Preparação da imagem: antes 9–24 ms, depois 10–27 ms nesta cena. A compressão não mostrou ganho de tempo mensurável; sua contribuição aqui foi reduzir o JPEG de 161.820 para 147.863 bytes (8,6%), mantendo dimensões. Nas cinco entregas atuais, o fim do envio ocorreu em aproximadamente 0,53–0,57 s desde o início da chamada; os primeiros tokens chegaram em 1,47–3,49 s. Isso aponta a espera pelo serviço/geração como maior componente nesta cena, sem isolar rede de inferência no servidor.

Os textos reais e cada evento parcial estão em `api-comparacao-java.json`. As rodadas exploratórias anteriores ficam separadas em `ensaios`; não foram selecionadas apenas as respostas mais rápidas.

## Narração e acessibilidade

A entrega à fila de voz agora ocorre no primeiro trecho coerente, em vez de aguardar o resultado completo. Os testes de integração verificam tela → preparação da imagem → HTTP/SSE → fila de voz, nos três níveis, com preferências pessoais e velocidade 1,5×. Também verificam ausência de duplicação, supressão da voz com leitor detectado e recuperação após erro/timeout.

O callback de início da voz registra o tempo no aplicativo para permitir medir em aparelho. **O tempo até o som real, antes e depois, não foi medido:** não há Android conectado nem emulador compatível disponível. Não se usa o instante de envio à fila como se fosse o início audível.

O TalkBack não foi executado. As verificações de semântica/estado e os testes com detecção simulada de leitor não comprovam os gestos, a sequência real de anúncios, eventual agrupamento de trechos pelo TalkBack ou ausência de sobreposição sonora em aparelho.

## Qualidade e pendências

A compressão foi verificada com imagem sintética de objetos/etiquetas à esquerda e à direita, preservando dimensão, contraste e posição. A orientação, preferências e níveis têm testes de regressão. Isso não substitui comparação de detalhes pequenos em fotos reais.

A API ainda apresentou imprecisões: em respostas anteriores e atuais, inferiu movimento de pessoas/carros a partir de uma foto, contrariando as instruções. A autoavaliação de confiança não elimina esse problema. Não se certificou a precisão visual nem a preservação integral da qualidade em todas as cenas.

Antes de considerar o problema resolvido, faltam:
1. Medir captura → primeiro retorno → som real em Android, com os três níveis, câmeras frontal/traseira e, quando disponível, protótipo BLE.
2. Usar TalkBack de verdade para testar espera, interrupção, erro, nova tentativa, preferências e velocidade; confirmar que a fila de anúncios não perde trechos nem se sobrepõe à voz.
3. Ampliar o ensaio real com cenas variadas, detalhes pequenos, redes lentas/instáveis e mais repetições; o HTTP 500 persistiu em uma chamada atual apesar da tentativa extra.
4. Revisar a qualidade factual, em especial movimento e afirmações sobre obstáculos. Não é adequado declarar a consistência ou acessibilidade completa com a amostra atual.

## Reproduzir

`verificar.ps1` executa testes locais, análise estática e compilação. A comparação real é opt-in com `-MedirApi`; requer o arquivo local de credencial e a cena pública no diretório da entrega. No teste portátil, configure `VERMAIS_RUN_BENCHMARK=1`, `VERMAIS_BENCHMARK_DIR` e `VERMAIS_BENCHMARK_KEY_FILE` (arquivo no formato NVIDIA_API_KEY=...). A chave nunca deve ser incluída nas fontes ou no APK público. Os testes locais não acessam a API por padrão.

