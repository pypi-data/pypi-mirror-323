"""Interface for querying and controlling loads."""

from decimal import Decimal
from enum import IntEnum

from .base import Interface


class LoadInterface(Interface):
    """Interface for querying and controlling loads."""

    class RampType(IntEnum):
        """Load ramp type."""

        Up = 5
        Down = 4
        Opposite = 3
        Stop = 2
        Fixed = 6
        Variable = 7
        Adjust = 8

    class AlertState(IntEnum):
        """Load alert state."""

        Clear = 0
        Overload = 1
        BulbChange = 2
        WrongType = 3
        DCCurrent = 4
        ShortCircuit = 5

    class DimmingConfig(IntEnum):
        """Load dimming config."""

        Manual = 0
        Forward = 1
        Reverse = 2
        Auto = 3

    method_signatures = {
        "Load.GetLevel": Decimal,
        "Load.GetLevelHW": Decimal,
        "Load.GetProfile": int,
        "Load.GetOverrideLevel": Decimal,
        "Load.GetAlertState": AlertState,
        "Load.GetDimmingConfig": DimmingConfig,
    }

    async def set_level(
        self, vid: int, level: float | Decimal, *, sw: bool = False
    ) -> None:
        """Set the level of a load.

        Args:
            vid: The Vantage ID of the load.
            level: The level to set the load to (0-100).
            sw: Set the cached value instead of the hardware value.
        """
        # INVOKE <id> Load.SetLevel <level (0-100)>
        # -> R:INVOKE <id> <rcode> Load.SetLevel <level (0-100)>
        await self.invoke(vid, "Load.SetLevelSW" if sw else "Load.SetLevel", level)

    async def get_level(self, vid: int, *, hw: bool = False) -> Decimal:
        """Get the level of a load.

        Args:
            vid: The Vantage ID of the load.
            hw: Fetch the value from hardware instead of cache.

        Returns:
            The level of the load, as a percentage (0-100).
        """
        # INVOKE <id> Load.GetLevel
        # -> R:INVOKE <id> <level (0.000-100.000)> Load.GetLevel
        return await self.invoke(vid, "Load.GetLevelHW" if hw else "Load.GetLevel")

    async def ramp(
        self,
        vid: int,
        cmd: RampType,
        ramptime: float | Decimal,
        finallevel: float | Decimal,
    ) -> None:
        """Ramp a load to a level over a number of seconds.

        Args:
            vid: The Vantage ID of the load.
            cmd: The type of ramp to perform.
            ramptime: The number of seconds to ramp the load over.
            finallevel: The level to ramp the load to (0-100).
        """
        # INVOKE <id> Load.Ramp <cmd> <time> <level>
        # -> R:INVOKE <id> <rcode> Load.Ramp <cmd> <time> <level>
        await self.invoke(vid, "Load.Ramp", cmd, ramptime, finallevel)

    async def set_profile(self, vid: int, profile: int) -> None:
        """Set the id of the power profile used by this load.

        Args:
            vid: The Vantage ID of the load.
            profile: The power profile id to set the load to.
        """
        # INVOKE <id> Load.SetProfile <profile>
        # -> R:INVOKE <id> <rcode> Load.SetProfile <profile>
        await self.invoke(vid, "Load.SetProfile", profile)

    async def get_profile(self, vid: int) -> int:
        """Get the id of the power profile used by this load.

        Args:
            vid: The Vantage ID of the load.

        Returns:
            The power profile id used by the load.
        """
        # INVOKE <id> Load.GetProfile
        # -> R:INVOKE <id> <profile> Load.GetProfile
        return await self.invoke(vid, "Load.GetProfile")

    async def get_override_level(self, vid: int) -> Decimal:
        """Get the override level of a load.

        Args:
            vid: The Vantage ID of the load.

        Returns:
            The override level of the load, as a percentage (0-100).
        """
        # INVOKE <id> Load.GetOverrideLevel
        # -> R:INVOKE <id> <level (0.000-100.000)> Load.GetOverrideLevel
        return await self.invoke(vid, "Load.GetOverrideLevel")

    async def ramp_auto_off(
        self,
        vid: int,
        cmd: RampType,
        ramptime: float | Decimal,
        finallevel: float | Decimal,
        offcmd: RampType,
        offramptime: float | Decimal,
        offtimeout: float | Decimal,
    ) -> None:
        """Ramp a load to a level over a number of seconds, then ramp off after a timeout.

        Args:
            vid: The Vantage ID of the load.
            cmd: The type of ramp to perform.
            ramptime: The number of seconds to ramp the load over.
            finallevel: The level to ramp the load to (0-100).
            offcmd: The type of ramp to perform to turn the load off.
            offramptime: The number of seconds to ramp the load off over.
            offtimeout: The number of seconds to wait before turning the load off.
        """
        # INVOKE <id> Load.RampAutoOff <cmd> <time> <level> <offcmd> <offtime> <offlevel>
        # -> R:INVOKE <id> <rcode> Load.RampAutoOff <cmd> <time> <level> <offcmd> <offtime> <offlevel>
        await self.invoke(
            vid,
            "Load.RampAutoOff",
            cmd,
            ramptime,
            finallevel,
            offcmd,
            offramptime,
            offtimeout,
        )

    async def get_alert_state(self, vid: int) -> AlertState:
        """Get the alert state of a load.

        Args:
            vid: The Vantage ID of the load.

        Returns:
            The alert state of the load.
        """
        # INVOKE <id> Load.GetAlertState
        # -> R:INVOKE <id> <alert state> Load.GetAlertState
        return await self.invoke(vid, "Load.GetAlertState")

    async def set_alert_state(self, vid: int, alert_state: AlertState) -> None:
        """Set the cached alert state of a load.

        Args:
            vid: The Vantage ID of the load.
            alert_state: The alert state to set the load to.
        """
        # INVOKE <id> Load.SetAlertStateSW <alert state>
        # -> R:INVOKE <id> <rcode> Load.SetAlertStateSW <alert state>
        await self.invoke(vid, "Load.SetAlertStateSW", alert_state)

    async def get_dimming_config(self, vid: int) -> DimmingConfig:
        """Get the dimming configuration of a load.

        Args:
            vid: The Vantage ID of the load.

        Returns:
            The dimming configuration of the load.
        """
        # INVOKE <id> Load.GetDimmingConfig
        # -> R:INVOKE <id> <dimming config> Load.GetDimmingConfig
        return await self.invoke(vid, "Load.GetDimmingConfig")

    # Convenience functions, not part of the interface
    async def turn_on(
        self, vid: int, transition: float | None = None, level: float | None = None
    ) -> None:
        """Turn on a load with an optional transition time.

        Args:
            vid: The Vantage ID of the load.
            transition: The time in seconds to transition to the new level, defaults to immediate.
            level: The level to set the load to (0-100), defaults to 100.
        """
        if level is None:
            level = 100

        if transition is None:
            return await self.set_level(vid, level)

        await self.ramp(vid, self.RampType.Fixed, transition, level)

    async def turn_off(self, vid: int, transition: float | None = None) -> None:
        """Turn off a load with an optional transition time.

        Args:
            vid: The Vantage ID of the load.
            transition: The time in seconds to ramp the load down, defaults to immediate.
        """
        if transition is None:
            return await self.set_level(vid, 0)

        await self.ramp(vid, self.RampType.Fixed, transition, 0)
