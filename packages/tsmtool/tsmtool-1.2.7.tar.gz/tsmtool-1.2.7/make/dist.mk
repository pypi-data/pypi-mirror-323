# python dist makefile

wheel := dist/$(module)-$(version)-py2.py3-none-any.whl
dependency_wheels := $(filter-out $(wildcard dist/*.whl),$(wheel))
version_dir = ~/.config/$(module)

$(wheel): $(src) pyproject.toml
	rm -f dist/$(module)-*.whl
	flit build
	mkdir -p $(version_dir)
	echo $(version) > $(version_dir)/version

wheel: $(wheel) depends

### build wheel 
dist: wheel 

dist-clean:
	[ -d dist ] && find dist -not -name README.md -not -name dist -exec rm -f '{}' + || true
	rm -rf build *.egg-info .eggs wheels

dist-sterile:
	@:
