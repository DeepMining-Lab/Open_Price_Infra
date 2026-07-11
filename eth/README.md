# Open Price ETH Data Repository
Open Price ETH is an open-data initiative providing a standardized, continuously updated historical dataset of ETH/USD prices from on-chain sources (Chainlink and Uniswap V3). Fully compliant with FAIR principles, it empowers researchers and developers with transparent, reproducible insights into Ethereum price dynamics.

---

## 📅 Available Datasets

| Dataset                          | End Date Available              | CSV File                                      |
|----------------------------------|---------------------------------|-----------------------------------------------|
| **Chainlink ETH/USD**         | 2026-07-11 15:40:35 UTC      | `data/chainlink_eth_usd.csv`                  |
| **Uniswap V3 ETH/USDC**      | 2026-07-11 16:16:59 UTC        | `data/eth_usdc_uniswap_v3_005.csv`            |
| **Uniswap V2 WETH/USDC**     | 2026-07-11 16:20:35 UTC   | `data/weth_usdc_uniswap_v2_03.csv`            |
| **Uniswap V2 WETH/USDT**     | 2026-07-11 16:18:59 UTC   | `data/weth_usdt_uniswap_v2_03.csv`            |
| **Curve crvUSD/WETH**        | N/A         | `data/crvusd_weth_curve.csv`                  |

---

## 🗂 CSV Structure: `chainlink_eth_usd.csv`

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

## 🗂 CSV Structure: `eth_usdc_uniswap_v3_005.csv`

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                                |
| `price_usdc_per_eth`  | float   | ETH price in USDC derived from `sqrtPriceX96` (USDC=token0 formula: `1/(sqrtP²×1e-12)`)    |
| `usdc_amount`         | float   | USDC leg of the swap (signed: positive = USDC into pool, negative = USDC out of pool)       |
| `eth_amount`          | float   | WETH leg of the swap (signed: positive = WETH into pool, negative = WETH out of pool)       |
| `volume_usdc`         | float   | Trade notional in USDC — absolute value of the USDC leg (`abs(usdc_amount)`)                |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block (ordering within multi-log transactions)                          |
| `pool_address`        | string  | Uniswap V3 pool contract address                                                             |
| `pool_fee_tier`       | int     | Pool fee tier in hundredths of a basis point (500 = 0.05%)                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `sqrt_price_x96`      | uint160 | Raw `sqrtPriceX96` value from the Swap event                                                 |
| `liquidity`           | uint128 | Active in-range liquidity of the pool at the time of the swap                               |
| `tick`                | int24   | Current tick of the pool at the time of the swap                                             |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD at the swap block (USDC balance + WETH balance × price)           |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→WETH swap: price impact + fee tier (via QuoterV2). `None` for pre-2022 blocks (QuoterV2 not yet deployed). |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction (relie toutes les lignes d'une même extraction) | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v3_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au moment du lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Numéro du dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de synchronisation (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées pour l'extraction | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap utilisée | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom lisible du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo (`transaction_index`) |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap`, `sushiswap`, `curve`) | config |
| `dex_version` | string | Version du protocole (`v3`, `v2`, etc.) | config |
| `token0_address` | string | Adresse du contrat token0 du pool | config |
| `token1_address` | string | Adresse du contrat token1 du pool | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Nombre de décimales de token0 | config |
| `token1_decimals` | int | Nombre de décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap (`sender` dans l'event) | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap (`recipient` dans l'event) | `topic2` du log |
| `swap_direction` | string | Direction du swap : `token0_to_token1` ou `token1_to_token0` (déduit du signe de `amount0_raw`) | calculé |
| `base_token_address` | string | Adresse du token de base (token pricé) | config |
| `quote_token_address` | string | Adresse du token de cotation (référence) | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode utilisée pour calculer le prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil de TVL (en USD ou équivalent) utilisé pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap de 10 000 USDC→WETH, calculé par la même méthode que `slip_1k` via QuoterV2 | calculé via QuoterV2 |
| `quality_flags` | string | Drapeaux qualité séparés par `\|` : `low_liquidity`, `zero_amount`, `extreme_slippage` ; `ok` si aucun | calculé |

## 🗂 CSV Structure: `weth_usdc_uniswap_v2_03.csv`

Uniswap V2 WETH/USDC pool (USDC=token0, WETH=token1). Price from swap amounts; reserves from `getReserves()`. `slip_1k` simulates buying WETH with 1 000 USDC.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_usdc_per_eth`  | float   | Effective ETH price in USDC from swap amounts (`\|USDC_net\| / \|WETH_net\|`)                |
| `usdc_amount`         | float   | USDC net flow (positive = into pool)                                                         |
| `eth_amount`          | float   | WETH net flow (positive = into pool)                                                         |
| `volume_usdc`         | float   | Trade notional in USDC — `abs(usdc_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (USDC) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (WETH) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD (USDC reserve + WETH reserve × price)                              |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDC→WETH swap using the V2 analytical formula                    |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction (relie toutes les lignes d'une même extraction) | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v2_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au moment du lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Numéro du dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de synchronisation (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées pour l'extraction | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap utilisée | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom lisible du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo (`transaction_index`) |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap`, `sushiswap`, `curve`) | config |
| `dex_version` | string | Version du protocole (`v3`, `v2`, etc.) | config |
| `token0_address` | string | Adresse du contrat token0 du pool | config |
| `token1_address` | string | Adresse du contrat token1 du pool | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Nombre de décimales de token0 | config |
| `token1_decimals` | int | Nombre de décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap (`sender` dans l'event) | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap (`to` dans l'event) | `topic2` du log |
| `swap_direction` | string | Direction du swap : `token0_to_token1` ou `token1_to_token0` (déduit du signe de `amount0_raw`) | calculé |
| `base_token_address` | string | Adresse du token de base (token pricé) | config |
| `quote_token_address` | string | Adresse du token de cotation (référence) | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode utilisée pour calculer le prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil de TVL (en USD ou équivalent) utilisé pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap de 10 000 USDC→WETH, calculé par la formule AMM V2 | calculé via formule AMM |
| `quality_flags` | string | Drapeaux qualité séparés par `\|` : `low_liquidity`, `zero_amount`, `extreme_slippage` ; `ok` si aucun | calculé |

