import os, re, html
from pathlib import Path
import pandas as pd
from email import policy
from email.parser import BytesParser

DATA_DIR = Path("data")
SPAM_DIR = DATA_DIR / "spam"
HAM_DIR = DATA_DIR / "ham"

URL_RE = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+)", flags=re.IGNORECASE)
EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
HTML_TAG_RE = re.compile(r"<(script|style).*?>.*?</\1>", flags=re.IGNORECASE | re.DOTALL)
STRIP_TAGS_RE = re.compile(r"<[^>]+>")

def list_files(folder: Path):
    return [p for p in folder.iterdir() if p.is_file]

def clean_html(html_text: str) -> str:
    #remove scripts/styles
    t = HTML_TAG_RE.sub(" ", html_text)
    
    #strip remaining tags
    t = STRIP_TAGS_RE.sub(" ", t)
    
    #unescape HTML entities
    t = html.unescape(t)
    
    #collapse whitespaces
    t = re.sub(r"\s+", " ", t).strip()
    
    return t


def extract_body_from_msg(msg) -> str:
    #text/plain parts
    if msg.is_multipart():
        parts_text = []
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get_content_disposition() or "").lower()
            if ctype == "text/plain" and disp != "attachment":
                try:
                    text = part.get_content()
                except Exception:
                    try:
                        text = part.get_payload(decode=True).decode(errors="ignore")
                    except Exception:
                        text = ""
                if text:
                    parts_text.append(text)
        if parts_text:
            return "\n\n".join(parts_text).strip()
        
        #fallback to text/html part
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    html_text = part.get_content()
                except Exception:
                    try:
                        html_text = part.get_payload(decode=True).decode(errors="ignore")
                    except Exception:
                        html_text = ""
                if html_text:
                    return clean_html(html_text)
        
        #final fallback: join non-multipart payloads
        try:
            fallback = msg.get_payload(decode=True)
            if isinstance(fallback, (bytes, bytearray)):
                return fallback.decode(errors="ignore").strip()
            return str(fallback).strip()
        except Exception:
            return ""
    
    else:
        #not multipart
        ctype = msg.get_content_type()
        try:
            content = msg.get_content()
        except Exception:
            try:
                content = msg.get_payload(decode=True).decode(errors=True)
            except Exception:
                content = ""
        if ctype == "text/html":
            return clean_html(content)
        return content.strip()
    
def normalize_text(text: str) -> str:
    if not text:
        return ""
    # replace URLs and emails with tokens
    text = URL_RE.sub(" <URL> ", text)
    text = EMAIL_RE.sub(" <EMAIL> ", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_email_file(path: Path):
    try:
        with open(path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)
    except Exception:
        # fallback: read as text if binary parse fails
        try:
            raw = path.read_text(errors="ignore")
            msg = BytesParser(policy=policy.default).parsebytes(raw.encode(errors="ignore"))
        except Exception:
            return None

    subject = (msg.get("Subject") or "").strip()
    from_ = (msg.get("From") or "").strip()
    to = (msg.get("To") or "").strip()
    date = (msg.get("Date") or "").strip()
    body = extract_body_from_msg(msg)
    body = normalize_text(body)
    raw_text = None
    return {
        "path": str(path),
        "subject": normalize_text(subject),
        "from": from_,
        "to": to,
        "date": date,
        "body": body,
    }

def load_folder(folder: Path, label: str):
    rows = []
    files = list_files(folder)
    # iterate
    for p in files:
        parsed = parse_email_file(p)
        if parsed is None:
            # skip unreadable files
            continue
        parsed["label"] = label
        rows.append(parsed)
    return rows

def main():
    rows = []
    if not SPAM_DIR.exists() or not HAM_DIR.exists():
        print("ERROR: data/spam or data/ham folder not found. Make sure you extracted files.")
        return
    print("Loading spam...")
    rows += load_folder(SPAM_DIR, "spam")
    print("Loading ham...")
    rows += load_folder(HAM_DIR, "ham")
    df = pd.DataFrame(rows, columns=["label","subject","from","to","date","body","path"])
    print("Loaded:", df.shape, "rows (spam+ham).")
    # show small sample
    with pd.option_context("display.max_colwidth", 200):
        print(df.sample(min(5, len(df)), random_state=1).to_string(index=False))
    # save a small CSV preview (optional)
    out = DATA_DIR / "emails_preview.csv"
    df.to_csv(out, index=False)
    print("Saved preview CSV to", out)
    # keep DataFrame in memory if you want further steps
    # For now we exit — reply with 'success' or the single error line if any.
    return

if __name__ == "__main__":
    main()