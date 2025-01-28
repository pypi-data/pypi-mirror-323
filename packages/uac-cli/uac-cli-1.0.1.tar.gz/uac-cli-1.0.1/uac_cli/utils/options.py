import click

output_option = click.option("--output", "-o", type=click.File("w"))
output_option_binary = click.option(
    "--output", "-o", type=click.File("wb", encoding="utf-16")
)
select_option = click.option(
    "--select", "-s", help="select which field to be returned. JSONPATH"
)
input_option = click.option("--input", "-i", type=click.File("r"), required=True)
input_option_binary = click.option(
    "--input", "-i", type=click.File("rb", encoding="utf-16"), required=True
)
