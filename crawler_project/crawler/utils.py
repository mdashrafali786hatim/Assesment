def validate_domains(domains):
    valid_domains = []
    for domain in domains:
        if domain.startswith("http://") or domain.startswith("https://"):
            valid_domains.append(domain)
        else:
            print(f"Invalid domain: {domain}")
    return valid_domains
