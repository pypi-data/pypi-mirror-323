"""Total Connect Location."""

import logging
from typing import Dict, Any

from .const import PROJECT_URL, ArmingState, ArmType, _ResultCode
from .device import TotalConnectDevice
from .exceptions import (
    FeatureNotSupportedError,
    PartialResponseError,
    TotalConnectError,
)
from .partition import TotalConnectPartition
from .zone import TotalConnectZone, ZoneStatus

DEFAULT_USERCODE = "-1"

LOGGER = logging.getLogger(__name__)


class TotalConnectLocation:
    """TotalConnectLocation class."""

    def __init__(self, location_info_basic: Dict[str, Any], parent) -> None:
        """Initialize based on a 'LocationInfoBasic'."""
        self.location_id = location_info_basic["LocationID"]
        self.location_name: str = location_info_basic["LocationName"]
        self._photo_url: str = location_info_basic["PhotoURL"]
        self._module_flags = dict(
            x.split("=") for x in location_info_basic["LocationModuleFlags"].split(",")
        )
        self.security_device_id: str = location_info_basic["SecurityDeviceID"]
        self.parent = parent
        self.ac_loss = None
        self.low_battery = None
        self.cover_tampered = None
        self.last_updated_timestamp_ticks = None
        self.configuration_sequence_number = None
        self.arming_state: ArmingState = ArmingState.UNKNOWN
        self.partitions: Dict[Any, TotalConnectPartition] = {}
        self._partition_list: Dict[str, list[Any]] = {"int": []}
        self.zones: Dict[Any, TotalConnectZone] = {}
        self.usercode: str = DEFAULT_USERCODE
        self.auto_bypass_low_battery: bool = False
        self._sync_job_id = None
        self._sync_job_state: int = 0

        dib = (location_info_basic.get("DeviceList") or {}).get("DeviceInfoBasic")
        tcdevs = [TotalConnectDevice(d) for d in (dib or {})]
        self.devices = {tcdev.deviceid: tcdev for tcdev in tcdevs}

    def __str__(self) -> str:
        """Return a text string that is printable."""
        data = (
            f"LOCATION {self.location_id} - {self.location_name}\n\n"
            f"PhotoURL: {self._photo_url}\n"
            f"SecurityDeviceID: {self.security_device_id}\n"
            f"AcLoss: {self.ac_loss}\n"
            f"LowBattery: {self.low_battery}\n"
            f"IsCoverTampered: {self.cover_tampered}\n"
            f"{self.arming_state}\n"
            f"LocationModuleFlags:\n"
        )

        for key, value in self._module_flags.items():
            data = data + f"  {key}: {value}\n"

        data = data + "\n"

        devices = f"DEVICES: {len(self.devices)}\n\n"
        for device in self.devices:
            devices = devices + str(self.devices[device]) + "\n"

        partitions = f"PARTITIONS: {len(self.partitions)}\n\n"
        for status in self.partitions.values():
            partitions += str(status) + "\n"

        zones = f"ZONES: {len(self.zones)}\n\n"
        for status in self.zones.values():
            zones += str(status)

        return data + devices + partitions + zones

    def get_panel_meta_data(self) -> None:
        """Get all meta data about the alarm panel."""
        # see https://rs.alarmnet.com/TC21api/tc2.asmx?op=GetPanelMetaDataAndFullStatus
        result = self.parent.request(
            "GetPanelMetaDataAndFullStatusEx_V2",
            (
                # to speed this up we could replace the first zero with
                # the most recent ConfigurationSequenceNumber and the
                # second with LastUpdatedTimestampTicks
                self.parent.token,
                self.location_id,
                0,
                0,
                self._partition_list,
            ),
        )
        self.parent.raise_for_resultcode(result)

        self._update_status(result)
        self._update_partitions(result)
        self._update_zones(result)

    def get_zone_details(self) -> None:
        """Get Zone details."""
        result = self.parent.request(
            "GetZonesListInStateEx_V1",
            (
                # 0 is the ListIdentifierID, whatever that might be
                self.parent.token,
                self.location_id,
                self._partition_list,
                0,
            ),
        )

        try:
            self.parent.raise_for_resultcode(result)
            self._update_zone_details(result)
        except FeatureNotSupportedError:
            LOGGER.warning(
                "getting Zone Details is a feature not supported by "
                "your Total Connect account or hardware"
            )

    def get_partition_details(self) -> None:
        """Get partition details for this location."""
        # see https://rs.alarmnet.com/TC21api/tc2.asmx?op=GetPartitionsDetails

        result = self.parent.request(
            "GetPartitionsDetails",
            (self.parent.token, self.location_id, self.security_device_id),
        )
        try:
            self.parent.raise_for_resultcode(result)
        except TotalConnectError:
            LOGGER.error(
                f"Could not get partition details for "
                f"device {self.security_device_id} at "
                f"location {self.location_id}."
                f"ResultCode: {result['ResultCode']}. "
                f"ResultData: {result['ResultData']}"
            )
            raise

        partition_details = ((result or {}).get("PartitionsInfoList") or {}).get(
            "PartitionDetails"
        )
        if not partition_details:
            raise PartialResponseError("no PartitionDetails", result)

        new_partition_list = []
        for partition in partition_details:
            new_partition = TotalConnectPartition(partition, self)
            self.partitions[new_partition.partitionid] = new_partition
            new_partition_list.append(new_partition.partitionid)

        self._partition_list = {"int": new_partition_list}

    def is_low_battery(self) -> bool:
        """Return true if low battery."""
        return self.low_battery is True

    def is_ac_loss(self) -> bool:
        """Return true if AC loss."""
        return self.ac_loss is True

    def is_cover_tampered(self) -> bool:
        """Return true if cover is tampered."""
        return self.cover_tampered is True

    def set_usercode(self, usercode: str) -> bool:
        """Set the usercode. Return true if successful."""
        if self.parent.validate_usercode(self.security_device_id, usercode):
            self.usercode = usercode
            return True
        return False

    def _build_partition_list(self, partition_id:str="") -> Dict[str, list[Any]]:
        """Build a list of partitions to use for arming/disarming."""
        if not partition_id:
            return self._partition_list

        if partition_id not in self.partitions:
            raise TotalConnectError(
                f"Partition {partition_id} does not exist "
                f"at location {self.location_id}"
            )
        return {"int": [partition_id]}

    def arm(self, arm_type: ArmType, partition_id:str="", usercode: str = "") -> None:
        """Arm the given partition.

        If no partition is given, arm all partitions.
        If no usercode given, use stored value."""
        # see https://rs.alarmnet.com/TC21api/tc2.asmx?op=ArmSecuritySystemPartitionsV1
        assert isinstance(arm_type, ArmType)
        partition_list = self._build_partition_list(partition_id)
        usercode = usercode or self.usercode

        result = self.parent.request(
            "ArmSecuritySystemPartitionsV1",
            (
                self.parent.token,
                self.location_id,
                self.security_device_id,
                arm_type.value,
                usercode,
                partition_list,
            ),
        )
        if _ResultCode.from_response(result) == _ResultCode.COMMAND_FAILED:
            LOGGER.warning("could not arm system; is a zone faulted?")
        self.parent.raise_for_resultcode(result)
        LOGGER.info(
            f"ARMED({arm_type}) partitions {partition_list} at {self.location_id}"
        )

    def disarm(self, partition_id:str="", usercode: str = "") -> None:
        """Disarm the system."""
        # if no partition is given, disarm all partitions
        # see https://rs.alarmnet.com/TC21api/tc2.asmx?op=ArmSecuritySystemPartitionsV1
        partition_list = self._build_partition_list(partition_id)
        usercode = usercode or self.usercode

        result = self.parent.request(
            "DisarmSecuritySystemPartitionsV1",
            (
                self.parent.token,
                self.location_id,
                self.security_device_id,
                usercode,
                partition_list,
            ),
        )
        self.parent.raise_for_resultcode(result)
        LOGGER.info(f"DISARMED partitions {partition_list} at {self.location_id}")

    def zone_bypass(self, zone_id: int) -> None:
        """Bypass a zone."""
        result = self.parent.request(
            "Bypass",
            (
                self.parent.token,
                self.location_id,
                self.security_device_id,
                zone_id,
                self.usercode,
            ),
        )
        self.parent.raise_for_resultcode(result)
        LOGGER.info(f"BYPASSED {zone_id} at {self.location_id}")
        self.zones[zone_id]._mark_as_bypassed()

    def zone_bypass_all(self) -> None:
        """Bypass all faulted zones."""
        faulted_zones = []
        for zone_id, zone in self.zones.items():
            if zone.is_faulted():
                faulted_zones.append(zone_id)

        if faulted_zones:
            zone_list = {"int": faulted_zones}

            result = self.parent.request(
                "BypassAll",
                (
                    self.parent.token,
                    self.location_id,
                    self.security_device_id,
                    zone_list,
                    self.usercode,
                ),
            )
            self.parent.raise_for_resultcode(result)
            LOGGER.info(f"BYPASSED all zones at location {self.location_id}")

    def clear_bypass(self) -> None:
        """Clear all bypassed zones."""
        self.disarm()

    def zone_status(self, zone_id: int) -> ZoneStatus:
        """Get status of a zone."""
        zone = self.zones.get(zone_id)
        if not zone:
            raise TotalConnectError(f"zone {zone_id} does not exist")
        return zone.status

    def arm_custom(self, arm_type: ArmType) -> Dict[str, Any]:
        """NOT OPERATIONAL YET.
        Arm custom the system.  Return true if successful.
        """
        zones_list = {}
        zones_list[0] = {"ZoneID": "12", "ByPass": False, "ZoneStatus": 0}
        settings = {"ArmMode": "1", "ArmDelay": "5", "ZonesList": zones_list}

        result = self.parent.request(
            "CustomArmSecuritySystem",
            (
                self.parent.token,
                self.location_id,
                self.security_device_id,
                arm_type.value,
                self.usercode,
                settings,
            ),
        )
        self.parent.raise_for_resultcode(result)
        # TODO: returning the raw result is not right
        return result

    def get_custom_arm_settings(self) -> Dict[str, Any]:
        """NOT OPERATIONAL YET.
        Get custom arm settings.
        """
        result = self.parent.request(
            "GetCustomArmSettings",
            (self.parent.token, self.location_id, self.security_device_id),
        )
        self.parent.raise_for_resultcode(result)
        # TODO: returning the raw result is not right
        return result

    def _update_zone_details(self, result: Dict[str, Any]) -> None:
        """
        Update from GetZonesListInStateEx_V1.

        ZoneStatusInfoWithPartitionId provides additional info for setting up zones.
        If we used TotalConnectZone._update() it would overwrite missing data with None.
        """
        zone_info = ((result.get("ZoneStatus") or {}).get("Zones") or {}).get(
            "ZoneStatusInfoWithPartitionId"
        )
        if not zone_info:
            LOGGER.warning(
                "No zones found when starting TotalConnect. Try to sync your panel using the TotalConnect app or website."
            )
            LOGGER.debug(f"_update_zone_details result: {result}")
        else:
            for zonedata in zone_info:
                self.zones[zonedata["ZoneID"]] = TotalConnectZone(zonedata, self)

    def _update_status(self, result: Dict[str, Any]) -> None:
        """Update from result."""
        data = (result or {}).get("PanelMetadataAndStatus")
        if not data:
            raise PartialResponseError("no PanelMetadataAndStatus", result)

        self.ac_loss = data.get("IsInACLoss")
        self.low_battery = data.get("IsInLowBattery")
        self.cover_tampered = data.get("IsCoverTampered")
        self.last_updated_timestamp_ticks = data.get("LastUpdatedTimestampTicks")
        self.configuration_sequence_number = data.get("ConfigurationSequenceNumber")

        astate = result.get("ArmingState")
        if not astate:
            raise PartialResponseError("no ArmingState", result)
        try:
            self.arming_state = ArmingState(astate)
        except ValueError:
            LOGGER.error(
                f"unknown location ArmingState {astate} in {result}: please report at {PROJECT_URL}/issues"
            )
            raise TotalConnectError(
                f"unknown location ArmingState {astate} in {result}"
            ) from None

    def _update_partitions(self, result: Dict[str, Any]) -> None:
        """Update partition info from Partitions."""
        pinfo = (
            (result.get("PanelMetadataAndStatus") or {}).get("Partitions") or {}
        ).get("PartitionInfo")
        if not pinfo:
            raise PartialResponseError("no PartitionInfo", result)

        # loop through partitions and update
        # NOTE: do not use keys because they don't line up with PartitionID
        for partition in pinfo:
            if "PartitionID" not in partition:
                raise PartialResponseError("no PartitionID", result)
            partition_id = str(partition["PartitionID"])
            if partition_id in self.partitions:
                self.partitions[partition_id]._update(partition)
            else:
                LOGGER.warning(f"Update provided for unknown partion {partition_id}")

    def _update_zones(self, result: Dict[str, Any]) -> None:
        """Update zone info from ZoneInfo or ZoneInfoEx."""

        data = (result.get("PanelMetadataAndStatus") or {}).get("Zones")
        if not data:
            LOGGER.error(
                "no zones found: sync your panel using TotalConnect app or website"
            )
            # PartialResponseError would mean this is retryable without fixing
            # anything, and this needs fixing
            raise TotalConnectError("no zones found: panel sync required")

        zone_info = data.get("ZoneInfoEx") or data.get("ZoneInfo")
        if not zone_info:
            raise PartialResponseError("no ZoneInfoEx or ZoneInfo", result)
        for zonedata in zone_info:
            zid = (zonedata or {}).get("ZoneID")
            if not zid:
                raise PartialResponseError("no ZoneID", result)
            zone = self.zones.get(zid)
            if zone:
                zone._update(zonedata)
            else:
                zone = TotalConnectZone(zonedata, self)
                self.zones[zid] = zone

            if (
                zone.is_low_battery()
                and zone.can_be_bypassed
                and self.auto_bypass_low_battery
            ):
                self.zone_bypass(zid)

    def sync_panel(self) -> None:
        """Syncronize the panel with the TotalConnect server."""
        result = self.parent.request(
            "SynchronizeSecurityPanel",
            (self.parent.token, None, self.usercode, self.location_id, False),
        )
        self.parent.raise_for_resultcode(result)
        self._sync_job_id = result.get("JobID")
        # Successful request so assume state is in progress
        self._sync_job_state = 1
        LOGGER.info(f"Started sync of panel for location {self.location_id}")

    def get_sync_status(self) -> None:
        """Get panel sync status from the TotalConnect server."""
        result = self.parent.request(
            "GetSyncJobStatus", (self.parent.token, self._sync_job_id, self.location_id)
        )

        try:
            self.parent.raise_for_resultcode(result)
            job_state = result.get("JobState")
            if job_state == 1:
                LOGGER.info(f"Panel sync for location {self.location_id} in progress")
            elif job_state == 2:
                LOGGER.info(f"Panel sync for location {self.location_id} complete")
            else:
                LOGGER.warning(
                    f"Unknown panel sync status for location {self.location_id}"
                )
        except TotalConnectError:
            LOGGER.error(
                f"Could not get status of Sync Job with ID {self._sync_job_id}"
            )

    def get_cameras(self) -> None:
        """Get cameras for the location."""
        result = self.parent.request(
            "GetLocationAllCameraListEx", (self.parent.token, self.location_id)
        )
        self.parent.raise_for_resultcode(result)

        if "AccountAllCameraList" not in result:
            LOGGER.info(f"No cameras found for location {self.location_id}")
            return

        camera_list = result["AccountAllCameraList"]

        if "WiFiDoorbellList" in camera_list:
            self._get_doorbell(camera_list["WiFiDoorbellList"])

        if "UnicornList" in camera_list:
            self._get_unicorn(camera_list["UnicornList"])

    def _get_doorbell(self, data: Dict[str, Any]) -> None:
        """Find doorbell info."""
        if not data or "WiFiDoorbellsList" not in data:
            return

        doorbells = data["WiFiDoorbellsList"]
        if "WiFiDoorBellInfo" not in doorbells:
            return

        doorbell_list = doorbells["WiFiDoorBellInfo"]
        for doorbell in doorbell_list:
            id = doorbell["DeviceID"]
            if id in self.devices:
                self.devices[id].doorbell_info = doorbell

    def _get_unicorn(self, data: Dict[str, Any]) -> None:
        """Find uniforn info."""
        if not data or "UnicornList" not in data:
            return

        unicorns = data["UnicornsList"]
        if "UnicornInfo" not in unicorns:
            return

        unicorn_list = unicorns["UnicornInfo"]
        for unicorn in unicorn_list:
            id = unicorn["DeviceID"]
            if id in self.devices:
                self.devices[id].unicorn_info = unicorn

    def get_video(self) -> None:
        """Get video for the location."""
        result = self.parent.request(
            "GetVideoPIRLocationDeviceList", (self.parent.token, self.location_id)
        )
        self.parent.raise_for_resultcode(result)

        if "VideoPIRList" not in result:
            return

        if "VideoPIRInfo" not in result["VideoPIRList"]:
            return

        video_list = result["VideoPIRList"]["VideoPIRInfo"]
        for video in video_list:
            id = video["DeviceID"]
            if id in self.devices:
                self.devices[id].video_info = video
