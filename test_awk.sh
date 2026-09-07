#!/bin/bash
awk '{
  if ($0 ~ /title: '\''\[AI-Assisted\] Self-Heal Auto-Fix'\''/) {
    print "          title: '\''[AI-Assisted] Self-Heal Auto-Fix'\''";
  } else {
    print $0;
  }
}' .github/workflows/self-heal.yml > .github/workflows/self-heal.yml.new
mv .github/workflows/self-heal.yml.new .github/workflows/self-heal.yml
