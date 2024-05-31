"""
Command Line Interface
(stolen from RVsearch)
"""
from argparse import ArgumentParser

import raphs
import raphs.driver


def main():
    psr = ArgumentParser(
        description="RAPHS: (R)adial velocity (A)nalysis of (P)otential (H)WO (S)tars", prog='raphs'
    )
    psr.add_argument('--version',
        action='version',
        version="%(prog)s {}".format(raphs.__version__),
        help="Print version number and exit."
    )

    subpsr = psr.add_subparsers(title="subcommands", dest='subcommand')

    # In the parent parser, we define arguments and options common to
    # all subcommands.
    psr_parent = ArgumentParser(add_help=False)
    psr_parent.add_argument('--num_cpus',
                            action='store', default=8, type=int,
                            help="Number of CPUs [8]")
    psr_parent.add_argument('-d', '--data_dir', metavar='data directory',
                          type=str,
                          help="path to data directory", default='DATA'
                          )
    psr_parent.add_argument('-o', '--output_dir', metavar='output directory',
                          type=str,
                          help="path to place outputs", default='OUT'
                          )
    
    
    # Do everything
    psr_run = subpsr.add_parser('run', parents=[psr_parent], )
    psr_run.add_argument('hd_name', type=str,
                          help="System HD name"
                          )
    psr_run.add_argument('--search', action='store_true',
                          help="Run search [default=True]"
                          )
    psr_run.add_argument('--injrec', action='store_true',
                          help="Run injection/recovery [default=True]"
                          )
    psr_run.add_argument('--mcmc', action='store_true',
                          help="Run mcmc after search [default=True]"
                          )
    psr_run.add_argument('--sind', action='store_true',
                          help="Search S index values [default=False]"
                          )

    psr_run.set_defaults(func=raphs.driver.do_everything)

    args = psr.parse_args()

    args.func(args)

if __name__ == '__main__':
    main()