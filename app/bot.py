def gerar_resposta(mensagem: str) -> str:
    texto = mensagem.lower().strip()

    if texto in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "menu"]:
        return (
            "Olá! Eu sou o assistente virtual da SoftBot Pro.\n\n"
            "Digite uma das opções abaixo:\n"
            "1 - Conhecer nossos serviços\n"
            "2 - Solicitar orçamento\n"
            "3 - Falar sobre suporte técnico\n"
            "4 - Ver horário de atendimento\n"
            "5 - Falar com um atendente"
        )

    if texto == "1" or "serviço" in texto or "servicos" in texto or "serviços" in texto:
        return (
            "A SoftBot Pro oferece desenvolvimento de sites, sistemas web, "
            "automações, APIs, dashboards e soluções personalizadas para empresas."
        )

    if texto == "2" or "orçamento" in texto or "orcamento" in texto:
        return (
            "Para solicitar um orçamento, informe:\n\n"
            "1. Nome da empresa\n"
            "2. Tipo de sistema desejado\n"
            "3. Principais funcionalidades\n"
            "4. Prazo desejado\n\n"
            "Nossa equipe analisará sua solicitação."
        )

    if texto == "3" or "suporte" in texto:
        return (
            "Para suporte técnico, descreva o problema encontrado e informe "
            "o nome do sistema ou serviço contratado."
        )

    if texto == "4" or "horário" in texto or "horario" in texto:
        return "Nosso atendimento funciona de segunda a sexta, das 8h às 18h."

    if texto == "5" or "atendente" in texto or "humano" in texto:
        return (
            "Certo! Sua solicitação foi encaminhada para um atendente humano. "
            "Aguarde o retorno da nossa equipe."
        )

    return (
        "Não encontrei uma resposta automática para sua dúvida.\n\n"
        "Sua mensagem foi registrada para análise da nossa equipe."
    )


def gerar_resposta_com_faq(mensagem: str, faqs: list) -> tuple[str, str]:
    texto = mensagem.lower().strip()

    if texto in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "menu"]:
        resposta = (
            "Olá! Eu sou o assistente virtual da SoftBot Pro.\n\n"
            "Digite uma das opções abaixo:\n"
            "1 - Conhecer nossos serviços\n"
            "2 - Solicitar orçamento\n"
            "3 - Falar sobre suporte técnico\n"
            "4 - Ver horário de atendimento\n"
            "5 - Falar com um atendente"
        )
        return resposta, "respondido"

    for faq in faqs:
        palavra = faq.palavra_chave.lower().strip()

        if palavra in texto:
            return faq.resposta, "respondido"

    resposta = gerar_resposta(mensagem)

    if "Não encontrei uma resposta automática" in resposta:
        return resposta, "pendente"

    if "atendente humano" in resposta:
        return resposta, "encaminhado"

    return resposta, "respondido"