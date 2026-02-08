# Escalate Bot - Setup Guide

## 📋 Prerequisites

- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Monad testnet RPC access
- Wallet with private key
- Deployed Escalate contract address
- USDC token address on Monad testnet

## 🔧 Step-by-Step Setup

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. **Important**: Disable privacy mode for group chat support
   - Send `/setprivacy` to @BotFather
   - Select your bot
   - Choose "Disable"

### 2. Install Python Dependencies

```bash
cd escale
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example env file:

```bash
copy .env.example .env
```

Edit `.env` with your actual values:

```env
# Get from @BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Monad testnet RPC
MONAD_RPC_URL=https://testnet-rpc.monad.xyz

# Your wallet private key (without 0x prefix)
PRIVATE_KEY=your_64_character_private_key_here

# Deployed Escalate contract address
CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890

# USDC token address on Monad testnet
USDC_ADDRESS=0x1234567890123456789012345678901234567890

# Resolver wallet address (can be same as your wallet)
RESOLVER_ADDRESS=0x1234567890123456789012345678901234567890
```

### 4. Verify Configuration

Run a quick config check:

```bash
python -c "from config import Config; Config.validate(); print('✅ Configuration valid')"
```

### 5. Run the Bot

```bash
python main.py
```

You should see:

```
✅ Configuration validated
✅ Connected to blockchain at https://testnet-rpc.monad.xyz
✅ Wallet address: 0x...
✅ All handlers registered
🚀 Starting Escalate bot...
```

## 🧪 Testing

### Test in Private Chat

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. You should see the main menu with buttons

### Test Market Creation

1. Click "Create Market"
2. Enter: `Will it rain tomorrow?`
3. Enter expiry: `2026-12-31 23:59`
4. Confirm creation
5. Wait for blockchain confirmation

### Test Betting

1. Click "View Markets"
2. Click "Bet YES" on a market
3. Enter amount: `10`
4. Confirm bet
5. Bot will approve USDC and place bet

### Test in Group Chat

1. Create a new Telegram group
2. Add your bot to the group
3. Send `/start` in the group
4. Bot should respond with main menu

## 🔍 Troubleshooting

### Bot doesn't respond in group

**Solution**: Disable privacy mode in @BotFather

```
/setprivacy → Select bot → Disable
```

### "Configuration Error: Missing required environment variables"

**Solution**: Check your `.env` file has all required variables

### "Failed to connect to blockchain"

**Solution**: 
- Check `MONAD_RPC_URL` is correct
- Verify internet connection
- Try alternative RPC endpoint

### "Transaction failed: insufficient funds"

**Solution**:
- Ensure wallet has USDC balance
- Ensure wallet has native tokens for gas
- Check USDC approval

### "Only the resolver can resolve markets"

**Solution**: 
- Verify `RESOLVER_ADDRESS` matches your wallet
- Check private key corresponds to resolver address

## 🚀 Production Deployment

### Option 1: VPS (Recommended)

1. Rent a VPS (DigitalOcean, AWS, etc.)
2. Install Python 3.11+
3. Clone your repository
4. Set up `.env` file
5. Run with process manager:

```bash
# Install PM2 or systemd service
pip install pm2
pm2 start main.py --name escalate-bot
pm2 save
pm2 startup
```

### Option 2: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t escalate-bot .
docker run -d --env-file .env --name escalate escalate-bot
```

### Option 3: Heroku

1. Create `Procfile`:
```
worker: python main.py
```

2. Deploy:
```bash
heroku create escalate-bot
heroku config:set TELEGRAM_BOT_TOKEN=...
heroku config:set MONAD_RPC_URL=...
# ... set all env vars
git push heroku main
heroku ps:scale worker=1
```

## 📊 Monitoring

### View Logs

```bash
# If using PM2
pm2 logs escalate-bot

# If using Docker
docker logs -f escalate

# If running directly
python main.py
```

### Health Check

The bot logs connection status on startup. Look for:

```
✅ Connected to blockchain
✅ Wallet address: 0x...
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use environment variables** - Don't hardcode secrets
3. **Secure your VPS** - Use SSH keys, disable password auth
4. **Rotate keys regularly** - Change private keys periodically
5. **Monitor transactions** - Watch for unusual activity
6. **Limit resolver access** - Only trusted address can resolve

## 🎯 Next Steps

Once your bot is running:

1. **Test all flows** - Create, bet, resolve
2. **Invite users** - Share bot link
3. **Monitor activity** - Watch transactions
4. **Add features** - Claim winnings, analytics, etc.
5. **Scale** - Add more markets and users

## 📞 Support

If you encounter issues:

1. Check logs for error messages
2. Verify blockchain connection
3. Test RPC endpoint manually
4. Check contract addresses are correct
5. Ensure wallet has sufficient balance

## 🎉 You're Ready!

Your Escalate prediction market bot is now live and ready to accept bets!

Share your bot with users and start creating markets.
