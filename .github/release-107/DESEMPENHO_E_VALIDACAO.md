# Ver+ 1.0.7 — descrições com mais contexto

27/10/2026. Versão de teste, código 19. A revisão corrige o excesso de concisão da 1.0.6: acrescenta contexto e detalhes úteis, sobretudo nos níveis Média e Detalhada. O formato compacto de resposta e as melhorias contra repetições foram preservados.

## Ajuste realizado

- **Rápida:** orientação para duas frases diretas, cerca de 30–45 palavras quando a cena permitir, com assunto principal, posição e contexto essencial.
- **Média:** três ou quatro frases naturais, cerca de 50–80 palavras quando houver conteúdo suficiente, incluindo distribuição, cores e relações relevantes.
- **Detalhada:** cinco ou seis frases naturais, cerca de 90–130 palavras quando a cena permitir, com visão geral, primeiro plano, fundo e detalhes úteis às prioridades pessoais.

Essas faixas são orientações, não contagens obrigatórias: a IA não deve inventar, repetir ou preencher texto em cenas simples. A aplicação não trunca localmente a descrição para atingir um tamanho. O nível, as preferências pessoais e a velocidade de voz continuam salvos. Não houve mudança silenciosa de modalidade.

A instrução geral passou a favorecer uma imagem mental mais completa do ambiente. Os campos continuam sendo `confianca`, `incertezas` e `frase`, com validação antes da primeira frase progressiva. Cabeçalhos genéricos de limitação e falas repetidas de espera não foram reintroduzidos. Incertezas relevantes e avisos de interrupção continuam disponíveis.

Os tetos totais de saída permanecem **240 / 360 / 560 tokens**, pois já comportam as descrições mais completas do novo ensaio. Não foi necessário aumentar os limites de espera ou trocar o modelo/serviço. Câmeras, JPEG/resolução, funcionamento offline, voz e configurações foram preservados.

## Comparação real com a 1.0.6

24 chamadas sequenciais: dois cenários fixos, três níveis, duas rodadas e duas versões. A ordem foi invertida na segunda rodada. Foi preservado o cliente 1.0.6 nas fontes de teste. As chamadas usaram o mesmo modelo NVIDIA, pergunta/preferência de teste e os mesmos JPEGs. As imagens são o [exemplo público da NVIDIA](https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1a.jpg) e figuras sintéticas com etiquetas; nenhuma foto pessoal foi enviada.

Medianas de respostas aceitas pelo formato e confiança. Isso não certifica a verdade visual. Os tempos começam com a imagem disponível em memória e excluem captura física e início sonoro real.

| Modo | Palavras antes → depois | Primeiro trecho antes → depois | Texto concluído antes → depois | Aceitas |
|---|---:|---:|---:|---:|
| Rápida | 22,5 → 32,0 | 1,95 s → 1,22 s | 2,11 s → 1,36 s | 4/4 → 4/4 |
| Média | 25,5 → 46,0 | 1,36 s → 1,50 s | 1,45 s → 1,75 s | 4/4 → 4/4 |
| Detalhada | 43,0 → 78,5 | 1,64 s → 1,38 s | 2,08 s → 1,94 s | 4/4 → 4/4 |

Nos 12 resultados atuais, a Rápida teve 27–37 palavras, a Média 28–68 e a Detalhada 53–88. As cenas simples não foram obrigadas a atingir os tamanhos sugeridos. Não houve timeout, corte por limite de tokens ou cabeçalho automático de limitação nesta rodada. O primeiro trecho da Média ficou ligeiramente mais lento; a amostra é pequena e não prova estabilidade de latência. A comparação completa fica em `comparacao-equilibrada.json`; estatísticas em `resumo-comparacao.json`.

Na cena da rua, a descrição Média passou a incluir a placa STOP, o poste, o portão, os leões, a posição do carro e a pessoa no fundo. A Detalhada acrescentou lojas, lanternas, árvore e elementos do primeiro plano. Isso representa mais conteúdo, em vez de alongar a resposta com comentários sobre a análise.

## Verificação e limitações

Os testes locais abrangem envio dos níveis/preferências, validação do formato compacto e legado, incertezas, ausência de repetição, cancelamento, recuperação, orientação, persistência e fila de voz. A contagem final, assinatura e hashes estão em `verificacao.json`. A leitura de textos e cores offline não foi resumida.

Continuam pendentes os testes práticos de captura, início audível, BLE e TalkBack em Android. Os testes automatizados usam leitor de tela e voz simulados. O modelo ainda pode inferir movimento ou formular quantidades ambíguas, como ocorreu na foto da rua; confiança autodeclarada não é garantia de precisão. Esta revisão ajusta a profundidade das descrições e não certifica segurança de navegação.

O uso da API pode oscilar mesmo com o texto ajustado. Não houve alteração de chave, projeto ou cobrança, nem nova tela de consumo. Credenciais continuam fora das fontes públicas, registros e APK.

## Reproduzir

`verificar.ps1` executa testes locais, análise estática e build sem API. `verificar.ps1 -MedirApi` executa o comparativo real opt-in e exige o arquivo local de credencial e as imagens de teste. O modelo principal e o mecanismo de transmissão progressiva são os mesmos da 1.0.6.
