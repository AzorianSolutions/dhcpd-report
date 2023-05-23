# DHCPd Report

A Python 3 tool for reporting DHCPd IP pool allocation from server configuration and lease files.

## TL;DR

```
git clone git@github.com:AzorianSolutions/dhcpd-report.git
cd dhcpd-report
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Place your `dhcpd.conf`, `dhcpd.leases`, and other related configuration files in subdirectories of `./data`
and run `./toolio.py`.  The script will generate a CSV report for each subdirectory of `./data` and save the
file to the `./reports` directory.

## [Donate](https://www.buymeacoffee.com/AzorianMatt)

Like my work?

<a href="https://www.buymeacoffee.com/AzorianMatt" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

**Want to sponsor me?** Please visit my organization's [sponsorship page](https://github.com/sponsors/AzorianSolutions).