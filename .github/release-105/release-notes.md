Versão de teste para Android 9 ou superior.

Correção de reenvios ocultos de pedidos, medições por etapa e por tentativa, leitura do uso real de tokens quando informado pelo serviço e instruções para concluir frases e o JSON. Mantém descrição progressiva, nível escolhido, preferências pessoais e velocidade de voz. Corrige também o aviso de erro por voz no fluxo do protótipo.

Limites totais de saída: Rápida 350, Média 500 e Detalhada 750 tokens. **O aplicativo ainda não tem uma tela de consumo da API**: os tokens ficam nos registros técnicos; saldo e custo não são exibidos.

138 testes locais aprovados; análise estática sem erros e com 101 avisos. Foram realizadas 60 chamadas reais de comparação. Na confirmação final, as medianas até o primeiro conteúdo foram 17,35 → 10,29 s (Rápida), 6,32 → 3,63 s (Média) e 5,13 → 5,49 s (Detalhada), somente entre respostas concluídas. Houve uma falha por prazo em cada versão. As rodadas exploratórias com piora foram preservadas no relatório. Não foi comprovada redução estável da demora nem que reduzir o teto de tokens acelere o serviço.

**Pendências:** captura física, início sonoro real, BLE e TalkBack em Android, cotas/projeto/custo da conta e validação factual ampliada. Persistem imprecisões do modelo e falhas por prazo. O modelo menor avaliado estava indisponível (HTTP 410) e não foi adotado.

O APK usa o mesmo certificado da versão 1.0.4 e não contém chave pessoal de IA. O relatório anexado detalha os testes e suas limitações.

SHA-256: `5e5e45af5f283abc33cd100a4a38508bb85a04d38474e7b4696ee48d0deb8f08`
