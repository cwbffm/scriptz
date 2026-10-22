# Automações AWS

Rotinas para consulta e administração de recursos AWS. Esta pasta integra o fork de [charles-josiah/scriptz](https://github.com/charles-josiah/scriptz); veja [Origem e contribuições](../CONTRIBUTIONS.md).

## Requisitos e uso

Abra o arquivo escolhido e confira as ferramentas utilizadas, credenciais locais, perfil, região, filtros e recursos selecionados. As rotinas Shell dependem dos comandos chamados no próprio arquivo; a rotina Python depende das bibliotecas que ela importa.

O catálogo abaixo indica o impacto esperado pela finalidade documentada. Ele não é um simulador nem implementa um modo universal de prévia para os scripts. A região e o escopo efetivos são definidos pela implementação e pela configuração de cada rotina.

## Catálogo por impacto

| Arquivo | Finalidade | Impacto a revisar |
| --- | --- | --- |
| [get_rds_tag.sh](get_rds_tag.sh) | Consultar tags de recursos RDS | Consulta |
| [s3_check_logging.sh](s3_check_logging.sh) | Verificar logging de buckets S3 | Consulta |
| [scan-check-certificate-expire.sh](scan-check-certificate-expire.sh) | Verificar endpoints HTTPS e expiração de certificados a partir de registros DNS | Consulta e sondagem de endpoints |
| [add_rds_tag.sh](add_rds_tag.sh) | Aplicar tags em recursos RDS | Alteração de tags |
| [rem_rds_tag.sh](rem_rds_tag.sh) | Remover tags de recursos RDS | Remoção de tags |
| [ec2_ebs_vol_agg_tag.sh](ec2_ebs_vol_agg_tag.sh) | Aplicar tags a volumes EBS, conforme os filtros da rotina | Alteração de tags |
| [ec2_ebs_vol_change_to_gp3.sh](ec2_ebs_vol_change_to_gp3.sh) | Alterar volumes EBS para gp3 | Alteração de armazenamento e possível impacto financeiro |
| [ecr_scan_on_push.sh](ecr_scan_on_push.sh) | Configurar scan on push no ECR | Alteração de configuração |
| [ecr_set_immutable.sh](ecr_set_immutable.sh) | Configurar imutabilidade de tags no ECR | Alteração do comportamento de publicação de imagens |
| [s3_force_ssl.sh](s3_force_ssl.sh) | Verificar ou configurar a exigência de HTTPS em buckets S3 | Alteração de políticas de acesso |
| [Finding_and_Releasing_Unattached_EIP.sh](Finding_and_Releasing_Unattached_EIP.sh) | Identificar e liberar Elastic IPs não associados | Liberação de endereços |
| [delete-default-vpc.py](delete-default-vpc.py) | Excluir VPCs padrão, conforme o escopo da rotina | Exclusão de recursos de rede |

## Resultado e documentação

Consulte a saída de cada rotina e verifique os recursos correspondentes na AWS. Para novos materiais ou revisões, documente os parâmetros, o conjunto de recursos atingido, um exemplo com valores fictícios e a forma de conferir o resultado.

Preserve os créditos e referências presentes nos arquivos. As rotinas desta pasta são materiais de referência e podem exigir adaptações para versões e ambientes atuais.
