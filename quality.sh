#!/bin/bash
customDie() {
    echo
    echo
    echo "ERROR:"
    echo "$1"
    echo
    echo
    exit 1
}

# pep8-3 says:
# pep8 has been renamed to pycodestyle (GitHub issue #466)
# Use of the pep8 tool will be removed in a future release.
# Please install and use `pycodestyle` instead.

if [ ! -f "`command -v pycodestyle-3`" ]; then
    customDie "pycodestyle-3 is missing. You must first install the python3-pycodestyle package."
fi

tmp_path=style-check-output.txt
if [ -f "$tmp_path" ]; then
    rm "$tmp_path" || customDie "rm \"$tmp_path\" failed."
fi
echo > "$tmp_path"
# for name in example-cli.py setup.py testing.pyw pypicolcd/lcdframebuffer.py pypicolcd/command_line.py pypicolcd/stats.py pypicolcd/__init__.py
for name in `ls *.py` `ls kivyglops/*.py`
do
echo "* checking '$name'..."
pycodestyle-3 $name  >> "$tmp_path"
done

if [ -f "`command -v outputinspector`" ]; then
    outputinspector "$tmp_path"
    # sleep 3
else
    cat "$tmp_path"
    cat <<END

Instead of cat, this script can use outputinspector if you install it
  (If you double-click on any error, outputinspector will tell Geany or
  Kate to navigate to the line and column in your program):

  <https://github.com/poikilos/outputinspector>

END
rm "$tmp_path"
fi

