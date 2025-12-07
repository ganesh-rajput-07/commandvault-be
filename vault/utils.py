KEYWORD_TAG_MAP = {
    'logo': 'logo', 'design': 'design', 'brand': 'branding',
    'sql': 'sql', 'query': 'sql', 'database': 'database',
    'react': 'react', 'component': 'react',
    'email': 'email', 'marketing': 'marketing',
}

USE_CASE_MAP = {
    'logo': 'Design', 'design': 'Design', 'sql': 'Database', 'react': 'Code', 'email': 'Marketing'
}


def auto_tag_and_use_case(text):
    text_low = text.lower()
    tags = set()
    use_case = None
    for kw, tag in KEYWORD_TAG_MAP.items():
        if kw in text_low:
            tags.add(tag)
            if not use_case and kw in USE_CASE_MAP:
                use_case = USE_CASE_MAP[kw]
    return list(tags), use_case
