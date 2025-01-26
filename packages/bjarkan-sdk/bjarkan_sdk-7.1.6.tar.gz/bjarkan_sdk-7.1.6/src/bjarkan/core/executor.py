import asyncio
from typing import Dict, List
import ccxt.pro as ccxt
import time
from bjarkan.models import OrderbookConfig, OrderConfig, APIConfig
from bjarkan.utils.logger import logger, catch_exception
from bjarkan.exceptions import BjarkanError


class OrderExecutor:
    @catch_exception
    def __init__(self, orderbook_config: OrderbookConfig, api_configs: List[APIConfig]):
        if not orderbook_config.aggregated or len(orderbook_config.symbols) != 1:
            raise ValueError("OrderExecutor requires aggregated data and exactly one symbol in orderbook_config")

        self.orderbook_config = orderbook_config
        self.api_configs = {config.exchange: config for config in api_configs}
        self.exchanges = {}
        self.symbol = orderbook_config.symbols[0]
        self.latest_orderbook = None

        # Validate and initialize exchanges
        self._initialize_exchanges()

    @catch_exception
    def _initialize_exchanges(self):
        """Initialize exchange connections with error handling."""
        for exchange_id in self.orderbook_config.exchanges:
            if exchange_id not in self.api_configs:
                continue  # Skip exchanges without API configs

            config = self.api_configs[exchange_id]
            exchange_class = getattr(ccxt, exchange_id)

            try:
                exchange = exchange_class({
                    'apiKey': config.api_key,
                    'secret': config.secret,
                    'password': config.password,
                    'enableRateLimit': True,
                })

                # Test authentication
                exchange.check_required_credentials()

                is_sandbox = self.orderbook_config.sandbox_mode.get(exchange_id, False)
                exchange.set_sandbox_mode(is_sandbox)

                self.exchanges[exchange_id] = exchange

            except ccxt.AuthenticationError as e:
                logger.error(f"Authentication failed for {exchange_id}: {str(e)}")
                raise BjarkanError(f"Invalid API credentials for {exchange_id}")
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_id}: {str(e)}")
                raise BjarkanError(f"Failed to initialize {exchange_id}: {str(e)}")

        if not self.exchanges:
            raise BjarkanError("No exchanges could be initialized with provided API configurations")

    @catch_exception
    def _prepare_margin_params(self, exchange_id: str, order: OrderConfig, base_params: Dict) -> Dict:
        """Prepare exchange-specific margin trading parameters."""
        params = base_params.copy()

        if order.margin_mode:
            if exchange_id == 'binance':
                params['type'] = 'margin'
                params['marginMode'] = 'cross'
                # params['marginMode'] = 'isolated'
            elif exchange_id == 'bybit':
                params['isLeverage'] = 1
                params['leverageType'] = 'cross_margin'
                params['spotMarginTrading'] = True
                params['marginTrading'] = True
            elif exchange_id == 'okx':
                params['tdMode'] = 'cross'
                # params['tdMode'] = 'isolated'
            elif exchange_id == 'kucoin':
                params['marginMode'] = 'cross'
                params['tradeType'] = 'MARGIN_TRADE'
                params['autoBorrow'] = True
            elif exchange_id == 'gate':
                params['account'] = 'cross_margin'
                params['auto_borrow'] = True
                # params['account'] = 'margin'
            elif exchange_id == 'bitget':
                params['marginMode'] = 'cross'
                params['loanType'] = 'autoLoanAndRepay'
                # params['marginMode'] = 'isolated'
            else:
                logger.warning(f"Margin trading might not be properly configured for {exchange_id}")

            logger.info(f"Prepared margin parameters for {exchange_id}: {params}")

        return params

    @catch_exception
    async def update_orderbook(self, orderbook: Dict):
        """Update the latest orderbook data."""
        if self.symbol not in orderbook:
            raise BjarkanError(f"No orderbook data available for symbol {self.symbol}")
        self.latest_orderbook = orderbook[self.symbol]

    @catch_exception
    async def execute_order(self, order: OrderConfig) -> Dict:
        """Execute market orders across available exchanges."""
        if not self.latest_orderbook:
            raise BjarkanError("No orderbook data available")

        if not self.exchanges:
            raise BjarkanError("No exchanges initialized with valid API keys")

        execution_plan = self._create_execution_plan(order)
        if not execution_plan:
            raise BjarkanError("Could not create valid execution plan with available liquidity")

        start_time = time.time()

        async def execute_single_order(exchange_id: str, amount: float):
            """Execute a single market order on one exchange."""
            execution_start_time = time.time()
            try:
                exchange = self.exchanges[exchange_id]
                params = self._prepare_margin_params(exchange_id, order, {})  # Empty base_params

                logger.info(f"Executing market order on {exchange_id}: {order.side} {amount} {self.symbol} "
                            f"with margin_mode={order.margin_mode}")

                executed_order = await exchange.createOrder(
                    self.symbol,
                    'market',
                    order.side,
                    amount,
                    None,
                    params
                )

                execution_time = round((time.time() - execution_start_time) * 1000, 2)
                filled_amount = float(executed_order.get('filled', 0) or 0)

                return {
                    "exchange": exchange_id,
                    "order": executed_order,
                    "status": "success",
                    "planned_amount": amount,
                    "filled_amount": filled_amount,
                    "actual_price": executed_order.get('price'),
                    "margin_mode": order.margin_mode,
                    "execution_time": execution_time
                }

            except Exception as e:
                execution_time = round((time.time() - execution_start_time) * 1000, 2)
                logger.error(f"Error executing order on {exchange_id}: {str(e)}")
                return {
                    "exchange": exchange_id,
                    "error": str(e),
                    "status": "failed",
                    "planned_amount": amount,
                    "margin_mode": order.margin_mode,
                    "execution_time": execution_time
                }

        # Execute all orders in parallel
        execution_tasks = [
            execute_single_order(exchange_id, amount)
            for exchange_id, amount in execution_plan
        ]
        execution_results = await asyncio.gather(*execution_tasks)

        # Calculate totals from results
        total_filled_amount = sum(
            result['filled_amount']
            for result in execution_results
            if result['status'] == 'success'
        )
        remaining_amount = max(0, order.amount - total_filled_amount)

        # Get execution statistics
        total_time = time.time() - start_time
        execution_times = {
            result['exchange']: result['execution_time']
            for result in execution_results
        }

        fastest_exchange = min(execution_times.items(), key=lambda x: x[1])
        slowest_exchange = max(execution_times.items(), key=lambda x: x[1])

        result = {
            "status": "completed" if remaining_amount <= 1e-8 else "partially_filled",
            "original_amount": order.amount,
            "filled_amount": total_filled_amount,
            "remaining_amount": remaining_amount,
            "execution_results": execution_results,
            "execution_plan": execution_plan,
            "total_execution_time": round(total_time * 1000, 2),
            "margin_mode": order.margin_mode,
            "execution_metrics": {
                "fastest_exchange": {
                    "exchange": fastest_exchange[0],
                    "time": fastest_exchange[1]
                },
                "slowest_exchange": {
                    "exchange": slowest_exchange[0],
                    "time": slowest_exchange[1]
                },
                "parallel_efficiency": round(
                    max(execution_times.values()) / total_time * 100, 2
                )
            }
        }

        # Log execution metrics
        logger.info(f"Order execution metrics:")
        logger.info(f"Total time: {result['total_execution_time']}ms")
        logger.info(f"Fastest exchange: {fastest_exchange[0]} ({fastest_exchange[1]}ms)")
        logger.info(f"Slowest exchange: {slowest_exchange[0]} ({slowest_exchange[1]}ms)")
        logger.info(f"Parallel efficiency: {result['execution_metrics']['parallel_efficiency']}%")

        return result

    @catch_exception
    def _create_execution_plan(self, order: OrderConfig) -> List[tuple]:
        """Create an execution plan for market orders based on available liquidity."""
        execution_plan = []
        remaining_amount = order.amount
        book_side = self.latest_orderbook['bids'] if order.side == 'sell' else self.latest_orderbook['asks']

        # Get market precision info
        exchange_precisions = {}
        for exchange_id in self.exchanges:
            market = self.exchanges[exchange_id].market(self.symbol)
            # Get precision for the base currency (amount)
            precision = market.get('precision', {}).get('amount', None)
            if precision is not None:
                exchange_precisions[exchange_id] = precision

        # Consolidate liquidity by exchange
        exchange_liquidity = {}
        for _, size, exchange in book_side:
            if exchange in self.exchanges:
                exchange_liquidity[exchange] = exchange_liquidity.get(exchange, 0) + size

        # Allocate amounts to exchanges based on their total liquidity
        for exchange, total_liquidity in exchange_liquidity.items():
            if remaining_amount <= 0:
                break

            executable_amount = min(remaining_amount, total_liquidity)

            # Round according to exchange precision
            if exchange in exchange_precisions:
                precision = exchange_precisions[exchange]
                executable_amount = round(executable_amount, precision)
                if executable_amount == 0:  # Skip if rounded to zero
                    continue

            execution_plan.append((exchange, executable_amount))
            remaining_amount -= executable_amount

        # Log the execution plan
        logger.info(f"Created market order execution plan:")
        for exchange, amount in execution_plan:
            logger.info(f"- {exchange}: {amount}")

        return execution_plan

    @catch_exception
    async def close(self):
        """Close all exchange connections."""
        close_tasks = []
        for exchange in self.exchanges.values():
            if hasattr(exchange, 'close'):
                close_tasks.append(exchange.close())

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
