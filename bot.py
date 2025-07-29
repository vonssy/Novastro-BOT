from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_utils import to_hex
from eth_account import Account
from eth_account.messages import encode_defunct
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, FormData, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, string, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Novastro:
    def __init__(self) -> None:
        self.BASE_API = "https://api.deperp.xyz/api/v1"
        self.RPC_URL = "https://sepolia.drpc.org/"
        self.USDC_CONTRACT_ADDRESS = "0xba1FCc7a596140e5feC52B3aB80a8F000C9Af104"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]}
        ]''')
        self.USER_AGENT = {}
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.used_nonce = {}
        self.auto_kyc = False
        self.purchase_count = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Novastro Ignition{Fore.BLUE + Style.BRIGHT} Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/http.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_login_payload(self, account: str, address: str, message: str):
        try:
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "walletAddress": address,
                "signature": signature,
                "message": message
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def random_name(self, jurisdiction: str):
        if jurisdiction == "United States":
            first_names = [
                "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
                "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
                "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Edward"
            ]
            last_names = [
                "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia",
                "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez",
                "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez", "Lee", "Gonzalez"
            ]
        elif jurisdiction == "Dubai":
            first_names = [
                "Mohammed", "Ahmed", "Ali", "Hassan", "Omar", "Abdullah", "Khalid", "Yousef",
                "Saif", "Faisal", "Majid", "Rashid", "Nasser", "Saeed", "Ibrahim", "Salem",
                "Jassim", "Tariq", "Zayed", "Hamdan", "Sultan", "Ziyad", "Kareem"
            ]
            last_names = [
                "Al-Maktoum", "Al-Falasi", "Al-Nahyan", "Al-Qasimi", "Al-Mansoori", "Al-Zarooni",
                "Al-Mazrouei", "Al-Suwaidi", "Al-Shamsi", "Al-Dhaheri", "Al-Mutairi", "Al-Rashid",
                "Al-Habtoor", "Al-Nuaimi", "Al-Kuwaiti", "Al-Ketbi", "Al-Ahmadi", "Al-Otaiba"
            ]
        else:
            return "Invalid jurisdiction"

        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def random_email(self, full_name: str):
        name = ''.join(full_name.lower().split())
        number = ''.join(random.choices(string.digits, k=3))
        return f"{name}{number}@gmail.com"
        
    def generate_kyc_payload(self, url_docs: str):
        try:
            jurisdiction = random.choice(["United States", "Dubai"])
            full_name = self.random_name(jurisdiction)
            email = self.random_email(full_name)

            payload = {
                "fullName": full_name,
                "email": email,
                "jurisdiction": jurisdiction,
                "documents": [
                    { "type": "other", "url": url_docs }
                ]
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Send TX Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
    
    async def get_token_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.USDC_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)
            balance = token_contract.functions.balanceOf(address).call()
            decimals = token_contract.functions.decimals().call()

            token_balance = balance / (10 ** decimals)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_transactions(self, account: str, address: str, to_address: str, calldata: str, amount: str, gas_limit: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            max_priority_fee = web3.to_wei(1.5, "gwei")
            max_fee = max_priority_fee

            tx = {
                "from": web3.to_checksum_address(address),
                "to": web3.to_checksum_address(to_address) if to_address else None,
                "data": calldata,
                "value": int(amount),
                "gas": int(gas_limit),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            }

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)

            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None

    def print_question(self):
        while True:
            try:
                auto_kyc = input(f"{Fore.YELLOW + Style.BRIGHT}Auto Submit KYC Verification? [y/n] -> {Style.RESET_ALL}").strip().lower()
                if auto_kyc in ["y", "n"]:
                    self.auto_kyc = auto_kyc == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 'y' or 'n'.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")
        
        while True:
            try:
                purchase_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Property Purchase Count For Each Wallets -> {Style.RESET_ALL}").strip())
                if purchase_count > 0:
                    self.purchase_count = purchase_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def auth_nonce(self, address: str, use_proxy: bool, retries=5):
        url = f"{self.BASE_API}/auth/nonce/{address}"
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=self.HEADERS[address], proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Nonce Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def auth_login(self, account: str, address: str, message: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/auth/login"
        data = json.dumps(self.generate_login_payload(account, address, message))
        headers = {
            **self.HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def user_profile(self, address: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/users/profile"
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch KYC Status Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def download_image(self, address: str, use_proxy: bool, retries=3):
        url = "https://thispersondoesnotexist.com"
        headers = {
            "User-Agent": self.USER_AGENT[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        with open("images/kyc_image.png", "wb") as f:
                            f.write(await response.read())
                        return True
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Download KYC Images Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def upload_kyc(self, address: str, use_proxy: bool, retries=3):
        url = "https://testnet.novastro.xyz/api/fileUpload"
        data = FormData()
        data.add_field(
            name="file",
            value=open("images/kyc_image.png", "rb"),
            filename="kyc_image.png",
            content_type="image/png"
        )
        headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.novastro.xyz",
            "Referer": "https://testnet.novastro.xyz/profile",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.USER_AGENT[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, data=data, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Upload KYC Images Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def submit_kyc(self, address: str, url_docs: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/users/kyc/submit"
        data = json.dumps(self.generate_kyc_payload(url_docs))
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} KYC Submission Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def create_identity(self, address: str, tx_hash: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/users/create-identity"
        data = json.dumps({"transactionHash":tx_hash})
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Identity Contract Not Created {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def process_kyc(self, address: str, tx_hash: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/users/kyc/process-payload"
        data = json.dumps({"transactionHash":tx_hash})
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} KYC Verification Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def faucet_status(self, address: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/faucet/profile"
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Claimable Status Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def prepare_claim_faucet(self, address: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/faucet/claim/prepare"
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": "0"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Prepare Claim Faucet Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def submit_claim_faucet(self, address: str, event_id: str, tx_hash: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/faucet/claim/submit"
        data = json.dumps({"transactionEventId":event_id, "transactionHash":tx_hash})
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Submit Tx Hash Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def list_properties(self, address: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/properties"
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Avaialble Tokenized Properties Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def detail_properties(self, address: str, property_id: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/properties/{property_id}"
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Detailed Properties Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def prepare_purchase_property(self, address: str, property_id: str, invest_amount: int, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/properties/{property_id}/purchase/prepare"
        data = json.dumps({"purchaseAmount":str(invest_amount)})
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Prepare Purchaing Properties Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
            
    async def submit_purchase_property(self, address: str, property_id: str, event_id: str, tx_hash: str, use_proxy: bool, retries=3):
        url = f"{self.BASE_API}/properties/{property_id}/purchase/submit"
        data = json.dumps({"transactionEventId":event_id, "transactionHash":tx_hash})
        headers = {
            **self.HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Submit Tx Hash Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
        
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    continue

                return False
            
            return True
        
    async def process_auth_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
       is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
       if is_valid:
            
            nonce = await self.auth_nonce(address, use_proxy)
            if not nonce: return False

            message = nonce["data"]["message"]

            login = await self.auth_login(account, address, message, use_proxy)
            if not login: return False

            self.access_tokens[address] = login["data"]["accessToken"]

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
            )
            return True
       
    async def process_perform_transactions(self, account: str, address: str, to_address: str, calldata: str, amount: str, gas_limit: str, tx_type: str, use_proxy: bool):    
        tx_hash, block_number = await self.perform_transactions(account, address, to_address, calldata, amount, gas_limit, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://sepolia.etherscan.io/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {tx_type} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
            return tx_hash
        
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )
        return None
    
    async def process_kyc_verification(self, account: str, address: str, use_proxy: bool): 
        profile = await self.user_profile(address, use_proxy)
        if not profile: return False

        kyc_status = profile["data"]["kycStatus"]
        if kyc_status == "approved": 
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Already Approved {Style.RESET_ALL}"
            )
            return True
        
        if not self.auto_kyc: 
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Pending, Skipping This Accounts {Style.RESET_ALL}"
            )
            return False
        
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
            f"{Fore.YELLOW+Style.BRIGHT} Pending, Starting KYC... {Style.RESET_ALL}"
        )

        images = await self.download_image(address, use_proxy)
        if not images: return False

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Images  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Downloaded {Style.RESET_ALL}"
        )

        upload = await self.upload_kyc(address, use_proxy)
        if not upload: return False

        url_docs = upload["url"]

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Upload  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   URL Docs:{Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT} {url_docs} {Style.RESET_ALL}"
        )

        submit = await self.submit_kyc(address, url_docs, use_proxy)
        if not submit: return False

        to_address = submit["data"]["payload"]["to"]
        calldata = submit["data"]["payload"]["data"]
        amount = submit["data"]["payload"]["value"]
        gas_limit = submit["data"]["payload"]["gasLimit"]

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Submit  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} KYC Submitted Successfully {Style.RESET_ALL}"
        )

        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.YELLOW+Style.BRIGHT}Sign First Transaction...{Style.RESET_ALL}"
        )

        tx_hash = await self.process_perform_transactions(account, address, to_address, calldata, amount, gas_limit, "Deploy Contract", use_proxy)
        if not tx_hash: return False

        create = await self.create_identity(address, tx_hash, use_proxy)
        if not create: return False

        to_address = create["data"]["managerKeyPayload"]["to"]
        calldata = create["data"]["managerKeyPayload"]["data"]
        amount = create["data"]["managerKeyPayload"]["value"]
        gas_limit = create["data"]["managerKeyPayload"]["gasLimit"]

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Identity:{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Contract Created {Style.RESET_ALL}"
        )

        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.YELLOW+Style.BRIGHT}Sign Second Transaction...{Style.RESET_ALL}"
        )

        tx_hash = await self.process_perform_transactions(account, address, to_address, calldata, amount, gas_limit, "Add Key", use_proxy)
        if not tx_hash: return False

        process = await self.process_kyc(address, tx_hash, use_proxy)
        if not process: return False

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} KYC Verification Completed {Style.RESET_ALL}"
        )

        return True
    
    async def process_claim_faucet(self, account: str, address: str, use_proxy: bool): 
        faucet = await self.faucet_status(address, use_proxy)
        if not faucet: return False

        can_claim = faucet["profile"]["canClaimNow"]
        if not can_claim: 
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
            )
            return False
        
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Can Claim {Style.RESET_ALL}"
        )

        prepare = await self.prepare_claim_faucet(address, use_proxy)
        if not prepare: return False

        event_id = prepare["data"]["transactionEventId"]
        to_address = prepare["data"]["payload"]["to"]
        calldata = prepare["data"]["payload"]["data"]

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Prepare :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
        )

        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.YELLOW+Style.BRIGHT}Sign Mint Transaction...{Style.RESET_ALL}"
        )

        tx_hash = await self.process_perform_transactions(account, address, to_address, calldata, "0", "300000", "Mint", use_proxy)
        if not tx_hash: return False

        submit = await self.submit_claim_faucet(address, event_id, tx_hash, use_proxy)
        if not submit: return False

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Tx Hash Submitted Successfully {Style.RESET_ALL}"
        )
    
    async def process_purchase_property(self, account: str, address: str, use_proxy: bool): 
        property_lists = await self.list_properties(address, use_proxy)
        if not property_lists: return False

        properties = property_lists["data"]["properties"]

        tokenized_properties = [
            p for p in properties
            if p["status"] == "tokenized" and not p.get("restrictedCountries")
        ]

        if not tokenized_properties:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Message :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} No Avaialble Tokenized Properties {Style.RESET_ALL}"
            )
            return False
        
        for i in range(self.purchase_count):
            self.log(
                f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{i+1}{Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT} Of {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.purchase_count}{Style.RESET_ALL}                                   "
            )

            selected_property = random.choice(tokenized_properties)
            
            property_id = selected_property["id"]

            detail = await self.detail_properties(address, property_id, use_proxy)
            if not detail: continue

            property_name = detail["data"]["title"]
            invest_amount = detail["data"]["token"]["minimumInvestment"]

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Name    :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {property_name}  {Style.RESET_ALL}"
            )

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {invest_amount} USDC {Style.RESET_ALL}"
            )

            balance = await self.get_token_balance(address, use_proxy)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} USDC {Style.RESET_ALL}"
            )

            if not balance or balance < invest_amount: 
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient USDC Token Balance {Style.RESET_ALL}"
                )
                break

            prepare = await self.prepare_purchase_property(address, property_id, invest_amount, use_proxy)
            if not prepare: continue

            event_id = prepare["data"]["transactionEventId"]

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Prepare :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
            )

            transactions_success = True

            payloads = prepare["data"]["payload"]
            for payload in payloads:
                type = payload["type"]
                to_address = payload["to"]
                calldata = payload["data"]
                amount = payload["value"]

                if type == "approve":
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Sign Approve Transaction...{Style.RESET_ALL}"
                    )

                    tx_hash = await self.process_perform_transactions(account, address, to_address, calldata, amount, "300000", "Approve", use_proxy)
                    if not tx_hash:
                        transactions_success = False
                        break

                elif type == "distribute":
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Sign Distribute Transaction...{Style.RESET_ALL}"
                    )

                    tx_hash = await self.process_perform_transactions(account, address, to_address, calldata, amount, "300000", "Distribute", use_proxy)
                    if not tx_hash:
                        transactions_success = False
                        break

                await asyncio.sleep(3)

            if not transactions_success: continue

            submit = await self.submit_purchase_property(address, property_id, event_id, tx_hash, use_proxy)
            if not submit: continue

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Tx Hash Submitted Successfully {Style.RESET_ALL}"
            )

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_auth_login(account, address, use_proxy, rotate_proxy)
        if logined:
            web3 = await self.get_web3_with_check(address, use_proxy)
            if not web3:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Web3 Not Connected {Style.RESET_ALL}"
                )
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

            
            self.log(f"{Fore.CYAN+Style.BRIGHT}KYC     :{Style.RESET_ALL}")

            is_verifed = await self.process_kyc_verification(account, address, use_proxy)
            if not is_verifed: return

            self.log(f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}")

            await self.process_claim_faucet(account, address, use_proxy)

            self.log(f"{Fore.CYAN+Style.BRIGHT}Purchase:{Style.RESET_ALL}")

            await self.process_purchase_property(account, address, use_proxy)
            
    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue

                        self.USER_AGENT[address] = FakeUserAgent().random

                        self.HEADERS[address] = {
                            "Accept": "application/json, text/plain, */*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Connection": "keep-alive",
                            "Host": "api.deperp.xyz",
                            "Origin": "https://testnet.novastro.xyz",
                            "Referer": "https://testnet.novastro.xyz/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "cross-site",
                            "User-Agent": self.USER_AGENT[address]
                        }

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Novastro()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Novastro Ignition - BOT{Style.RESET_ALL}                                       "                              
        )