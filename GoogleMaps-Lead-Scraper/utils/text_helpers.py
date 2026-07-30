import string

def clean_text(text):
    """Hapus karakter aneh & non-printable dari teks."""
    if not text or text == "N/A":
        return text
    cleaned = ''.join(char for char in text if char in string.printable)
    return ' '.join(cleaned.split())

def is_chain(name, chain_keywords):
    """Return True if business name contains known chain keyword."""
    if not name or name == "N/A":
        return False
    name_lower = name.lower()
    return any(keyword.lower() in name_lower for keyword in chain_keywords)

def is_blacklisted_email(email, email_blacklist):
    """Return True if email is blacklisted."""
    if email == "N/A" or not email:
        return True
    email_lower = email.lower()
    return any(pattern.lower() in email_lower for pattern in email_blacklist)

def normalize_country_name(name):
    name = name.strip().lower()
    aliases = {
        "usa": "united states",
        "amerika": "united states",
        "amerika serikat": "united states",
        "inggris": "united kingdom",
        "uk": "united kingdom",
        "jerman": "germany",
        "perancis": "france",
        "prancis": "france",
        "india": "india",
        "brazil": "brazil",
        "brasil": "brazil",
    }
    return aliases.get(name, name)
