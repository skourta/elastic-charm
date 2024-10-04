#!/usr/bin/env python3
# Copyright 2024 Ubuntu
# See LICENSE file for licensing details.

"""Charm the application."""

import logging
import subprocess

import ops

logger = logging.getLogger(__name__)


class AllocationIdFailedError(Exception):
    """Allocation ID not found error."""


class AssociatingElasticIpError(Exception):
    """Associating Elastic IP error."""


class GettingInstanceIdError(Exception):
    """Getting Instance ID error."""


class ElasticCharmCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.start, self._on_start)
        framework.observe(self.on.config_changed, self._on_config_changed)
        framework.observe(self.on.install, self._on_install)

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        # get the instance id
        try:
            instance_id = self._get_instance_id()
        except GettingInstanceIdError as e:
            logger.error(f"Failed to get instance id: {e}")
            self.unit.status = ops.BlockedStatus("Failed to get instance id")
            return

        logger.info(f"Instance ID: {instance_id}")
        self.unit.status = ops.ActiveStatus()

    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        """Handle config changed event."""
        logger.info("Config changed")

        # if leader
        if not self.unit.is_leader():
            return

        if "elastic-ip" in self.config:
            elastic_ip: str = str(self.config["elastic-ip"])
            # associate elastic ip
            self.unit.status = ops.MaintenanceStatus("Associating Elastic IP")
            # get the allocation id of the elastic ip
            try:
                self._associate_elastic_ip(elastic_ip)
            except (
                GettingInstanceIdError,
                AllocationIdFailedError,
                AssociatingElasticIpError,
            ) as e:
                logger.error(f"Failed to associate elastic ip: {e}")
                self.unit.status = ops.BlockedStatus("Failed to associate elastic ip")
                event.defer()
                return

            self.unit.status = ops.ActiveStatus()
            logger.info("Elastic IP associated")

    def _on_install(self, event: ops.InstallEvent):
        """Handle install event."""
        logger.info("Install event")
        # install aws cli snap
        self.unit.status = ops.MaintenanceStatus("Installing AWS CLI")
        try:
            subprocess.check_output(["snap", "install", "aws-cli", "--classic"])
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install aws cli: {e}")
            self.unit.status = ops.BlockedStatus("Failed to install aws cli")
            return
        self.unit.status = ops.ActiveStatus()
        logger.info("AWS CLI installed")

    def _get_instance_id(self) -> str:
        try:
            return (
                subprocess.check_output(["ec2metadata", "--instance-id"])
                .decode()
                .strip()
            )
        except subprocess.CalledProcessError as e:
            raise GettingInstanceIdError(f"Failed to get instance id: {e}")

    def _get_allocation_id(self, elastic_ip: str) -> str:
        """Get the allocation id of the elastic ip."""
        try:
            output = subprocess.check_output(
                [
                    "aws",
                    "ec2",
                    "describe-addresses",
                    "--public-ips",
                    elastic_ip,
                    "--query",
                    "Addresses[0].AllocationId",
                    "--output",
                    "text",
                ]
            )
            return output.decode().strip()
        except subprocess.CalledProcessError as e:
            raise AllocationIdFailedError(f"Failed to get allocation id: {e}")

    def _associate_elastic_ip(self, public_ip: str) -> None:
        """Associate the elastic ip with the instance."""
        breakpoint()
        instance_id = self._get_instance_id()
        allocation_id = self._get_allocation_id(public_ip)

        try:
            subprocess.check_output(
                [
                    "aws",
                    "ec2",
                    "associate-address",
                    "--instance-id",
                    instance_id,
                    "--allocation-id",
                    allocation_id,
                ]
            )
        except subprocess.CalledProcessError as e:
            raise AssociatingElasticIpError(f"Failed to associate elastic ip: {e}")


if __name__ == "__main__":  # pragma: nocover
    ops.main(ElasticCharmCharm)  # type: ignore
