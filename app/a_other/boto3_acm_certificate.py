import boto3


acm_client = boto3.client('acm')


certificates_response = acm_client.list_certificates(CertificateStatuses=['ISSUED'])

certificates_list = certificates_response['CertificateSummaryList']

certificate_arn = next(iter(certificates_list))['CertificateArn']


# certificate_response = acm_client.export_certificate(CertificateArn=certificate_arn,
#     Passphrase=b'11111111'
# )

certificate_response = acm_client.get_certificate(CertificateArn=certificate_arn)

app.logger.info(f'BOT certificates_response {certificates_response}')
app.logger.info(f'BOT certificate_arn {certificate_arn}')
app.logger.info(f'BOT certificate_response {certificate_response}')