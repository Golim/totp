# TOTP

This program allows you to generate TOTP codes from the command line.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

```bash
sudo cp ./totp.py /usr/local/bin/totp
sudo chmod +x /usr/local/bin/totp
```

## Usage

### Add a new service

Providing the secret as an argument:

```bash
totp add -s <service> --secret <secret>
```

Providing the URL as an argument:

```bash
totp add -s <service> --url <url>
```

If you don't know what these are, you should be able to find them by reading the QR code provided by the service.

You can **update** a service by replacing the `add` command with `update`.

### Generate a code

```bash
totp -s <service>
```

To automatically copy the code to the clipboard, add the `-c` flag.

## Notice

Is this program secure? I guess so: it stores the secrets using the [`keyring`](https://pypi.org/project/keyring/) module, which uses the system's keyring and uses [`oathtool`](https://www.nongnu.org/oath-toolkit/) to generate the codes.

Anyway, use it at your own risk.
