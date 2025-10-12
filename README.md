# LeagueAccounts

Welcome to **LeagueAccounts**, a tool designed to simplify managing multiple **League of Legends** accounts in one place. With fast account switching, secure password storage using Windows' built-in credential system, and convenient features like automatic credential entry and rank fetching, LeagueAccounts makes handling multiple accounts seamless and efficient.

## Features

- **Quick Account Switching**: Easily switch between multiple League of Legends accounts without the hassle of logging in and out repeatedly.
- **Secure Password Storage**: Safely store your account credentials using Windows' native password storage system.
- **Auto Credential Entry**: Use `CTRL+SHIFT+V` to automatically input your login credentials into the Riot Client.
- **Automatic Rank and Level Fetching**: Retrieve and display your account ranks and levels effortlessly, keeping you updated on your progress.
- **User-Friendly Interface**: Intuitive design for managing accounts with minimal effort.

## Installation

Download the latest release from GitHub:

[Download Latest Release](https://github.com/FlorentTariolle/LeagueAccounts/releases/latest)

## Usage

1. Launch LeagueAccounts.
2. Add your League of Legends accounts to the tool.
3. Use the interface to select an account and switch instantly.
4. Press `CTRL+SHIFT+V` to auto-fill credentials in the Riot Client.
5. View your account ranks automatically fetched by the tool.

## Building from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable and installer
python scripts/build_all.py
```

For detailed build instructions, see [BUILD.md](docs/BUILD.md).

## Contributing

We welcome contributions to make LeagueAccounts even better! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a pull request.

Please ensure your code follows the project's coding standards and includes appropriate documentation.
