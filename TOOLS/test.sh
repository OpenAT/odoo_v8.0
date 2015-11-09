#!/usr/bin/env bash

# This is a simple test file - use it to test bash code or to note bash tricks


#http://mywiki.wooledge.org/BashFAQ/001
#psql -d intdadi_demo -t --field-separator-zero --quiet --single-transaction --set AUTOCOMMIT=off --set ON_ERROR_STOP=on --no-align  -c 'SELECT code, iso_code from res_lang'


# ATTENTION: This IS a generic solutions since the IFS delimiter NULL is used :)
# HINT: Sice we use a save NULL as the delimiter between fields we have to use read -d '' for all fields but the
#       last one of one record. The last field in the record will havae a newline after it and therefore starts the
#       next loop of the while cycle
# HINT: We do NOT use "IFS= read ..." since IFS= would prevent trimming of leading and trainling whitespace and
#       even this seems desired it gave unexpected results together with read!

declare -A installedlangs=( )
while read -r -d '' field_a && read -r field_b; do
    echo 'field_a: '${field_a}
    echo 'field_b: '${field_b}
    installedlangs[$field_a]=$field_b
done < <(psql -d intdadi_demo -w \
              -t --field-separator-zero --quiet --single-transaction --set AUTOCOMMIT=off --set ON_ERROR_STOP=on --no-align  \
              -c 'SELECT code, iso_code from res_lang')

# HINT: We do not need to check if key en_US exists since this is the default language therefore must be installed
installedlangs[en_US]=en

# Abfragen ob key all is
$Lang = $installedlangs

elsif (if der key in der $installedlangs)
$Lang[$5] = $installedlangs[$5]
else
exit


printf '\n\n'
echo "Found Langs:"
for code in "${!installedlangs[@]}"; do
    echo ${code}": "${installedlangs[$code]}
done
