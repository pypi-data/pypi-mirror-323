import logging
from typing import Annotated

import typer
from dotenv import load_dotenv
from metagame import TradingClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.command()
def main(
    jwt: Annotated[str, typer.Option(envvar="JWT")],
    api_url: Annotated[str, typer.Option(envvar="API_URL")],
    act_as: Annotated[int, typer.Option(envvar="ACT_AS")],
):
    with TradingClient(api_url, jwt, act_as) as client:
        withdraw_all_credits(client)


def withdraw_all_credits(client: TradingClient):
    acting_as = client.act_as(1)
    state = client.state()
    logger.info(f"Acting as {state.accounts[acting_as.account_id].name}")
    for portfolio in state.portfolios.values():
        account_id = portfolio.account_id
        account_name = state.accounts[account_id].name
        for owner_credit in portfolio.owner_credits:
            if owner_credit.credit == 0:
                continue
            owner_id = owner_credit.owner_id
            owner_name = state.accounts[owner_id].name
            if owner_name == "Nicholas Charette":
                continue
            logger.info(
                f"Withdrawing {owner_credit.credit} credits from {account_name} to {owner_name}"
            )
            client.act_as(owner_id)
            client.make_transfer(
                from_account_id=account_id,
                to_account_id=owner_id,
                amount=owner_credit.credit,
                note="Full Withdrawal",
            )
            client.act_as(1)


if __name__ == "__main__":
    app()
