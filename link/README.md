# Open Price LINK Data Repository
Open Price LINK is an open-data initiative providing a standardized, continuously updated historical dataset of LINK/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into LINK price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink LINK/USD**        | 2026-05-30 12:03:11 UTC      | `data/chainlink_link_usd.csv`                |
| **Uniswap V3 LINK/USDC**     | 2026-05-30 12:52:35 UTC        | `data/link_usdc_uniswap_v3_03.csv`           |
| **Uniswap V3 LINK/USDT**     | 2026-05-30 12:55:47 UTC           | `data/link_usdt_uniswap_v3_03.csv`           |
| **Uniswap V3 LINK/WETH**     | 2026-05-30 11:20:47 UTC        | `data/link_weth_uniswap_v3_03.csv`           |
| **SushiSwap V3 LINK/ETH**    | 2026-05-30 12:11:35 UTC       | `data/link_eth_sushiswap_v3_03.csv`          |
| **Uniswap V2 LINK/WETH**     | 2026-05-30 11:20:23 UTC        | `data/link_weth_uniswap_v2_03.csv`           |
| **SushiSwap V2 LINK/ETH**    | 2026-05-30 08:47:23 UTC       | `data/link_eth_sushiswap_v2_03.csv`          |

---

## 🗂 CSV Structure: `chainlink_link_usd.csv`

**Round identification**

| Column              | Type    | Description                                                    | Method       |
|---------------------|---------|----------------------------------------------------------------|--------------|
| `global_round_id`   | uint80  | Global round identifier (`phase << 64 | aggregator_round_id`) | script-local |
| `phase`             | int     | Chainlink proxy contract phase identifier                      | script-local |
| `aggregator_round`  | int     | Round identifier within the current phase                      | script-local |

**Round data**

| Column                  | Type    | Description                                                                      | Method                                      |
|-------------------------|---------|----------------------------------------------------------------------------------|---------------------------------------------|
| `round_updated_at_utc`  | string  | UTC timestamp when the round was updated (`YYYY-MM-DD HH:MM:SS+00:00`)          | `eth_call:getRoundData` → `updatedAt`       |
| `answer_normalized`     | float   | Price in quote asset: `answer_raw / 10^feed_decimals`                            | computed                                    |
| `answer_raw`            | int256  | Raw answer returned by the Chainlink contract                                    | `eth_call:getRoundData` → `answer`          |
| `answered_in_round`     | uint80  | Round in which the answer was definitively committed                             | `eth_call:getRoundData` → `answeredInRound` |
| `round_started_at_utc`  | string  | UTC timestamp when the round was started (`YYYY-MM-DD HH:MM:SS+00:00`)          | `eth_call:getRoundData` → `startedAt`       |
| `answer_status`         | string  | Computed status: `ok`, `zero_answer`, `negative_answer`, `answered_in_old_round` | computed                                    |

**Extraction metadata**

| Column                           | Type    | Description                                                      | Method                                  |
|----------------------------------|---------|------------------------------------------------------------------|-----------------------------------------|
| `extraction_run_id`              | string  | UUID identifying this extraction run                             | script-local (`uuid4`)                  |
| `schema_version`                 | string  | CSV schema version (e.g. `chainlink_price_feed_v1`)              | config                                  |
| `extraction_timestamp_utc`       | string  | UTC timestamp of extraction start                                | script-local                            |
| `client_name`                    | string  | Ethereum client name of the RPC node                             | `web3_clientVersion` (before first `/`) |
| `client_version`                 | string  | Ethereum client version                                          | `web3_clientVersion` (after first `/`)  |
| `node_chain_id`                  | int     | Chain ID reported by the node                                    | `eth_chainId`                           |
| `chain_id`                       | int     | Same as `node_chain_id` (duplicated for standalone file reading) | `eth_chainId`                           |
| `node_head_block_at_extraction`  | int     | Latest block number known at extraction time                     | `eth_blockNumber`                        |
| `node_sync_completion_block`     | int     | Current sync block (= head if node is fully synced)              | `eth_syncing` or `eth_blockNumber`      |
| `rpc_method_used`                | string  | Primary RPC method used to fetch price data                      | config (`eth_call:getRoundData`)        |
| `extraction_script_hash`         | string  | SHA-256 of the Python script that produced this CSV              | `hashlib.sha256(open(__file__).read())` |
| `abi_hash`                       | string  | SHA-256 of the Chainlink ABI string used                         | `hashlib.sha256(abi.encode())`          |

