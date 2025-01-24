import warnings
from dataclasses import dataclass, field, fields
from datetime import datetime

import numpy as np
import pandas as pd

from finter.backtest.v0.config import (
    CacheConfig,
    CostConfig,
    DataConfig,
    DateConfig,
    ExecutionConfig,
    FrameConfig,
    OptionalConfig,
    SimulatorConfig,
)
from finter.backtest.v0.simulators.base import BaseBacktestor
from finter.backtest.v0.simulators.basic import BasicBacktestor
from finter.backtest.v0.simulators.id_fund import IDFundBacktestor
from finter.backtest.v0.simulators.vars import InputVars
from finter.backtest.v0.simulators.vn import VNBacktestor
from finter.modeling.utils import daily2period, get_rebalancing_mask

POSITION_SCALAR = 1e8
BASIS_POINT_SCALAR = 10000


@dataclass
class SimulatorBuilder:
    data: DataConfig = field(default_factory=DataConfig)

    date: DateConfig = field(default_factory=DateConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    optional: OptionalConfig = field(default_factory=OptionalConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    frame: FrameConfig = field(default_factory=FrameConfig)

    def __repr__(self) -> str:
        return (
            "SimulatorBuilder(\n"
            f"    data={self.data},\n"
            f"    date={self.date},\n"
            f"    cost={self.cost},\n"
            f"    execution={self.execution},\n"
            f"    optional={self.optional},\n"
            f"    cache={self.cache},\n"
            f"    frame={self.frame}\n"
            ")"
        )

    def build(self, position: pd.DataFrame) -> BaseBacktestor:
        start_date = datetime.strptime(str(self.date.start), "%Y%m%d")
        end_date = datetime.strptime(str(self.date.end), "%Y%m%d")
        position = position.loc[start_date:end_date]

        if position.empty or self.data.price.empty:
            raise ValueError("Both position and price data are required")

        if not (self.date.start < self.date.end):
            raise ValueError("Start date must be earlier than end date")

        data_config = self.__build_data(position)
        self.frame = self.__build_frame(data_config)
        config = self.__build_config()
        # print(config)
        input_vars = self.__build_input_vars(config, data_config)

        if self.execution.core_type == "basic":
            return BasicBacktestor(config, input_vars)
        elif self.execution.core_type == "id_fund":
            return IDFundBacktestor(config, input_vars)
        elif self.execution.core_type == "vn":
            return VNBacktestor(config, input_vars)
        else:
            raise ValueError(f"Unknown core type: {self.execution.core_type}")

    def __build_input_vars(
        self, config: SimulatorConfig, data_config: DataConfig
    ) -> InputVars:
        weight, price = DataProcessor.preprocess_position(config, data_config)
        volume_capacity = DataProcessor.preprocess_volume_capacity(config, data_config)
        rebalancing_mask = DataProcessor.preprocess_rebalancing_mask(
            config, data_config
        )
        dividend_ratio = DataProcessor.preprocess_dividend_ratio(config, data_config)
        exchange_rate = DataProcessor.preprocess_exchange_rate(config, data_config)

        buy_price = price * (1 + self.cost.slippage)
        sell_price = price * (1 - self.cost.slippage)

        return InputVars(
            weight=weight,
            price=price,
            buy_price=buy_price,
            sell_price=sell_price,
            volume_capacity=volume_capacity,
            rebalancing_mask=rebalancing_mask,
            dividend_ratio=dividend_ratio,
            exchange_rate=exchange_rate,
        )

    def __build_frame(self, data_config: DataConfig) -> FrameConfig:
        return FrameConfig(
            shape=data_config.price.shape,
            common_columns=data_config.position.columns.intersection(
                data_config.price.columns
            ).tolist(),
            common_index=data_config.price.index.tolist(),
        )

    def __build_config(self) -> SimulatorConfig:
        return SimulatorConfig(
            date=self.date,
            cost=self.cost,
            execution=self.execution,
            optional=self.optional,
            cache=self.cache,
            frame=self.frame,
        )

    def __build_data(
        self,
        position: pd.DataFrame,
    ) -> DataConfig:
        def _filter_nonzero_and_common_columns(
            position: pd.DataFrame, price: pd.DataFrame
        ) -> tuple[pd.DataFrame, pd.DataFrame]:
            non_zero_columns = position.columns[position.sum() != 0]
            position = position[non_zero_columns]
            price = price[non_zero_columns]

            common_columns = position.columns.intersection(price.columns)
            if len(common_columns) == 0:
                raise ValueError("No overlapping columns between position and price")

            position = position[common_columns]
            price = price[common_columns]

            return position, price

        def _align_index_with_price(
            position: pd.DataFrame, price: pd.DataFrame
        ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
            start_date = (
                (position.reindex_like(price).shift(-1).notna() * price.notna())
                .any(axis=1)
                .idxmax()
            )

            position = position.loc[start_date:]
            price = price.loc[start_date:]
            position_start_date = position.index.min()

            if price.loc[:position_start_date].empty:
                warnings.warn(
                    "No price data before position start date. "
                    "Position data will be trimmed to match available price data.",
                    UserWarning,
                )
                price_start_date = price.index[0]
            else:
                price_start_date = price.loc[:position_start_date].index[-1]

            common_end_date = min(position.index[-1], price.index[-1])
            price = price.loc[price_start_date:common_end_date]
            position = position.reindex(price.index)

            return position, price, price_start_date

        # Initialize variables
        price = self.data.price
        volume = self.data.volume
        dividend_ratio = self.data.dividend_ratio
        exchange_rate = self.data.exchange_rate

        if not position.empty and not price.empty:
            position, price = _filter_nonzero_and_common_columns(position, price)
            position, price, price_start_date = _align_index_with_price(position, price)

            if not volume.empty:
                volume = volume.loc[price_start_date:]
                volume = volume.reindex(
                    index=position.index, columns=position.columns
                ).loc[: position.index[-1]]

            if not dividend_ratio.empty:
                dividend_ratio = dividend_ratio.loc[price_start_date:]
                dividend_ratio = dividend_ratio.reindex(
                    index=position.index, columns=position.columns
                ).loc[: position.index[-1]]

            if not exchange_rate.empty:
                exchange_rate = exchange_rate.loc[price_start_date:]
                exchange_rate = exchange_rate.reindex(position.index).loc[
                    : position.index[-1]
                ]

        return DataConfig(
            position=position,
            price=price,
            volume=volume,
            dividend_ratio=dividend_ratio,
            exchange_rate=exchange_rate,
        )

    def update_data(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(DataConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for DataConfig: {invalid_params}")

        data_params = {
            slot: kwargs.get(slot, getattr(self.data, slot))
            for slot in slots(DataConfig)
        }

        self.data = DataConfig(**data_params)
        return self

    def update_date(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(DateConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for DateConfig: {invalid_params}")

        date_params = {
            slot: kwargs.get(slot, getattr(self.date, slot))
            for slot in slots(DateConfig)
        }

        self.date = DateConfig(**date_params)
        return self

    def update_cost(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(CostConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for CostConfig: {invalid_params}")

        # Convert basis points to decimal if provided
        for param in ["buy_fee_tax", "sell_fee_tax", "slippage", "dividend_tax"]:
            if param in kwargs:
                kwargs[param] = kwargs[param] / BASIS_POINT_SCALAR

        cost_params = {
            slot: kwargs.get(slot, getattr(self.cost, slot))
            for slot in slots(CostConfig)
        }

        self.cost = CostConfig(**cost_params)
        return self

    def update_execution(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(ExecutionConfig))
        if invalid_params:
            raise ValueError(
                f"Invalid parameters for ExecutionConfig: {invalid_params}"
            )

        execution_params = {
            slot: kwargs.get(slot, getattr(self.execution, slot))
            for slot in slots(ExecutionConfig)
        }

        self.execution = ExecutionConfig(**execution_params)
        return self

    def update_optional(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(OptionalConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for OptionalConfig: {invalid_params}")

        optional_params = {
            slot: kwargs.get(slot, getattr(self.optional, slot))
            for slot in slots(OptionalConfig)
        }

        self.optional = OptionalConfig(**optional_params)
        return self

    def update_cache(self, **kwargs) -> "SimulatorBuilder":
        invalid_params = set(kwargs) - set(slots(CacheConfig))
        if invalid_params:
            raise ValueError(f"Invalid parameters for CacheConfig: {invalid_params}")

        cache_params = {
            slot: kwargs.get(slot, getattr(self.cache, slot))
            for slot in slots(CacheConfig)
        }

        self.cache = CacheConfig(**cache_params)
        return self

    def update(self, **kwargs) -> "SimulatorBuilder":
        """
        Update any configuration options in a single call.
        Uses __slots__ from Config classes to determine which parameters belong where.

        Raises:
            ValueError: If an unknown parameter is provided
        """
        updates = {
            "data": {},
            "date": {},
            "cost": {},
            "execution": {},
            "optional": {},
            "cache": {},
        }

        # Track unknown parameters
        unknown_params = []

        # Sort parameters into their respective config updates
        for key, value in kwargs.items():
            if key in slots(DataConfig):
                updates["data"][key] = value
            elif key in slots(DateConfig):
                updates["date"][key] = value
            elif key in slots(CostConfig):
                updates["cost"][key] = value
            elif key in slots(ExecutionConfig):
                updates["execution"][key] = value
            elif key in slots(OptionalConfig):
                updates["optional"][key] = value
            elif key in slots(CacheConfig):
                updates["cache"][key] = value
            else:
                unknown_params.append(key)

        # Raise error if unknown parameters were provided
        if unknown_params:
            raise ValueError(
                f"Unknown parameter(s): {', '.join(unknown_params)}. "
                "Please check the parameter names and try again."
            )

        # Apply updates only if there are changes
        if updates["data"]:
            self.update_data(**updates["data"])
        if updates["date"]:
            self.update_date(**updates["date"])
        if updates["cost"]:
            self.update_cost(**updates["cost"])
        if updates["execution"]:
            self.update_execution(**updates["execution"])
        if updates["optional"]:
            self.update_optional(**updates["optional"])
        if updates["cache"]:
            self.update_cache(**updates["cache"])

        return self


class DataProcessor:
    def __init__(self):
        pass

    @staticmethod
    def preprocess_position(config: SimulatorConfig, data: DataConfig):
        if config.execution.resample_period:
            position = daily2period(
                data.position,
                config.execution.resample_period,
                keep_index=True,
            )
        else:
            position = data.position

        return (
            (position / POSITION_SCALAR).to_numpy(),
            data.price.to_numpy(),
        )

    @staticmethod
    def preprocess_volume_capacity(config: SimulatorConfig, data: DataConfig):
        if data.volume.empty and config.execution.volume_capacity_ratio != 0:
            raise ValueError("Volume data is required for volume capacity")
        if config.execution.volume_capacity_ratio == 0:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                np.inf,
            )
        else:
            volume = data.volume.reindex(
                config.frame.common_index,
                columns=config.frame.common_columns,
            )
            return volume.fillna(0).to_numpy() * config.execution.volume_capacity_ratio

    @staticmethod
    def preprocess_rebalancing_mask(config: SimulatorConfig, data: DataConfig):
        period = config.execution.rebalancing_method
        if period in ["W", "M", "Q"]:
            return np.array(
                [
                    d in get_rebalancing_mask(data.position, period)  # type: ignore
                    for d in config.frame.common_index
                ],
                dtype=int,
            )
        else:
            return np.array([])

    @staticmethod
    def preprocess_dividend_ratio(config: SimulatorConfig, data: DataConfig):
        if config.execution.drip and data.dividend_ratio.empty:
            raise ValueError("Dividend ratio is required for drip")

        if data.dividend_ratio.empty:
            return np.full(
                (len(config.frame.common_index), len(config.frame.common_columns)),
                0,
            )
        else:
            return data.dividend_ratio.to_numpy()

    @staticmethod
    def preprocess_exchange_rate(config: SimulatorConfig, data: DataConfig):
        if data.exchange_rate.empty:
            return np.array([])
        else:
            return data.exchange_rate.to_numpy()


def slots(cls):
    return [f.name for f in fields(cls)]


if __name__ == "__main__":
    from finter.data import ContentFactory, ModelData

    start, end = 20220101, 20250101
    position = ModelData.load("alpha.krx.krx.stock.ldh0127.div_new_1").loc["2022"]
    price = ContentFactory("kr_stock", start, end).get_df("price_close", fill_nan=False)

    builder = SimulatorBuilder()

    (
        builder.update_data(price=price)
        .update_date(start=20220101, end=20240131)
        .update_cost(buy_fee_tax=10, sell_fee_tax=10, slippage=10)
        .update_execution(initial_cash=1e4, core_type="basic", drip="cash")
        .update_optional(debug=True)
    )

    res = []
    for rebalancing_method in [
        "auto",
        "W",
        "M",
        "Q",
        "by_position",
    ]:
        builder.update_execution(rebalancing_method=rebalancing_method)

        simulator = builder.build(position)
        res.append(simulator.run())