## 🗂 CSV Structure: `weth_usdt_uniswap_v2_03.csv`

Uniswap V2 WETH/USDT pool (WETH=token0, USDT=token1). `slip_1k` simulates buying WETH with 1 000 USDT.

| Column                | Type    | Description                                                                                  |
|-----------------------|---------|----------------------------------------------------------------------------------------------|
| `timestamp`           | string  | UTC timestamp of the block                                                                   |
| `price_usdt_per_eth`  | float   | Effective ETH price in USDT from swap amounts (`\|USDT_net\| / \|WETH_net\|`)                |
| `eth_amount`          | float   | WETH net flow (positive = into pool)                                                         |
| `usdt_amount`         | float   | USDT net flow (positive = into pool)                                                         |
| `volume_usdt`         | float   | Trade notional in USDT — `abs(usdt_amount)`                                                  |
| `block_number`        | int     | Ethereum block number                                                                        |
| `transaction_hash`    | string  | Transaction hash                                                                             |
| `log_index`           | int     | Log index within the block                                                                   |
| `pool_address`        | string  | Pool contract address                                                                        |
| `pool_fee_tier`       | int     | Pool fee tier (3000 = 0.3%)                                                                  |
| `chain_id`            | int     | Ethereum chain ID (1 = mainnet)                                                              |
| `reserve0`            | uint112 | Raw token0 (WETH) reserve at the swap block                                                  |
| `reserve1`            | uint112 | Raw token1 (USDT) reserve at the swap block                                                  |
| `pool_tvl_at_block`   | float   | Total Value Locked in USD (USDT reserve + WETH reserve × price)                              |
| `slip_1k`             | float   | Simulated cost of a 1 000 USDT→WETH swap using the V2 analytical formula                    |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction (relie toutes les lignes d'une même extraction) | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_uniswap_v2_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au moment du lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Numéro du dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de synchronisation (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées pour l'extraction | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement Swap utilisée | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom lisible du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo (`transaction_index`) |
| `event_signature` | string | Keccak-256 de la signature de l'événement Swap (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`uniswap`, `sushiswap`, `curve`) | config |
| `dex_version` | string | Version du protocole (`v3`, `v2`, etc.) | config |
| `token0_address` | string | Adresse du contrat token0 du pool | config |
| `token1_address` | string | Adresse du contrat token1 du pool | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Nombre de décimales de token0 | config |
| `token1_decimals` | int | Nombre de décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount1_raw` | int | Flux net de token1 en unités brutes (positif = entre dans le pool) | décodage ABI du log Swap |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` | calculé |
| `swap_sender` | string | Adresse de l'envoyeur du swap (`sender` dans l'event) | `topic1` du log |
| `swap_recipient` | string | Adresse du destinataire du swap (`to` dans l'event) | `topic2` du log |
| `swap_direction` | string | Direction du swap : `token0_to_token1` ou `token1_to_token0` (déduit du signe de `amount0_raw`) | calculé |
| `base_token_address` | string | Adresse du token de base (token pricé) | config |
| `quote_token_address` | string | Adresse du token de cotation (référence) | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode utilisée pour calculer le prix (`sqrt_price_x96` ou `amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil de TVL (en USD ou équivalent) utilisé pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap de 10 000 USDT→WETH, calculé par la formule AMM V2 | calculé via formule AMM |
| `quality_flags` | string | Drapeaux qualité séparés par `\|` : `low_liquidity`, `zero_amount`, `extreme_slippage` ; `ok` si aucun | calculé |

---

## 🗂 CSV Structure: `crvusd_weth_curve.csv`

Curve pool `0x6e5492f8Ea2370844eE098a56dD88e1717E4A9C2` — coin0=crvUSD (18 dec), coin1=WETH (18 dec).
Price derived from `TokenExchange` event amounts. TVL in crvUSD (≈ USD). `slip_1k` simulates buying WETH with 1 000 crvUSD via `get_dy()`.

| Column                   | Type   | Description                                                                                |
|--------------------------|--------|--------------------------------------------------------------------------------------------|
| `timestamp`              | string | UTC timestamp of the block, e.g. `2024-04-19 23:59:59+00:00`                              |
| `price_weth_per_crvusd`  | float  | crvUSD price in WETH from swap amounts (`\|WETH_net\| / \|crvUSD_net\|`)                   |
| `crvusd_amount`          | float  | crvUSD net flow (positive = into pool, negative = out of pool)                             |
| `weth_amount`            | float  | WETH net flow (positive = into pool, negative = out of pool)                               |
| `volume_crvusd`          | float  | Trade notional in crvUSD — `abs(crvusd_amount)`                                            |
| `block_number`           | int    | Ethereum block number                                                                      |
| `transaction_hash`       | string | Transaction hash                                                                           |
| `log_index`              | int    | Log index within the block                                                                 |
| `pool_address`           | string | Curve pool contract address                                                                |
| `chain_id`               | int    | Ethereum chain ID (1 = mainnet)                                                            |
| `pool_tvl_at_block`      | float  | Total Value Locked in crvUSD (≈ USD): crvUSD balance + WETH balance / price               |
| `slip_1k`                | float  | Simulated cost of a 1 000 crvUSD→WETH swap via Curve `get_dy(0, 1, dx)`                   |

**Metadata d'extraction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `extraction_run_id` | string | UUID identifiant l'exécution d'extraction (relie toutes les lignes d'une même extraction) | script-local (`uuid4`) |
| `schema_version` | string | Version du schéma CSV (ex. `dex_curve_v1`) | config |
| `extraction_timestamp_utc` | string | Timestamp UTC au moment du lancement du script | script-local |
| `client_name` | string | Nom du client Ethereum du nœud RPC | `web3_clientVersion` (avant le premier `/`) |
| `client_version` | string | Version du client Ethereum | `web3_clientVersion` (après le premier `/`) |
| `node_chain_id` | int | Chain ID rapporté par le nœud | `eth_chainId` |
| `node_head_block_at_extraction` | int | Numéro du dernier bloc connu au moment de l'extraction | `eth_blockNumber` |
| `node_sync_completion_block` | int | Bloc courant de synchronisation (= head si nœud synchronisé) | `eth_syncing` ou `eth_blockNumber` |
| `rpc_method_used` | string | Méthodes RPC utilisées pour l'extraction | config |
| `extraction_script_hash` | string | SHA-256 du fichier Python ayant produit ce CSV | `hashlib.sha256(open(__file__,'rb').read())` |
| `abi_hash` | string | SHA-256 de l'ABI de l'événement TokenExchange utilisée | `hashlib.sha256(SWAP_EVENT_ABI.encode())` |
| `network_name` | string | Nom lisible du réseau blockchain | config |

**Métadonnées de bloc et transaction**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `block_timestamp_utc` | string | Timestamp UTC du bloc (identique à `timestamp`) | `eth_getBlockByNumber` → `timestamp` |
| `block_hash` | string | Hash du bloc | `eth_getBlockByNumber` → `hash` |
| `transaction_index` | int | Index de la transaction dans le bloc | issu du CSV cryo (`transaction_index`) |
| `event_signature` | string | Keccak-256 de la signature de l'événement TokenExchange (= `topic0`) | config |

**Métadonnées DEX et tokens**

| Colonne | Type | Description | Méthode |
|---------|------|-------------|---------|
| `dex_protocol` | string | Protocole DEX (`curve`) | config |
| `dex_version` | string | Version du protocole (vide pour Curve) | config |
| `token0_address` | string | Adresse du contrat token0 du pool (crvUSD) | config |
| `token1_address` | string | Adresse du contrat token1 du pool (WETH) | config |
| `token0_symbol` | string | Symbole de token0 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token1_symbol` | string | Symbole de token1 | `eth_call:symbol()` sur le contrat ERC-20 |
| `token0_decimals` | int | Nombre de décimales de token0 | config |
| `token1_decimals` | int | Nombre de décimales de token1 | config |
| `amount0_raw` | int | Flux net de token0 (crvUSD) en unités brutes (positif = entre dans le pool) | décodage ABI du log TokenExchange |
| `amount1_raw` | int | Flux net de token1 (WETH) en unités brutes (positif = entre dans le pool) | décodage ABI du log TokenExchange |
| `amount0_normalized` | float | `amount0_raw / 10^token0_decimals` (identique à `crvusd_amount`) | calculé |
| `amount1_normalized` | float | `amount1_raw / 10^token1_decimals` (identique à `weth_amount`) | calculé |
| `swap_sender` | string | Adresse de l'acheteur (`buyer` dans l'event) | `topic1` du log |
| `swap_recipient` | string | Toujours `None` — l'event `TokenExchange` Curve n'a pas de champ recipient | N/A |
| `swap_direction` | string | Direction du swap : `token0_to_token1` ou `token1_to_token0` (déduit de `sold_id`) | calculé |
| `base_token_address` | string | Adresse du token de base (crvUSD) | config |
| `quote_token_address` | string | Adresse du token de cotation (WETH) | config |
| `base_token_symbol` | string | Symbole du token de base | config |
| `quote_token_symbol` | string | Symbole du token de cotation | config |
| `price_source_field` | string | Méthode utilisée pour calculer le prix (`amount_ratio`) | config |
| `pool_tvl_threshold_used` | int | Seuil de TVL (en USD ou équivalent) utilisé pour le flag `low_liquidity` | config |
| `slip_10k` | float | Slippage simulé pour un swap de 10 000 crvUSD→WETH via Curve `get_dy(0, 1, dx)` | calculé via `get_dy` |
| `quality_flags` | string | Drapeaux qualité séparés par `\|` : `low_liquidity`, `zero_amount`, `extreme_slippage` ; `ok` si aucun | calculé |

---

## 🧾 License

All contents of this repository (data, code, and documentation) are licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH**