**Feed configuration**

| Column                     | Type    | Description                                                            | Method                             |
|----------------------------|---------|------------------------------------------------------------------------|------------------------------------|
| `network_name`             | string  | Human-readable blockchain network name                                 | config                             |
| `feed_proxy_address`       | string  | Chainlink proxy contract address used as the entry point               | config                             |
| `aggregator_address`       | string  | Active aggregator address for the current phase (`N/A` if unavailable) | `eth_call:phaseAggregators(phase)` |
| `feed_description`         | string  | Official feed description returned by the contract                     | `eth_call:description()`           |
| `base_asset`               | string  | Base asset of the price pair                                           | config                             |
| `quote_asset`              | string  | Quote asset of the price pair                                          | config                             |
| `feed_decimals`            | int     | Number of decimals used by the feed (8 for standard USD feeds)         | `eth_call:decimals()`              |
| `chainlink_version`        | int     | Version of the `AggregatorV3Interface` contract                        | `eth_call:version()`               |
| `heartbeat_seconds`        | int     | Maximum update interval in seconds (from Chainlink documentation)      | config                             |
| `deviation_threshold_bps`  | int     | Price deviation threshold that triggers an update (in basis points)    | config                             |

## 🗂 CSV Structure: `link_usdc_uniswap_v3_03.csv`

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_link` | float   | LINK price in USDC derived from `sqrtPriceX96` (LINK=token0 formula: `sqrtP²×1e12`)         |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `link_amount`         | float   | LINK leg of the swap (signed: positive = LINK into pool, negative = LINK out of pool)       |
| `volume_usdc`         | float   | Trade notional in USDC — absolute value of the USDC leg (`abs(usdc_amount)`)                |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block (ordering within multi-log transactions)                          |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier in hundredths of a basis point (3000 = 0.3%)                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity of the pool at the time of the swap                               |
| `tick`                | int24   | Current tick of the pool at the time of the swap                                             |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + LINK balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→LINK swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v3_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de sync (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap` ou `sushiswap`) | config |
| `dex_version` | string | Version du protocole (`v3` ou `v2`) | config |
| `token0_address` | string | Adresse du contrat token0 | config |
| `token1_address` | string | Adresse du contrat token1 | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Décimales de token0 | config |
| `token1_decimals` | int | Décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap | `topic2` du log |
| `swap_direction` | string | `token0_to_token1` ou `token1_to_token0` | calculé depuis le signe de `amount0_raw` |
| `base_token_address` | string | Adresse du token de base | config |
| `quote_token_address` | string | Adresse du token de cotation | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode de calcul du prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil TVL pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap 10× plus grand que `slip_1k` | calculé via QuoterV2 ou formule AMM |
| `quality_flags` | string | Drapeaux qualité (`low_liquidity`, `zero_amount`, `extreme_slippage`, ou `ok`) | calculé |

## 🗂 CSV Structure: `link_usdt_uniswap_v3_03.csv`

