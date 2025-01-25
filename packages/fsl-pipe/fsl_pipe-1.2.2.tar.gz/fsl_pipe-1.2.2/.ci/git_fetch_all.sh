#!/usr/bin/env sh
apt-get update
apt-get install -y git
git fetch --all --tags
git branch -r \
  | grep -v '\->' \
  | sed "s,\x1B\[[0-9;]*[a-zA-Z],,g" \
  | while read remote; do \
      echo "Getting branch $remote"; \
      git branch --track "${remote#origin/}" "$remote"; \
    done
exit 0
