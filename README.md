# Escalate - Telegram Prediction Market Bot

A production-grade Telegram bot for decentralized prediction markets on Monad testnet.

Escalate turns group chat debates into on-chain markets.

Instead of arguing:

“MON will hit $1 before March.”

You create a market.
Liquidity forms.
Positions are visible.
Outcome settles on-chain.

The blockchain is the source of truth.
Telegram is the interface.

## 🎯 Features

- **Polymarket-style UX** - Clean market listings with visible pools and liquidity
- **Fully On-Chain** - No database, all state pulled from blockchain
- **Group Chat Ready** - Works seamlessly in Telegram groups
- **Async Architecture** - Built with aiogram v3 and async web3.py
- **Production Ready** - Modular structure with proper error handling

## 📁 Project Structure

```
escale_bot/
│
├── main.py                 # Bot entry point
├── config.py               # Configuration and env validation
├── requirements.txt        # Python dependencies
│
├── bot/
│   ├── states.py          # FSM state definitions
│   ├── keyboards.py       # Inline keyboard layouts
│   ├── handlers/
│   │   ├── start.py       # Start command and navigation
│   │   ├── markets.py     # Market viewing
│   │   ├── create.py      # Market creation flow
│   │   ├── bet.py         # Betting flow
│   │   ├── resolve.py     # Market resolution (resolver only)
│
├── services/
│   ├── blockchain.py      # Web3 service layer
│
├── contracts/
│   ├── escalate_abi.json  # Escalate contract ABI
│   ├── erc20_abi.json     # USDC token ABI
```

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with your configuration:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
MONAD_RPC_URL=https://testnet-rpc.monad.xyz
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=0x...
USDC_ADDRESS=0x...
RESOLVER_ADDRESS=0x...
```

### 3. Run the Bot

```bash
python main.py
```

## 💡 Usage

### Commands

- `/start` - Show main menu
- `/resolve` - Resolve a market (resolver only)

### Flows

#### 📊 View Markets
1. Click "View Markets"
2. See all active markets with:
   - YES/NO pools
   - Total liquidity
   - Time remaining
3. Click "Bet YES" or "Bet NO" to place a bet

#### ➕ Create Market
1. Click "Create Market"
2. Enter market question
3. Enter expiry date (YYYY-MM-DD HH:MM UTC)
4. Confirm creation
5. Transaction submitted to blockchain

#### 💰 Place Bet
1. Click "Place Bet" or select from market list
2. Choose YES or NO
3. Enter amount in USDC
4. Confirm bet
5. Bot approves USDC and places bet
6. See updated pools

#### 🏁 Resolve Market (Resolver Only)
1. Type `/resolve`
2. Enter market ID
3. Select outcome (YES/NO)
4. Confirm resolution
5. Market resolved on-chain

## 🔧 Technical Details

### Blockchain Service

The `BlockchainService` class handles all Web3 interactions:

- **Async operations** - All blockchain calls are async
- **Transaction management** - Automatic gas estimation and nonce handling
- **Error handling** - Graceful handling of RPC and contract errors
- **USDC integration** - Automatic approval flow for betting

### State Management

Uses aiogram's FSM (Finite State Machine) for conversation flows:

- `CreateMarketStates` - Market creation flow
- `PlaceBetStates` - Betting flow
- `ResolveMarketStates` - Resolution flow

### No Database

All market data is fetched live from the blockchain:

- Market count via `marketCount()`
- Market details via `markets(id)`
- No caching or persistence layer

## 🎨 Polymarket-Style UX

Markets are displayed with:

- **Clear question** - What users are betting on
- **Pool sizes** - YES pool and NO pool in USDC
- **Implied probability** - Calculated from pool ratios
- **Total liquidity** - Sum of both pools
- **Time remaining** - Human-readable countdown
- **Status** - Active, expired, or resolved

## ⚠️ Error Handling

The bot handles:

- Invalid market IDs
- Expired markets
- Insufficient USDC balance
- RPC connection failures
- Contract errors
- Invalid user input

All errors return user-friendly messages.

## 🔐 Security

- Private keys loaded from `.env`
- Resolver-only access control for resolution
- Transaction confirmation before execution
- Input validation on all user data

## 📝 License

MIT

## 🤝 Contributing

This is a production-grade template. Feel free to extend with:

- Claim winnings flow
- Market analytics
- User portfolio tracking
- Price charts
- Notification system

---

Built with ❤️ for decentralized prediction markets on Monad