Same structure as `link_usdc_uniswap_v3_03.csv` with USDT replacing USDC.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdt_per_link` | float   | LINK price in USDT derived from `sqrtPriceX96` (LINK=token0 formula: `sqrtP²×1e12`)         |
| `usdt_amount`         | float   | USDT leg of the swap (signed)                                                                |
| `link_amount`         | float   | LINK leg of the swap (signed)                                                                |
| `volume_usdt`         | float   | Trade notional in USDT — `abs(usdt_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity at the time of the swap                                            |
| `tick`                | int24   | Current tick at the time of the swap                                                         |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD (USDT balance + LINK balance × price)                              |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDT→LINK swap (via QuoterV2)                                     |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v3_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de sync (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap` ou `sushiswap`) | config |
| `dex_version` | string | Version du protocole (`v3` ou `v2`) | config |
| `token0_address` | string | Adresse du contrat token0 | config |
| `token1_address` | string | Adresse du contrat token1 | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Décimales de token0 | config |
| `token1_decimals` | int | Décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap | `topic2` du log |
| `swap_direction` | string | `token0_to_token1` ou `token1_to_token0` | calculé depuis le signe de `amount0_raw` |
| `base_token_address` | string | Adresse du token de base | config |
| `quote_token_address` | string | Adresse du token de cotation | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode de calcul du prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil TVL pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap 10× plus grand que `slip_1k` | calculé via QuoterV2 ou formule AMM |
| `quality_flags` | string | Drapeaux qualité (`low_liquidity`, `zero_amount`, `extreme_slippage`, ou `ok`) | calculé |

## 🗂 CSV Structure: `link_weth_uniswap_v3_03.csv` and `link_eth_sushiswap_v3_03.csv`

Uniswap V3 and SushiSwap V3 LINK/WETH pools. TVL and volume are expressed in WETH. `slip_1k` simulates buying LINK with 1 WETH.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_link` | float   | LINK price in WETH derived from `sqrtPriceX96` (LINK=token0, WETH=token1: `sqrtP²`)         |
| `price_eth_per_link`  | float   | (SushiSwap variant) Same formula, column renamed to `price_eth_per_link`                     |
| `weth_amount`         | float   | WETH leg of the swap (signed)                                                                |
| `eth_amount`          | float   | (SushiSwap variant) Same field, renamed to `eth_amount`                                      |
| `link_amount`         | float   | LINK leg of the swap (signed)                                                                |
| `volume_weth`         | float   | Trade notional in WETH — `abs(weth_amount)`                                                  |
| `volume_eth`          | float   | (SushiSwap variant)                                                                          |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity at the time of the swap                                            |
| `tick`                | int24   | Current tick at the time of the swap                                                         |
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH balance + LINK balance × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→LINK swap (via QuoterV2 for V3, N/A for pre-deployment blocks)   |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v3_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de sync (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap` ou `sushiswap`) | config |
| `dex_version` | string | Version du protocole (`v3` ou `v2`) | config |
| `token0_address` | string | Adresse du contrat token0 | config |
| `token1_address` | string | Adresse du contrat token1 | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Décimales de token0 | config |
| `token1_decimals` | int | Décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap | `topic2` du log |
| `swap_direction` | string | `token0_to_token1` ou `token1_to_token0` | calculé depuis le signe de `amount0_raw` |
| `base_token_address` | string | Adresse du token de base | config |
| `quote_token_address` | string | Adresse du token de cotation | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode de calcul du prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil TVL pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap 10× plus grand que `slip_1k` | calculé via QuoterV2 ou formule AMM |
| `quality_flags` | string | Drapeaux qualité (`low_liquidity`, `zero_amount`, `extreme_slippage`, ou `ok`) | calculé |

## 🗂 CSV Structure: `link_weth_uniswap_v2_03.csv` and `link_eth_sushiswap_v2_03.csv`

Uniswap V2 and SushiSwap V2 LINK/WETH pools. Price derived from swap amounts; reserves fetched via `getReserves()`. TVL and volume in WETH. `slip_1k` uses the analytical V2 formula.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_weth_per_link` | float   | Effective LINK price in WETH from swap amounts (`\|WETH_net\| / \|LINK_net\|`)               |
| `price_eth_per_link`  | float   | (SushiSwap variant)                                                                          |
| `weth_amount`         | float   | WETH net flow (positive = into pool, negative = out of pool)                                 |
| `eth_amount`          | float   | (SushiSwap variant)                                                                          |
| `link_amount`         | float   | LINK net flow (signed)                                                                       |
| `volume_weth`         | float   | Trade notional in WETH — `abs(weth_amount)`                                                  |
| `volume_eth`          | float   | (SushiSwap variant)                                                                          |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (LINK) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in WETH (WETH reserve + LINK reserve × price)                             |
| `slip_1k`             | float   | Simulated cost of a 1 WETH→LINK swap using the V2 analytical formula                        |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v3_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de sync (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap` ou `sushiswap`) | config |
| `dex_version` | string | Version du protocole (`v3` ou `v2`) | config |
| `token0_address` | string | Adresse du contrat token0 | config |
| `token1_address` | string | Adresse du contrat token1 | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Décimales de token0 | config |
| `token1_decimals` | int | Décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap | `topic2` du log |
| `swap_direction` | string | `token0_to_token1` ou `token1_to_token0` | calculé depuis le signe de `amount0_raw` |
| `base_token_address` | string | Adresse du token de base | config |
| `quote_token_address` | string | Adresse du token de cotation | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode de calcul du prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil TVL pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap 10× plus grand que `slip_1k` | calculé via QuoterV2 ou formule AMM |
| `quality_flags` | string | Drapeaux qualité (`low_liquidity`, `zero_amount`, `extreme_slippage`, ou `ok`) | calculé |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**
