#!/usr/bin/env bash

script=~/bin/tnt-is-dead

cat <<EOF > "$script"
#!/usr/bin/env bash
cd ~/workspace/tnt_is_dead
pipenv run python ./main.py \$*
EOF

chmod +x "$script"
