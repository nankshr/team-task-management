import secrets
import string

def generate_secret_key(length=64):
    # Use only alphanumeric + a few safe special chars (- and _)
    safe_chars = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(safe_chars) for _ in range(length))

if __name__ == "__main__":
    key = generate_secret_key()
    print(f"SECRET_KEY={key}")
