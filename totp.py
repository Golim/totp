#!/usr/bin/env python3

__author__ = "Matteo Golinelli"
__copyright__ = "Copyright (C) 2024 Matteo Golinelli"
__license__ = "MIT"

import subprocess
import argparse
import logging
import keyring
import getpass
import json
import os

try:
    import pyclip
except ImportError:
    pass


class KeyManager:
    '''
    Manages the keys using the system keyring.
    '''
    def __init__(self, service):
        self.service = service

    def get_key(self):
        '''
        Retrieves the key from the system keyring.
        '''
        return keyring.get_password(self.service, self.service)

    def set_key(self, key):
        '''
        Sets the key in the system keyring.
        '''
        keyring.set_password(self.service, self.service, key)


class TOTPGenerator:
    '''
    Generates TOTP codes using oath.
    '''
    def __init__(self, key):
        self.key = key

    def generate(self):
        '''
        Generates a TOTP code.
        '''
        cmd = ['oathtool', '--totp', '--base32', self.key]
        return subprocess.check_output(cmd).decode('utf-8').strip()


class Services:
    '''
    Manages the services and persists
    them in a file in the
    ~/.local/share/totp directory
    in a JSON format.
    '''
    def __init__(self):
        self.directory = os.path.expanduser('~/.local/share/totp')
        self.services = []
        if os.path.exists(self.directory + '/services'):
            with open(self.directory + '/services', 'r') as f:
                self.services = json.load(f)

    def get_services(self):
        '''
        Retrieves the services.
        '''
        return self.services

    def add_service(self, service):
        '''
        Adds a service.
        '''
        self.services.append(service)
        self.save()

    def remove_service(self, service):
        '''
        Removes a service.
        '''
        self.services.remove(service)
        self.save()

    def save(self):
        '''
        Saves the services to a file.
        '''
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(self.directory + '/services', 'w') as f:
            json.dump(self.services, f)


def main():
    parser = argparse.ArgumentParser(description='TOTP code generator for the Linux CLI.')

    parser.add_argument("action", choices=["generate", "add", "update", "remove", "list"], help="Action to perform", default="generate", nargs="?", const="generate")
    parser.add_argument("-s", "--service", help="Service name")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy the code to the clipboard")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger('totp')
    
    if args.debug:
        logger.setLevel(logging.DEBUG)

    services = Services()

    if args.action == "list":
        logger.info(f"Services: {', '.join(services.get_services())}")
        exit(0)

    if args.service is None:
        logger.error("Service name is required")
        exit(1)

    key_manager = KeyManager(args.service)

    if args.action == "generate":
        key = key_manager.get_key()

        if key is None:
            print("Key not found")
            exit(1)
        totp_generator = TOTPGenerator(key)

        totp = totp_generator.generate()

        logger.info(f"TOTP code for {args.service}: {totp}")

        if "pyclip" in globals() and args.copy:
            if args.copy:
                pyclip.copy(totp)
                logger.info("Code copied to clipboard")

    elif args.action == "add":
        secret = getpass.getpass("Enter the secret or URL: ")
        if secret == "":
            logger.error("Secret or URL is required")
            exit(1)
        elif secret.startswith("otpauth://"):
            secret = secret.split("secret=")[1].split("&")[0]

        # Check if key already exists
        key = key_manager.get_key()
        if key:
            logger.error("Service already exists, use update instead")
            exit(1)

        key_manager.set_key(secret)
        if args.service not in services.get_services():
            services.add_service(args.service)

        logger.info(f"Key added for service {args.service}")

    elif args.action == "update":
        secret = getpass.getpass("Enter the secret or URL: ")

        if secret == "":
            logger.error("Secret or URL is required")
            exit(1)
        elif secret.startswith("otpauth://"):
            secret = secret.split("secret=")[1].split("&")[0]

        # Check if key already exists
        key = key_manager.get_key()
        if key is None:
            logger.error("Service not found")
            exit(1)

        key_manager.set_key(secret)
        if args.service not in services.get_services():
            services.add_service(args.service)

        logger.info(f"Key updated for service {args.service}")

    elif args.action == "remove":
        key = key_manager.get_key()
        if key is None:
            logger.error("Service not found")
            exit(1)

        key_manager.set_key("")
        if args.service in services.get_services():
            services.remove_service(args.service)

        logger.info(f"Key removed for service {args.service}")

if __name__ == '__main__':
    main()
