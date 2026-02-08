# Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram Users                          │
│                    (Private & Group Chats)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Bot API                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Bot Initialization & Dispatcher                      │  │
│  │  - aiogram v3                                         │  │
│  │  - FSM Storage (Memory)                               │  │
│  │  - Router Registration                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌─────────────┐
│  bot/handlers/ │ │ bot/       │ │ services/   │
│                │ │            │ │             │
│  • start.py    │ │ • states   │ │ • blockchain│
│  • markets.py  │ │ • keyboards│ │             │
│  • create.py   │ │            │ │             │
│  • bet.py      │ │            │ │             │
│  • resolve.py  │ │            │ │             │
└────────┬───────┘ └────────────┘ └──────┬──────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   BlockchainService           │
         │                               │
         │   • Web3 Provider             │
         │   • Contract Instances        │
         │   • Transaction Management    │
         │   • Async Operations          │
         └───────────────┬───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Monad Testnet RPC           │
         └───────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐           ┌──────────────────┐
│ Escalate        │           │ USDC Token       │
│ Smart Contract  │           │ (ERC20)          │
│                 │           │                  │
│ • createMarket  │           │ • approve        │
│ • placeBet      │           │ • allowance      │
│ • resolveMarket │           │ • balanceOf      │
│ • markets       │           │                  │
│ • marketCount   │           │                  │
└─────────────────┘           └──────────────────┘
```

## 📊 Data Flow

### Market Creation Flow

```
User → /start → Create Market Button
                      ↓
              Enter Question (FSM)
                      ↓
              Enter Expiry (FSM)
                      ↓
              Confirm Creation
                      ↓
          BlockchainService.create_market()
                      ↓
          Build Transaction → Sign → Send
                      ↓
          Wait for Receipt → Get Market ID
                      ↓
          Display Success + TX Hash
```

### Betting Flow

```
User → View Markets → Select Market
                      ↓
              Choose YES/NO (FSM)
                      ↓
              Enter Amount (FSM)
                      ↓
              Confirm Bet
                      ↓
          BlockchainService.approve_usdc()
                      ↓
          Wait for Approval TX
                      ↓
          BlockchainService.place_bet()
                      ↓
          Wait for Bet TX
                      ↓
          Fetch Updated Market Data
                      ↓
          Display Updated Pools
```

### Market Viewing Flow

```
User → View Markets Button
              ↓
    BlockchainService.get_market_count()
              ↓
    Loop: get_market(1..count)
              ↓
    Filter: !resolved && expiry > now
              ↓
    Format: Pools, Liquidity, Time
              ↓
    Display with Inline Buttons
```

## 🔄 State Management

### FSM States

```
CreateMarketStates:
  entering_question → entering_expiry → confirming

PlaceBetStates:
  selecting_market → selecting_side → entering_amount → confirming_bet

ResolveMarketStates:
  entering_market_id → entering_outcome → confirming_resolution
```

### State Storage

- **Type**: In-Memory (MemoryStorage)
- **Scope**: Per-user conversation
- **Lifecycle**: Cleared on completion or cancel
- **Data**: Temporary form inputs only

## 🔐 Security Model

### Access Control

```
┌─────────────────────────────────────┐
│  Public Actions                     │
│  • View markets                     │
│  • Create markets                   │
│  • Place bets                       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Resolver-Only Actions              │
│  • Resolve markets                  │
│  • Check: wallet == RESOLVER_ADDRESS│
└─────────────────────────────────────┘
```

### Transaction Security

```
User Input → Validation → Confirmation
                              ↓
                    Build Transaction
                              ↓
                    Sign with Private Key
                              ↓
                    Send to RPC
                              ↓
                    Wait for Receipt
                              ↓
                    Verify Status == 1
```

## 📦 Module Responsibilities

### `main.py`
- Bot initialization
- Dispatcher setup
- Router registration
- Startup validation
- Logging configuration

### `config.py`
- Environment variable loading
- Configuration validation
- Constants definition
- Type safety

### `services/blockchain.py`
- Web3 connection management
- Contract interaction
- Transaction building & signing
- Gas estimation
- Error handling
- Amount formatting

### `bot/states.py`
- FSM state definitions
- State groups
- Conversation flow structure

### `bot/keyboards.py`
- Inline keyboard layouts
- Button generation
- Callback data formatting
- Navigation structure

### `bot/handlers/`
- **start.py**: Main menu, navigation
- **markets.py**: Market listing, viewing
- **create.py**: Market creation flow
- **bet.py**: Betting flow
- **resolve.py**: Resolution flow

## 🎯 Design Principles

### 1. **No Database**
- All data from blockchain
- No caching layer
- Live data fetching
- Stateless (except FSM)

### 2. **Async Everything**
- aiogram v3 async
- web3.py async calls
- Non-blocking I/O
- Concurrent operations

### 3. **Modular Architecture**
- Separation of concerns
- Single responsibility
- Easy to extend
- Clean imports

### 4. **Error Resilience**
- Graceful error handling
- User-friendly messages
- Retry logic
- Fallback states

### 5. **Polymarket UX**
- Clean market display
- Visible liquidity
- Time countdown
- Pool visualization
- Instant updates

## 🔧 Extension Points

### Easy to Add:

1. **Claim Winnings Flow**
   - New handler: `claim.py`
   - New state: `ClaimStates`
   - Contract method: `claimWinnings()`

2. **Market Analytics**
   - New handler: `analytics.py`
   - Calculate ROI, volume, etc.
   - Display charts (via image generation)

3. **User Portfolio**
   - Track user bets
   - Show P&L
   - Display history

4. **Notifications**
   - Market expiry alerts
   - Resolution notifications
   - Price movement alerts

5. **Advanced Features**
   - Limit orders
   - Partial exits
   - Market making
   - Liquidity provision

## 📈 Scalability

### Current Limits:
- **Markets per view**: 5 (configurable)
- **Concurrent users**: Unlimited (async)
- **RPC calls**: Rate-limited by provider
- **Memory**: Minimal (no caching)

### Scaling Strategies:
1. **Multiple bot instances** - Load balancing
2. **RPC pooling** - Multiple endpoints
3. **Caching layer** - Redis for hot data
4. **Database** - For analytics only
5. **Webhooks** - Instead of polling

## 🎨 UX Philosophy

### Polymarket-Inspired:
- **Clarity**: Clear market questions
- **Transparency**: Visible pools
- **Speed**: Instant updates
- **Trust**: On-chain verification
- **Simplicity**: One-tap betting

### Telegram-Native:
- **Inline keyboards**: No typing
- **Markdown formatting**: Rich text
- **Group chat support**: Social betting
- **Mobile-first**: Touch-friendly
- **Instant feedback**: Loading states

---

This architecture provides a solid foundation for a production-grade prediction market bot while remaining simple, maintainable, and extensible.
