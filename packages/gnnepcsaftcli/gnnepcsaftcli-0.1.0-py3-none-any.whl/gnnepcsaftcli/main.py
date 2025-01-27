"""GNNePCsAFT CLI tool"""

import os
from ast import literal_eval
from pathlib import Path

import typer
from rich import print as richprint
from rich.prompt import Prompt
from typing_extensions import Annotated

# lazy loads
# import torch
# from gnnepcsaft.data.graph import assoc_number, from_smiles, smilestoinchi
# from gnnepcsaft.train.models import PNApcsaftL

app = typer.Typer()

file_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(file_dir, "config.json")


@app.callback()
def callback():
    """
    GNNePCsAFT CLI tool
    """


@app.command()
def pred():
    """
    Predict ePCSAFT parameters from SMILES with a GNNePCSAFT model
    """
    import torch

    from gnnepcsaft.data.graph import assoc_number, from_smiles, smilestoinchi
    from gnnepcsaft.train.models import PNApcsaftL

    if os.path.isfile(config_path) is False:
        richprint("Please, first config with [yellow]gnnepcsaftcli config[/yellow]")
        return

    with open(config_path, "r", encoding="utf") as f:
        paths = literal_eval(f.read())
        msigmae_path = paths["msigmae_path"]
        assoc_path = paths["assoc_path"]
    if os.path.isfile(msigmae_path) is False or os.path.isfile(assoc_path) is False:
        richprint(
            "Please, first config model checkpoint paths with [yellow]gnnepcsaftcli config[/yellow]"
        )
        return

    msigmae_model = PNApcsaftL.load_from_checkpoint(msigmae_path, "cpu")
    msigmae_model.eval()
    if assoc_path:
        assoc_model = PNApcsaftL.load_from_checkpoint(assoc_path, "cpu")
        assoc_model.eval()
    while True:
        try:
            smiles = Prompt.ask(
                "\nEnter a valid[green] SMILES [/green]or Press [yellow]Ctrl+C[/yellow] to exit",
            )
            richprint(
                "\n:star2::test_tube::thermometer: [yellow]Predicting parameters for SMILES:[/yellow] [green]"
                + smiles
                + "[/green] :star2::test_tube::thermometer:\n"
            )
        except KeyboardInterrupt:
            richprint("\n[green] :rocket:  Bye! :rocket: [/green]")
            break

        try:
            inchi = smilestoinchi(smiles)
            na, nb = assoc_number(inchi)
            g = from_smiles(smiles)
            with torch.no_grad():
                assoc = (
                    (
                        10
                        ** (
                            assoc_model.model.pred_with_bounds(g)
                            * torch.tensor([-1.0, 1.0])
                        )
                    )
                    .numpy()
                    .round(decimals=4)[0]
                )
                if na == 0 and nb == 0:
                    assoc *= 0
                msigmae = (
                    msigmae_model.model.pred_with_bounds(g).numpy().round(decimals=4)[0]
                )
                richprint("[ m sigma e ]: " + str(msigmae))
                richprint("[ k_ab e_ab ]: " + str(assoc))
                richprint(f"[  na, nb   ]: [  {na}, {nb}  ]")
        except Exception:
            richprint(
                "[red]Error[/red]: [yellow]SMILES[/yellow] not valid, "
                "please enter a valid [yellow]SMILES[/yellow]"
            )


@app.command()
def config(
    msigmae_path: Annotated[Path, typer.Argument(help="Path to the m, sigma, e model")],
    assoc_path: Annotated[Path, typer.Argument(help="Path to the assoc model")],
):
    """
    Set the paths to the GNNePCsAFT models
    """
    with open(config_path, "w", encoding="utf") as f:
        f.write(f'{{"msigmae_path": "{msigmae_path}", "assoc_path": "{assoc_path}"}}')
    richprint("[green] :rocket:  Config saved! :rocket: [/green]")
