#!/usr/bin/env zsh

cd $(dirname "$0")

new="pyquocca==$(yq '.project.version' pyproject.toml)"
echo Replacing existing pyquocca requirements with $new...

# Update example challenges
cd ../../challenges

for file in **/requirements.txt; do
    old=$(grep -E 'pyquocca==\d+\.\d+\.\d+' $file)
    if [[ $? == '0' ]]; then
        echo $(dirname $file): $old '-->' $new
        safe=$(sed 's/\./\\./g' <<<$old)
        sed -i.bak s/$safe/$new/g $file
        rm $file.bak
    else
        echo $(dirname $file): no pyquocca requirement
    fi
done
