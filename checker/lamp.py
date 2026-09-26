#!/usr/bin/env python3

from ctf_gameserver import checkerlib

import utils
import random
import secrets
import requests
import logging
import re

import user_agents

class LampChecker(checkerlib.BaseChecker):

    def base(self):
        return f"http://[{self.ip}]:1337/"

    def register(self, S, username, password, shipname):
        logging.info(f"Register {shipname} as {username}:{password}")
        req = S.post(f"{self.base()}/register", data={"username": username, "password": password, "shipname": shipname})
        logging.info(req.content)
        return b"Successfully registered account" in req.content

    def login(self, S, username, password):
        logging.info(f"Login {username}:{password}")
        req = S.post(f"{self.base()}/login", data={"username": username, "password": password})
        logging.info(req.content)
        return b"Successfully logged in" in req.content

    def add_component(self, S, t, x, y):
        logging.info(f"Add {t} ({x}/{y})")
        resp = S.post(f"{self.base()}/", data={"action": "add", "x": x, "y": y, "typ": t})

        try:
            response_text = resp.text
        except UnicodeDecodeError:
            return -1

        # formatting differs for python and the service
        # python formats floats with .0 suffix, so cast to int beforehand
        if float(x).is_integer():
            x = int(float(x))
        if float(y).is_integer():
            y = int(float(y))

        components = re.findall(f"<span class=\"component-wrap\" data-id=\"([0-9]+)\" style=\"position: absolute; left: {x}px; top: {y}px;\"><input class=\"component {t}", response_text)
        if len(components) != 1:
            logging.info(f"Found {len(components)} components in response, should be exactly one: {components} / {response_text}")
            return -1

        logging.info(f"Id: {components[0]}")
        return components[0]

    def connect(self, S, a, b):
        logging.info(f"Connect {a} -> {b}")
        resp = S.post(f"{self.base()}/", data={"action": "connect", "left": a, "right": b})

        try:
            response_text = resp.text
        except UnicodeDecodeError:
            return -1

        leftpos = re.findall(f"<span class=\"component-wrap\" data-id=\"{a}\" style=\"position: absolute; left: ([^p]*)px; top: ([^p]*)px;\">", response_text)
        if len(leftpos) != 1:
            logging.info(f"Failed to find left part of connection: {leftpos} / {response_text}")
            return False
        rightpos = re.findall(f"<span class=\"component-wrap\" data-id=\"{b}\" style=\"position: absolute; left: ([^p]*)px; top: ([^p]*)px;\">", response_text)
        if len(rightpos) != 1:
            logging.info(f"Failed to find right part of connection: {rightpos} / {response_text}")
            return False

        success = re.search(f"<div class=\"line (off|on)\" data-x1=\"{leftpos[0][0]}\" data-y1=\"{leftpos[0][1]}\" data-x2=\"{rightpos[0][0]}\" data-y2=\"{rightpos[0][1]}\">", response_text) is not None
        if not success:
            logging.info(f"Connection should run from {leftpos[0]} -> {rightpos[0]}, but not found")
            logging.info(response_text)

        return success

    def place_flag(self, tick):
        try:
            S = requests.Session()
            S.headers.update({"User-Agent": user_agents.rand()})

            username = secrets.token_hex(8)
            password = secrets.token_hex(8)
            flag = checkerlib.get_flag(tick)
            checkerlib.store_state(f"data_{tick}", {"username": username, "password": password})

            if not self.register(S, username, password, flag):
                return checkerlib.CheckResult.FAULTY

            return checkerlib.CheckResult.OK
        except requests.exceptions.ChunkedEncodingError:
            return checkerlib.CheckResult.FAULTY

    def check_service_component_creation(self, S):
        logging.info("Running check_service_component_creation")
        numcomp = random.randint(3, 10)
        TYPES = ['light', 'button', 'source']
        component_ids = [
            self.add_component(S,
                               random.choice(TYPES),
                               str(random.randint(-10000, 10000) / 100),
                               str(random.randint(-10000, 10000) / 100))
            for i in range(0, numcomp)
        ]

        if -1 in component_ids:
            return False

        numconn = random.randint(0, min(numcomp * numcomp, 20))
        for i in range(0, numconn):
            a = random.choice(component_ids)
            b = random.choice(component_ids)
            if a != b and not self.connect(S, a, b):
                return False

        return True

    def check_service_update_logic(self, S):
        logging.info("Running check_service_update_logic")
        patterns = [
            {
                "components": ['source', 'button', 'light'],
                "conns": [(0, 1), (1, 2)],
                "actions": [
                    {"type": "refresh", "state": [True, False, False]},
                    {"type": "toggle", "target": 1},
                    {"type": "refresh", "state": [True, True, True]},
                ]
            },
            {
                "components": ['source', 'light'],
                "conns": [(0, 1)],
                "actions": [
                    {"type": "refresh", "state": [True, True]}
                ]
            },
            {
                "components": ['source', 'button', 'button', 'light'],
                "conns": [(0, 1), (0, 2), (1, 3), (2, 3)],
                "actions": [
                    {"type": "refresh", "state": [True, False, False, False]},
                    {"type": "toggle", "target": 1},
                    {"type": "refresh", "state": [True, True, False, True]},
                    {"type": "toggle", "target": 2},
                    {"type": "refresh", "state": [True, True, True, True]},
                    {"type": "toggle", "target": 1},
                    {"type": "refresh", "state": [True, False, True, True]},
                    {"type": "toggle", "target": 2},
                    {"type": "refresh", "state": [True, False, False, False]},
                ]
            },
        ]

        selected = random.choice(patterns)

        permutation = [i for i in range(len(selected["components"]))]
        random.shuffle(permutation)
        rev = [-1 for i in range(len(permutation))]
        for i, idx in enumerate(permutation):
            rev[idx] = i

        component_ids = [
            self.add_component(S,
                               selected["components"][i],
                               str(random.randint(-10000, 10000) / 100),
                               str(random.randint(-10000, 10000) / 100))
            for i in permutation
        ]

        if -1 in component_ids:
            return False

        conns = list(selected["conns"])
        random.shuffle(conns)
        for (a, b) in conns:
            if not self.connect(S, component_ids[rev[a]], component_ids[rev[b]]):
                return False

        for entry in selected["actions"]:
            match entry["type"]:
                case "toggle":
                    logging.info(f"Toggle {component_ids[rev[entry['target']]]}")
                    S.post(f"{self.base()}/", data={"action": "toggle", "id": component_ids[rev[entry["target"]]]})
                case "refresh":
                    logging.info(f"Refreshing, expected {[(component_ids[rev[i]], 'on' if x else 'off') for (i, x) in enumerate(entry['state'])]}")
                    resp = S.post(f"{self.base()}/", data={"action": "tick"})

                    try:
                        response_text = resp.text
                    except UnicodeDecodeError:
                        return False

                    for id in range(len(selected["components"])):
                        data = re.findall(f"<span class=\"component-wrap\" data-id=\"{component_ids[rev[id]]}\" style=\"position: absolute; left: -?[0-9]+(\\.[0-9]+)?px; top: -?[0-9]+(\\.[0-9]+)?px;\"><input class=\"component {selected['components'][id]} (off|on)", response_text)
                        if len(data) != 1:
                            logging.info(f"Found {len(data)} after tick for ({component_ids[rev[id]]}), should be exactly one: {data} / {response_text}")
                            return False

                        expected = "on" if entry['state'][id] else "off"

                        if expected != data[0][-1]:
                            logging.info(f"State of component {component_ids[rev[id]]} does not match, should be {expected} but is {data[0][-1]}")
                            return False
                case _:
                    assert False

        return True

    def check_service(self):
        try:
            checks = [self.check_service_component_creation, self.check_service_update_logic]
            check = random.choice(checks)

            S = requests.Session()
            S.headers.update({"User-Agent": user_agents.rand()})

            username = secrets.token_hex(8)
            password = secrets.token_hex(8)

            if not self.register(S, username, password, utils.generate_message()):
                logging.error("Failed to register for check_service");
                return checkerlib.CheckResult.FAULTY

            if not check(S):
                return checkerlib.CheckResult.FAULTY

            return checkerlib.CheckResult.OK
        except requests.exceptions.ChunkedEncodingError:
            return checkerlib.CheckResult.FAULTY

    def check_flag(self, tick):
        try:
            state = checkerlib.load_state(f"data_{tick}")
            if not state:
                return checkerlib.CheckResult.FLAG_NOT_FOUND

            S = requests.Session()
            S.headers.update({"User-Agent": user_agents.rand()})
            if not self.login(S, state["username"], state["password"]):
                return checkerlib.CheckResult.FLAG_NOT_FOUND

            flag = checkerlib.get_flag(tick)
            req = S.get(f"{self.base()}/")
            logging.info(flag)
            logging.info(req.content)

            if flag.encode() not in req.content:
                return checkerlib.CheckResult.FLAG_NOT_FOUND

            return checkerlib.CheckResult.OK
        except requests.exceptions.ChunkedEncodingError:
            return checkerlib.CheckResult.FAULTY

if __name__ == '__main__':

    checkerlib.run_check(LampChecker)
