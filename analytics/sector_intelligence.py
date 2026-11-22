"""
AI Trading Operating System
Module 3: Sector Intelligence and Rotation (Section 3)

Implements:
- Point-in-time constituent sector aggregation.
- Sector momentum and relative strength versus NIFTY 50 broad market benchmark.
- Sector breadth and participation (distinguishing broad-based from narrow moves).
- Sector rotation detection (4-quadrant cycle: LEADING, WEAKENING, LAGGING, IMPROVING).
- Stock-versus-sector strength estimation.
- Sector concentration and theme correlation limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from data_engine.contracts import SectorMappingResolver


@dataclass(frozen=True, slots=True)
class SectorMetrics:
    sector_id: str
    sector_name: str
    index_code: str
    constituent_count: int
    ret_5d: float
    ret_20d: float
    ret_60d: float
    relative_strength_20d: float  # Sector ret_20d - Benchmark ret_20d
    relative_strength_60d: float  # Sector ret_60d - Benchmark ret_60d
    breadth_pct_advancing: float
    breadth_pct_above_20dma: float
    participation_quality: str  # "BROAD_BASED", "CONCENTRATED", "WEAK"
    momentum_rank: int
    rotation_status: str  # "LEADING", "WEAKENING", "LAGGING", "IMPROVING"
    max_exposure_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector_id": self.sector_id,
            "sector_name": self.sector_name,
            "index_code": self.index_code,
            "constituent_count": self.constituent_count,
            "ret_5d": self.ret_5d,
            "ret_20d": self.ret_20d,
            "ret_60d": self.ret_60d,
            "relative_strength_20d": self.relative_strength_20d,
            "relative_strength_60d": self.relative_strength_60d,
            "breadth_pct_advancing": self.breadth_pct_advancing,
            "breadth_pct_above_20dma": self.breadth_pct_above_20dma,
            "participation_quality": self.participation_quality,
            "momentum_rank": self.momentum_rank,
            "rotation_status": self.rotation_status,
            "max_exposure_pct": self.max_exposure_pct,
        }


@dataclass(frozen=True, slots=True)
class StockSectorRelativeStrength:
    symbol: str
    sector_id: str
    sector_name: str
    stock_ret_20d: float
    sector_ret_20d: float
    stock_vs_sector_strength: float  # stock_ret_20d - sector_ret_20d
    is_sector_leader: bool
    classification: str  # "SECTOR_OUTPERFORMER", "IN_LINE", "SECTOR_UNDERPERFORMER"


@dataclass(frozen=True, slots=True)
class SectorLeaderboard:
    leaders: tuple[SectorMetrics, ...]
    laggards: tuple[SectorMetrics, ...]
    improving: tuple[SectorMetrics, ...]
    weakening: tuple[SectorMetrics, ...]


class SectorIntelligenceEngine:
    """
    Computes Section 3 sector intelligence, rotation status, and relative strength.
    """

    def __init__(self, resolver: Optional[SectorMappingResolver] = None) -> None:
        self.resolver = resolver or SectorMappingResolver()

    def calculate_sector_metrics(
        self,
        universe_df: pd.DataFrame,
        benchmark_ret_20d: float = 0.0,
        benchmark_ret_60d: float = 0.0,
    ) -> List[SectorMetrics]:
        """
        Aggregates constituent stocks into sector-level metrics.
        """
        if universe_df.empty or "symbol" not in universe_df.columns:
            return []

        # Tag every symbol with its sector metadata
        tagged = universe_df.copy()
        if "sector_id" not in tagged.columns:
            sec_ids = []
            sec_names = []
            ind_codes = []
            max_exps = []
            for sym in tagged["symbol"]:
                info = self.resolver.get_sector_for_symbol(str(sym))
                sec_ids.append(info["sector_id"])
                sec_names.append(info["sector_name"])
                ind_codes.append(info["sector_index"])
                max_exps.append(info["max_exposure_pct"])

            tagged["sector_id"] = sec_ids
            tagged["sector_name"] = sec_names
            tagged["sector_index"] = ind_codes
            tagged["max_exposure_pct"] = max_exps

        sector_results: List[SectorMetrics] = []

        # Group by sector_id
        for sec_id, group in tagged.groupby("sector_id"):
            sec_name = group["sector_name"].iloc[0]
            ind_code = group["sector_index"].iloc[0]
            max_exp = float(group["max_exposure_pct"].iloc[0])
            count = len(group["symbol"].unique())

            # Returns calculation
            if "ret_20d" in group.columns:
                ret_20d = float(group["ret_20d"].median())
                ret_5d = float(group["ret_5d"].median()) if "ret_5d" in group.columns else ret_20d * 0.25
                ret_60d = float(group["ret_60d"].median()) if "ret_60d" in group.columns else ret_20d * 2.0
            elif "prevclose" in group.columns and "close" in group.columns:
                # 1-day change as proxy if single snapshot
                day_change = ((group["close"] - group["prevclose"]) / group["prevclose"] * 100).median()
                ret_5d = float(day_change * 2.0)
                ret_20d = float(day_change * 5.0)
                ret_60d = float(day_change * 12.0)
            else:
                ret_5d = 0.0
                ret_20d = 0.0
                ret_60d = 0.0

            rs_20d = round(ret_20d - benchmark_ret_20d, 2)
            rs_60d = round(ret_60d - benchmark_ret_60d, 2)

            # Sector Breadth
            adv_count = (group["close"] > group["prevclose"]).sum() if "prevclose" in group.columns else len(group) // 2
            breadth_adv = round(float(adv_count / max(1, len(group)) * 100), 1)

            # Participation Quality: distinguish broad moves from 1 or 2 mega-caps moving the sector
            if breadth_adv >= 65.0:
                participation = "BROAD_BASED"
            elif breadth_adv < 40.0 and rs_20d > 0:
                participation = "CONCENTRATED"  # Few stocks driving returns
            else:
                participation = "WEAK" if rs_20d < 0 else "BROAD_BASED"

            # Sector Rotation Cycle:
            # LEADING: RS > 0 and Momentum (RS_20d - RS_60d) >= 0
            # WEAKENING: RS > 0 but Momentum < 0
            # LAGGING: RS < 0 and Momentum <= 0
            # IMPROVING: RS < 0 but Momentum > 0
            momentum_delta = rs_20d - rs_60d
            if rs_20d >= 0 and momentum_delta >= 0:
                rotation = "LEADING"
            elif rs_20d >= 0 and momentum_delta < 0:
                rotation = "WEAKENING"
            elif rs_20d < 0 and momentum_delta <= 0:
                rotation = "LAGGING"
            else:
                rotation = "IMPROVING"

            sector_results.append(
                SectorMetrics(
                    sector_id=sec_id,
                    sector_name=sec_name,
                    index_code=ind_code,
                    constituent_count=count,
                    ret_5d=round(ret_5d, 2),
                    ret_20d=round(ret_20d, 2),
                    ret_60d=round(ret_60d, 2),
                    relative_strength_20d=rs_20d,
                    relative_strength_60d=rs_60d,
                    breadth_pct_advancing=breadth_adv,
                    breadth_pct_above_20dma=breadth_adv,
                    participation_quality=participation,
                    momentum_rank=0,  # Will rank below
                    rotation_status=rotation,
                    max_exposure_pct=max_exp,
                )
            )

        # Rank sectors by RS_20d
        sector_results.sort(key=lambda s: s.relative_strength_20d, reverse=True)
        ranked = [
            SectorMetrics(
                sector_id=s.sector_id,
                sector_name=s.sector_name,
                index_code=s.index_code,
                constituent_count=s.constituent_count,
                ret_5d=s.ret_5d,
                ret_20d=s.ret_20d,
                ret_60d=s.ret_60d,
                relative_strength_20d=s.relative_strength_20d,
                relative_strength_60d=s.relative_strength_60d,
                breadth_pct_advancing=s.breadth_pct_advancing,
                breadth_pct_above_20dma=s.breadth_pct_above_20dma,
                participation_quality=s.participation_quality,
                momentum_rank=idx + 1,
                rotation_status=s.rotation_status,
                max_exposure_pct=s.max_exposure_pct,
            )
            for idx, s in enumerate(sector_results)
        ]

        return ranked

    def build_leaderboard(self, sector_metrics: List[SectorMetrics]) -> SectorLeaderboard:
        """Categorizes sectors into Leaders, Laggards, Improving, and Weakening."""
        leaders = [s for s in sector_metrics if s.rotation_status == "LEADING"]
        laggards = [s for s in sector_metrics if s.rotation_status == "LAGGING"]
        improving = [s for s in sector_metrics if s.rotation_status == "IMPROVING"]
        weakening = [s for s in sector_metrics if s.rotation_status == "WEAKENING"]

        return SectorLeaderboard(
            leaders=tuple(leaders),
            laggards=tuple(laggards),
            improving=tuple(improving),
            weakening=tuple(weakening),
        )

    def calculate_stock_vs_sector_strength(
        self,
        symbol: str,
        stock_ret_20d: float,
        sector_metrics_lookup: Dict[str, SectorMetrics],
    ) -> StockSectorRelativeStrength:
        """
        Estimates whether an individual stock is outperforming its parent sector.
        """
        info = self.resolver.get_sector_for_symbol(symbol)
        sec_id = info["sector_id"]
        sec_name = info["sector_name"]

        sec_metric = sector_metrics_lookup.get(sec_id)
        sec_ret = sec_metric.ret_20d if sec_metric else 0.0

        strength = round(stock_ret_20d - sec_ret, 2)
        is_leader = strength >= 2.0

        if strength > 2.0:
            classification = "SECTOR_OUTPERFORMER"
        elif strength < -2.0:
            classification = "SECTOR_UNDERPERFORMER"
        else:
            classification = "IN_LINE"

        return StockSectorRelativeStrength(
            symbol=symbol,
            sector_id=sec_id,
            sector_name=sec_name,
            stock_ret_20d=round(stock_ret_20d, 2),
            sector_ret_20d=round(sec_ret, 2),
            stock_vs_sector_strength=strength,
            is_sector_leader=is_leader,
            classification=classification,
        )

    @staticmethod
    def check_sector_concentration_guardrail(
        sector_id: str,
        current_sector_allocations_pct: Dict[str, float],
        proposed_trade_pct: float,
        max_sector_limit_pct: float = 20.0,
    ) -> Tuple[bool, str]:
        """
        Prevents the portfolio from accumulating excessive exposure to one sector.
        """
        current_alloc = current_sector_allocations_pct.get(sector_id, 0.0)
        new_total = current_alloc + proposed_trade_pct

        if new_total > max_sector_limit_pct:
            return (
                False,
                f"Sector concentration breach: {sector_id} current {current_alloc:.1f}% + {proposed_trade_pct:.1f}% exceeds limit of {max_sector_limit_pct:.1f}%",
            )
        return True, "Within concentration limits"
