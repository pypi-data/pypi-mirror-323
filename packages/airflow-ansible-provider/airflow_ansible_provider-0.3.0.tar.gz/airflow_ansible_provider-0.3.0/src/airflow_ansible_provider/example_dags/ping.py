#!/bin/env python3
"""
ansible linux ping workflow example
"""
from datetime import datetime

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow_ansible_provider.decorators.ansible_decorators import ansible_task


@task(task_id="gen_inventory")
def gen_inventory():
    context = get_current_context()
    param = context["dag_run"].conf
    return {
        "default": {
            "hosts": {
                "test": {
                    "ansible_host": param["ip"],
                    "ansible_ssh_host": param["ip"],
                }
            },
        }
    }


@ansible_task(
    task_id="ping",
    playbook="ping.yml",
    get_ci_events=True,
)
def ping(inventory):  # pylint: disable=unused-argument
    """Collect ansible run results"""
    return get_current_context().get("ansible_return", {})


@dag(
    dag_id="ping",
    start_date=datetime(2023, 8, 1),
    schedule=None,
    catchup=False,
    tags=["ansible", "Linux", "ping"],
    params={
        "ip": Param(
            default="",
            type="string",
            description="server ip",
            title="Server IP",
        ),
    },
)
def main():
    """linux ping workflow"""
    inventory = gen_inventory()
    ping(inventory=inventory)


main()
