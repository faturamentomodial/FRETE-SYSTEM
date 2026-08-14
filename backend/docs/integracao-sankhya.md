# Integração Sankhya → FRETEWAY

## Endpoint de cotação

`POST /integrations/sankhya/cotacao` (também disponível sob `/api/v1`)

Autenticação: header `X-API-Key`, cujo valor deve ser configurado no backend pela
variável `SANKHYA_API_KEY`. A chamada é síncrona: a resposta só é entregue depois
que as transportadoras terminarem ou atingirem seu timeout individual.

```json
{
  "origem": {"cep": "01001000", "cidade": "São Paulo", "uf": "SP"},
  "destino": {"cep": "30110000", "cidade": "Belo Horizonte", "uf": "MG"},
  "itens": [{
    "quantidade": 2, "peso_kg": 12.5,
    "comprimento_cm": 50, "largura_cm": 40, "altura_cm": 30,
    "valor": 3390.5
  }],
  "valor_mercadoria": 6781,
  "numero_pedido": "21259",
  "tipo_entrega": "MODIAL ENTREGA",
  "tipo_transporte": "FRETE INCLUSO NA NOTA FISCAL"
}
```

Também é possível enviar `volume_m3` no lugar das três dimensões. `peso_kg` é
unitário e o FRETEWAY multiplica peso e volume pela quantidade.

Cada item de `linhas` na resposta contém os campos da grid: `id_container`,
`codigo_parceiro_transportadora`, `nome_parceiro`, `prazo_entrega`,
`valor_cotacao`, `aprovado` (sempre nulo), `codigo_servico`, `servico`,
`transportadora` e `erro`.

Uma falha de transportadora não retorna erro HTTP para a operação inteira. Ela
gera uma linha com `status=error` ou `timeout` e texto em `erro`. Transportadora
sem de-para também gera linha, com código de parceiro vazio e o erro
`TRANSPORTADORA_SEM_DE_PARA`.

Depois do cálculo, o FRETEWAY autentica no Gateway e grava as linhas. A integração
global `sankhya` deve conter credenciais criptografadas `client_id`,
`client_secret` e `x_token`. A configuração não sensível aceita:

```json
{
  "ambiente": "homologacao",
  "base_url": "https://api.sandbox.sankhya.com.br",
  "modo": "anexar",
  "entidade_pedido": "CabecalhoNota",
  "campo_numero_pedido": "NUMPEDIDO",
  "entidade_cotacao": "ENTIDADE_CONFIRMADA_NO_DICIONARIO",
  "campos_cotacao": {
    "pedido": "CAMPO_PEDIDO",
    "id_container": "CAMPO_CONTAINER",
    "codigo_parceiro": "CAMPO_CODPARC",
    "prazo": "CAMPO_PRAZO",
    "valor": "CAMPO_VALOR",
    "aprovado": "CAMPO_APROVADO",
    "codigo_servico": "CAMPO_CODSERV",
    "servico": "CAMPO_SERVICO",
    "transportadora": "CAMPO_TRANSPORTADORA",
    "erro": "CAMPO_ERRO"
  }
}
```

O token OAuth2 fica em cache respeitando `expires_in`; respostas 401 forçam uma
renovação. Falhas de rede, HTTP 429 e HTTP 5xx recebem até três tentativas com
backoff. Segredos nunca são incluídos em logs ou respostas.

## De-para de transportadoras

Usuários autenticados no FRETEWAY podem consultar e salvar mapeamentos:

- `GET /api/v1/integrations/sankhya/mapeamentos`
- `PUT /api/v1/integrations/sankhya/mapeamentos/{transportadora_id}`

O `PUT` recebe `transportadora_id`, `codigo_parceiro`, `nome_parceiro` e,
opcionalmente, `codigo_servico`, `servico` e `ativo`.

## Ação no Sankhya

Criar uma nova ação chamada **Gerar Cotação de Frete — Automática (FRETEWAY)** e
preservar a ação/manual e os botões nativos da grade. A customização deve:

1. validar que o pedido foi salvo e coletar cabeçalho, parceiro e itens;
2. ativar o indicador de carregamento;
3. chamar o endpoint com timeout superior ao `TIMEOUT_API_INTEGRACAO`;
4. para cada item de `linhas`, inserir uma linha na entidade de cotação vinculada
   ao `NUNOTA`, usando os nomes físicos confirmados no dicionário de dados;
5. manter `Aprovado` nulo e atualizar a grade;
6. em falha HTTP, preservar todas as linhas existentes e oferecer a ação manual.

Até a confirmação da regra, a ação deve **anexar** as respostas automáticas e
nunca excluir linhas manuais. Para evitar duplicação em cliques repetidos,
recomenda-se guardar `request_id`/origem FRETEWAY em campos adicionais ou pedir
confirmação antes de repetir a importação.

O nome físico da tabela e dos campos deve ser validado no ambiente do cliente;
`TGFCOT` não deve ser assumida sem essa conferência, pois pode variar conforme a
versão e customizações do Sankhya.
