# Scriptz — Administração e Automação

Coleção de scripts, adaptações e guias para administração de Linux, Windows, AWS, redes, backups e serviços de infraestrutura.

Este repositório é um **fork de [charles-josiah/scriptz](https://github.com/charles-josiah/scriptz)**. Os créditos dos materiais estão nos arquivos e em [Origem e contribuições](CONTRIBUTIONS.md). A documentação do usuário restrito no Linux identifica uma colaboração entre Charles Josiah e Fabio Ferreira.

## Por onde começar

| Material | Finalidade | Documentação |
| --- | --- | --- |
| [Auditoria de usuários Windows](audit-local-users.ps1) | Inventário de usuários locais e relatórios de triagem | [Guia de execução](docs/user-audit.md) |
| [Usuário restrito no Linux](create-restricted-user.sh) | Criação de usuário com shell restrito e comandos permitidos | [Guia e limitações](create-restricted-user.md) |
| [Docker no Ubuntu 24.04](howto-install-docker-ubuntu-2404.md) | Instalação e preparação do ambiente | Guia no próprio arquivo |
| [Rotinas AWS](aws/README.md) | Operações em EC2, EBS, RDS, ECR, S3 e Route 53 | Catálogo por finalidade e impacto |

## Requisitos por tipo de material

| Área | Requisitos a conferir |
| --- | --- |
| PowerShell / Windows | Versão do PowerShell e módulos exigidos; a auditoria usa WinRM e, no modo OU, o módulo ActiveDirectory |
| Bash / Linux | Bash e utilitários chamados pelo script; operações administrativas podem exigir root ou sudo |
| AWS | AWS CLI ou bibliotecas Python utilizadas pelo arquivo, credenciais locais e permissões para as operações selecionadas |
| Perl / LDAP | Perl, módulos adicionais quando usados e um arquivo ou servidor LDAP conforme a rotina |
| Zimbra | Ferramentas administrativas do Zimbra e contexto de execução compatível com a instalação |
| Redes e backups | Acesso aos equipamentos ou servidores de destino, dependências como Expect e diretórios de backup configurados |

Alguns materiais são legados e foram escritos para problemas específicos. Compatibilidade de versões, parâmetros e dependências deve ser verificada no arquivo escolhido. Este catálogo descreve a finalidade dos materiais; ele não representa uma validação de todos os scripts em ambientes atuais.

## Exemplo: auditoria de usuários Windows

1. Abra [audit-local-users.ps1](audit-local-users.ps1) e revise a seção `CONFIG`.
2. Escolha a origem dos servidores: OU do Active Directory ou arquivo CSV.
3. Ajuste os caminhos dos relatórios e confirme os pré-requisitos do [guia](docs/user-audit.md).
4. Execute o script completo no PowerShell com uma conta autorizada a consultar os servidores.

```powershell
.\audit-local-users.ps1
```

O script solicita a credencial e grava, por padrão, `C:\Temp\Local_Users_Report.csv` e `C:\Temp\Hosts_Triage_Report.csv`. O primeiro contém usuários dos hosts Windows consultados com sucesso; o segundo registra falhas e resultados da triagem.

## Catálogo

### Windows e administração Linux

| Arquivo | Finalidade |
| --- | --- |
| [audit-local-users.ps1](audit-local-users.ps1) | Consulta remota de usuários locais em servidores Windows, a partir de OU ou CSV |
| [create_users.md](create_users.md) | Guia de criação de usuários em lote no Active Directory |
| [create-restricted-user.sh](create-restricted-user.sh) | Criação de usuário Linux com shell e comandos restritos |
| [create-restricted-user.md](create-restricted-user.md) | Documentação, autoria, uso e limitações da rotina de usuário restrito |
| [another_docker_installer.sh](another_docker_installer.sh) | Instalação do Docker e Docker Compose |
| [howto-install-docker-ubuntu-2404.md](howto-install-docker-ubuntu-2404.md) | Guia de instalação do Docker no Ubuntu 24.04 |
| [renova_certificado.sh](renova_certificado.sh) | Rotina de renovação de certificado |
| [setup-router-only-for-lab.sh](setup-router-only-for-lab.sh) | Configuração de roteamento destinada a laboratório |

### Backups e equipamentos de rede

| Arquivo | Finalidade |
| --- | --- |
| [backup_dir_mysql.sh](backup_dir_mysql.sh) | Backup de diretórios e MySQL, com notificação de status |
| [bkp_arquivos.sh](bkp_arquivos.sh) | Backup de arquivos com criptografia |
| [bkp_servidores.sh](bkp_servidores.sh) | Rotinas de backup, sincronização e relatórios de servidores |
| [bkp_pfsense.sh](bkp_pfsense.sh) | Backup de configuração do pfSense |
| [bkp_pfsense_2.sh](bkp_pfsense_2.sh) | Variante para múltiplos hosts e notificações |
| [bkp_rtr_3com.sh](bkp_rtr_3com.sh) | Backup de roteadores 3COM |
| [bkp_sw_3com.sh](bkp_sw_3com.sh) | Backup de switches 3COM |
| [bkp_sw_dell.sh](bkp_sw_dell.sh) | Backup de switches DELL |
| [mk-bkp.sh](mk-bkp.sh) | Backup de equipamentos MikroTik |
| [mk_chaves.sh](mk_chaves.sh) | Configuração ou cópia de chaves SSH para acesso aos equipamentos |

### Zimbra, LDAP e serviços

| Arquivo | Finalidade |
| --- | --- |
| [add_mod_usuarios_zimbra.sh](add_mod_usuarios_zimbra.sh) | Criação e alteração de usuários no Zimbra |
| [get_usuario_email_ldap.pl](get_usuario_email_ldap.pl) | Consulta de usuários de e-mail em LDAP |
| [ldap2csv.pl](ldap2csv.pl) | Conversão de LDIF para CSV; crédito original em [CONTRIBUTIONS.md](CONTRIBUTIONS.md) |
| [zimbra_cota_user.sh](zimbra_cota_user.sh) | Relatório de contas, cotas e uso no Zimbra |
| [zimbra_cota_user_v2.sh](zimbra_cota_user_v2.sh) | Variante de relatório de cotas com alertas |
| [zimbra_cota_dominio.sh](zimbra_cota_dominio.sh) | Informações de utilização por domínio |
| [zimbra_dataExpiraSenha.sh](zimbra_dataExpiraSenha.sh) | Relatório de expiração de senhas |
| [zimbra_limpa_dom_invalidos.sh](zimbra_limpa_dom_invalidos.sh) | Limpeza de mensagens da fila para domínios definidos na rotina |
| [zimbra_sync_emails.sh](zimbra_sync_emails.sh) | Sincronização de contas de e-mail por IMAP |
| [zimbra_backup_agenda_tasks_contato.sh](zimbra_backup_agenda_tasks_contato.sh) | Backup de agendas, tarefas e contatos |
| [zimbra_restore_agenda_tasks_contato.sh](zimbra_restore_agenda_tasks_contato.sh) | Restauração dos dados exportados pela rotina correspondente |
| [c_t_mysql.py](c_t_mysql.py) | Teste de conexão com MySQL |

### Monitoramento, logs e cloud

| Material | Finalidade |
| --- | --- |
| [mt_inst_pf.sh](mt_inst_pf.sh) | Instalação inicial do sistema de monitoramento MTMON |
| [zbx_mtmon.sh](zbx_mtmon.sh) | Integração entre Zabbix e MTMON |
| [ConverteLogsFortigateSquidIP.pl](ConverteLogsFortigateSquidIP.pl) | Conversão de logs Fortigate para formato compatível com Squid/SARG |
| [aws/](aws/README.md) | Catálogo de automações AWS, incluindo operações de consulta, alteração e remoção |

## Padrão de documentação

Ao adicionar ou atualizar um material, descreva:

- Problema resolvido e resultado esperado.
- Plataformas, versões e dependências.
- Parâmetros e exemplo com valores fictícios.
- Recursos consultados ou alterados e arquivos gerados.
- Limitações conhecidas e como verificar o resultado.
- Autor, colaboradores e referência original quando aplicável.

Confira [Origem e contribuições](CONTRIBUTIONS.md) para a atribuição dos materiais desta coleção.
