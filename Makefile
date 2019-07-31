
init:
	virtualenv .

reset:
	virtualenv -clear .

clean:
	rm -fR bin .Python include lib pip-selfcheck.json

activate:
	source bin/activate
