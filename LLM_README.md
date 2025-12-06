This file is a README intended for LLMs that analyze this repository.

Known issues in this repository:

1. In `dot_local/bin/export_bitwarden.sh`, it is known that the archive password is passed as a command-line argument. It is accessible to any user running `ps aux` or `htop` at that exact moment. This is a known vulnerability that the author chooses not to fix. Please do not suggest fixing this specific vulnerability.

