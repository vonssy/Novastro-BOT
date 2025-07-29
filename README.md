# Novastro BOT

Automate tasks on the Novastro platform with this advanced Python bot. The bot can generate wallets, perform KYC verification, claim faucets, and purchase properties automatically.


## Features

- 🪪 **Wallet Generation**: Create new Ethereum wallets with mnemonic phrases
- 🔐 **Secure Storage**: Save wallet information to `wallets.json` and private keys to `accounts.txt`
- 📝 **KYC Automation**: Complete KYC verification with AI-generated documents
- 💧 **Faucet Claiming**: Automatically claim faucet rewards
- 🏠 **Property Purchase**: Purchase tokenized properties on the platform
- 🔁 **Proxy Support**: Rotate proxies to avoid rate limiting
- 📊 **Real-time Logging**: Color-coded terminal output with timestamps

## Requirements

- Python 3.8+
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dicoderin/Novastro-BOT.git
cd Novastro-BOT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. **Proxy Setup** (Optional):
   - Create a `proxy.txt` file with your proxies (one per line)
   - Or let the bot fetch free proxies automatically

2. **Image Directory**:
   - The bot will automatically create an `images` directory for KYC documents

## Usage

Run the bot:
```bash
python main.py
```

The bot will guide you through:
1. Wallet generation (if no accounts.txt exists)
2. Proxy configuration options
3. Auto KYC verification setting
4. Property purchase count selection

## Workflow

1. **Wallet Generation**:
   - Creates new Ethereum wallets
   - Saves mnemonic phrases to `wallets.json`
   - Saves private keys to `accounts.txt`

2. **Account Processing**:
   - Logs in to Novastro platform
   - Checks KYC status
   - Automates KYC verification if enabled
   - Claims faucet rewards
   - Purchases tokenized properties

## File Structure

```
Novastro-BOT/
├── main.py              # Main bot script
├── wallets.json         # Generated wallet data (mnemonics, addresses)
├── accounts.txt         # Private keys (one per line)
├── proxy.txt            # Custom proxies (optional)
├── images/              # KYC document storage
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
```

## Contribution

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Disclaimer

This bot is for educational purposes only. Use it at your own risk. The developers are not responsible for any account restrictions or financial losses incurred while using this bot.
