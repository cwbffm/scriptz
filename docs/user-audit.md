# Auditoria de usuários locais em servidores Windows

## Objetivo

O script [audit-local-users.ps1](../audit-local-users.ps1) coleta usuários locais de servidores Windows e gera relatórios CSV. Os servidores podem vir de uma OU do Active Directory ou de uma lista CSV.

## Requisitos

- PowerShell 5.1 ou versão compatível com os módulos utilizados.
- Módulo `ActiveDirectory` / RSAT quando a origem for uma OU.
- WinRM habilitado nos destinos Windows e acesso de rede à porta utilizada, normalmente 5985 ou 5986.
- Conta com permissão para consultar os computadores e executar os comandos remotos necessários.
- Diretório local gravável para os arquivos de saída.

## Configuração

Edite a seção `CONFIG` no arquivo antes de executar.

| Parâmetro | Uso |
| --- | --- |
| `$UseAD_OrganizationalUnit` | `$true` usa a OU; `$false` usa CSV |
| `$AD_OrganizationalUnitDN` | DN da OU, por exemplo `OU=Servers,DC=example,DC=local` |
| `$InputCsvPath` | Caminho da lista CSV; utilize o campo `Server` esperado pelo script |
| `$InputCsvDelimiter` | Separador da lista, `;` por padrão |
| `$OutputUsersCsvPath` | Destino do relatório de usuários |
| `$OutputTriageCsvPath` | Destino do relatório de triagem e falhas |
| `$WorkDir` | Diretório local de trabalho |
| `$TcpTimeoutMs` | Tempo de espera da sondagem TCP |

Exemplo de lista de entrada:

```csv
Server;Status
srv-app01;Enabled
srv-db01;Enabled
```

## Execução

Execute o arquivo completo para que as credenciais e funções sejam inicializadas:

```powershell
.\audit-local-users.ps1
```

A credencial é solicitada pelo PowerShell durante a execução. Ajuste a origem e o escopo para consultar apenas os servidores pretendidos.

## Resultado esperado

| Arquivo padrão | Conteúdo |
| --- | --- |
| `C:\Temp\Local_Users_Report.csv` | Usuários dos hosts Windows consultados com sucesso |
| `C:\Temp\Hosts_Triage_Report.csv` | Hosts não consultados, falhas de WinRM e resultados da sondagem de portas |

O console apresenta contadores e a duração ao final. Revise o relatório de triagem junto com o relatório de usuários para identificar servidores que ficaram sem coleta.

## Limites da triagem

A implementação testa TCP/3389 antes de tentar WinRM. Um Windows com WinRM disponível e RDP fechado pode ficar fora da coleta por causa dessa condição. Na ausência de RDP, uma resposta em TCP/22 é registrada como indício de host Linux; isso não comprova o sistema operacional.

Esses comportamentos fazem parte da implementação atual. Os relatórios devem ser interpretados como os resultados da coleta realizada, e não como garantia de cobertura de todos os servidores.

## Origem

Consulte [Origem e contribuições](../CONTRIBUTIONS.md) para o contexto do fork e a atribuição dos materiais. Este guia documenta o script existente, sem alterar sua lógica.
