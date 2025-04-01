import rs1101.random_string as rs
import rs1101.random_format as rf
import click
import cloup


class Repo:
    pass


default_length = 10


@click.group(invoke_without_command=True)
@cloup.option_group(
    "candidate options",
    click.option(
        "-c",
        metavar="canddidate",
        type=click.Choice(list(rs.candidate_dict.keys())),
        multiple=True,
        default=rs.cddt_default,
    ),
    click.option("-cs", type=str, default=""),
    constraint=cloup.constraints.mutually_exclusive,
)
@click.option(
    "-l", metavar="the length of the generated string", type=int, default=None
)
@click.option(
    "-ss",
    metavar="show strength",
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option(
    "-s",
    metavar="secret string",
    type=str,
    default=None,
)
@click.pass_context
def cli(ctx, c, cs, l, ss, s):
    candidate = rs.g_candidate(c)
    if cs:
        candidate = cs
    ctx.obj = Repo()
    ctx.obj.candidate = candidate
    ctx.obj.length = l if l else default_length
    ctx.obj.ss = ss
    if ctx.invoked_subcommand is None:
        if l is None:
            l = default_length
        if s is not None:
            result = rs.s2rs(s, l, candidate)
        else:
            result = rs.random_string(l, candidate)
        print(result)
        show_strength(ctx.obj)
    else:
        if l is not None:
            raise click.BadOptionUsage(
                message="You should not use the -l option here when using the subcommand."
            )


@cli.command("rs2int")
@click.argument("s", metavar="a string", type=str)
@click.pass_obj
def cli_rs2int(obj, s):
    x = rs.rs2int(s, candidate=obj.candidate)
    obj.length = len(s)
    print(x)
    show_strength(obj)


@cli.command("int2rs")
@click.argument("x", metavar="a int", type=int)
@click.option(
    "-l", metavar="the length of the generated string", type=int, default=None
)
@click.pass_obj
def cli_int2rs(obj, x, l):
    s = rs.int2rs(x, length=l, candidate=obj.candidate)
    obj.length = len(s)
    print(s)
    show_strength(obj)


@cli.command("gen")
@click.option(
    "-l", metavar="the length of the generated string", type=int, default=default_length
)
@click.pass_obj
def cli_rs(obj, l):
    s = rs.random_string(l, candidate=obj.candidate)
    obj.length = l
    print(s)
    show_strength(obj)


def show_strength(obj):
    if obj.ss:
        print(f"strength:{rs.strength(obj.length,len(obj.candidate))}")


@cli.command("mac")
def rsmac():
    print(rf.random_mac())


if __name__ == "__main__":
    cli()
