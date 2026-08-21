# Reading Polymarket Like an Order Book: A Field Guide

*Companion guide to pmkit. Written from live scanning data collected August 2026.*

## 1. Two APIs, one market

Polymarket has two public surfaces:

- **Gamma API** (`gamma-api.polymarket.com`) - the catalog: markets, events,
  outcome prices, volumes, metadata.
- **CLOB API** (`clob.polymarket.com`) - the order books: resting bids/asks
  per outcome token.

Gamma tells you what markets exist. CLOB tells you what you can actually
trade. Confusing the two is the number-one mistake in Polymarket tooling.

## 2. The phantom-arb trap

Scan Gamma midpoints for `YES + NO < 1` or negRisk events whose probabilities
sum above 1, and you will find dozens of "arbitrages" every day. We did -
61 deviations on a single scan. Then we checked the order books.

Most were fake:

- **Zombie markets**: resolved or dead events whose resting orders were never
  cancelled. Prices look wildly wrong because nobody can trade them.
- **Micro-depth**: the best bid exists but is 3 shares deep. Your fill eats
  through it instantly.

**Rule: a deviation that survives book-depth validation is rare.** On our
scan day: 2,100 binary markets -> zero executable spreads. 62 negRisk
candidates -> one survived at ~$3.40 max fill. That is what an efficient,
bot-saturated market looks like.

## 3. What the scanners are actually for

If pure arb is competed away, why scan? Because the scanner output is a
*market-quality map*:

- Events with persistent small deviations are where liquidity lives.
- Sudden deviation spikes mark news shocks - volatility windows.
- Sub-market sums drifting over time reveal where flow is one-sided.

Traders use these signals for entries, not free money. pmkit gives you the
raw signal; the interpretation is your job.

## 4. Paper-trade first, always

pmkit's paper ledger simulates fills at stated prices. Run any idea against
live books for at least a week before considering capital. If a strategy
cannot survive simulation at optimistic prices, reality will be worse.

## 5. Pre-capital checklist

Before risking a dollar:

1. Scanner says opportunity exists (not just once - persistently).
2. Book depth supports your size at your price.
3. You understand resolution rules for every market you touch.
4. You have simulated the strategy for 100+ fills.
5. You accept that backtested/simulated edge routinely evaporates live.

Nothing in this guide is financial advice. Prediction markets can go to
zero on your position overnight. Size accordingly.
