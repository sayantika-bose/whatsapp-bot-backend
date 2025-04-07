from bs4 import BeautifulSoup

def html_to_whatsapp_format(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # Convert <a> to plain text (or text + URL if needed)
    for a in soup.find_all('a'):
        if a.string:
            a.replace_with(f"{a.string}")
        else:
            a.unwrap()

    # Replace <b>, <strong> with *
    for b in soup.find_all(['b', 'strong']):
        b.insert_before('*')
        b.insert_after('*')
        b.unwrap()

    # Replace <i>, <em> with _
    for i in soup.find_all(['i', 'em']):
        i.insert_before('_')
        i.insert_after('_')
        i.unwrap()

    # Replace <code>, <pre> with ```
    for code in soup.find_all(['code', 'pre']):
        code.insert_before('```')
        code.insert_after('```')
        code.unwrap()

    # Replace <del>, <strike> with ~
    for s in soup.find_all(['del', 'strike']):
        s.insert_before('~')
        s.insert_after('~')
        s.unwrap()

    # Handle <br> and <p> with newlines
    for br in soup.find_all('br'):
        br.replace_with('\n')
    for p in soup.find_all('p'):
        p.insert_after('\n')
        p.unwrap()

    # Get plain text
    return soup.get_text(strip=True)
