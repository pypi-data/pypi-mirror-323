BIN=ezchlog
UNIXEXT=
WINEXT=.exe
DST=target

.PHONY: help
help:
	@echo "rust targets":
	@echo "  - build                build a debug version"
	@echo "  - release              build a release version"
	@echo "  - list                 list release targets"
	@echo "  - multi-releases       create multiple releases with zig"
	@echo "  - docker-*             run make through cargo-zigbuild docker image"
	@echo "  - clean                clean the $(DST) directory"

.PHONY: clean
clean: $(DST)
	rm -rf $(DST)

$(DST)/debug/$(BIN):
	cargo build

.PHONY: build
build: $(DST)/debug/$(BIN)

$(DST)/release/ezchlog:
	cargo build --locked --release

$(DST)/$(BIN): $(DST)/release/$(BIN)
	upx --lzma --best -o $@ $<

.PHONY: release
release: $(DST)/$(BIN)

.PHONY: list
list:
	@echo $(DST)/$(BIN)-linux-x86_64$(UNIXEXT).sha256
	@echo $(DST)/$(BIN)-linux-aarch64$(UNIXEXT).sha256
	@echo $(DST)/$(BIN)-linux-arm$(UNIXEXT).sha256
	@echo $(DST)/$(BIN)-darwin-aarch64$(UNIXEXT).sha256
	@echo $(DST)/$(BIN)-darwin-x86_64$(UNIXEXT).sha256
	@echo $(DST)/$(BIN)-windows-x86_64$(WINEXT).sha256

.PHONY: docker-%
docker-%:
	docker run --rm -v "$${PWD}:/src:rw" -e "HUID=$$(id -u):$$(id -g)" -w /src messense/cargo-zigbuild bash -c "\
		(cd /usr/local/bin; curl -L https://github.com/upx/upx/releases/download/v4.2.4/upx-4.2.4-amd64_linux.tar.xz | tar xJf -; mv upx-4.2.4-amd64_linux/upx ./; rm -rf upx-4.2.4-amd64_linux); \
		make $(DST)/$*" \
		chown -R $${HUID:-$$(id -u):$$(id -g)} $(DST)

.PHONY: multi-releases
multi-releases: \
	$(DST)/$(BIN)-linux-x86_64$(UNIXEXT).sha256 \
	$(DST)/$(BIN)-linux-aarch64$(UNIXEXT).sha256 \
	$(DST)/$(BIN)-linux-arm$(UNIXEXT).sha256 \
	$(DST)/$(BIN)-darwin-aarch64$(UNIXEXT).sha256 \
	$(DST)/$(BIN)-darwin-x86_64$(UNIXEXT).sha256 \
	$(DST)/$(BIN)-windows-x86_64$(WINEXT).sha256

$(DST)/%.sha256: $(DST)/%
	sha256sum $< | sed 's, .*/, ,' > $@

$(DST)/%/release/$(BIN)$(UNIXEXT) $(DST)/%/release/$(BIN)$(WINEXT): /usr/local/bin/zig
	cargo zigbuild --locked --release --target $*

$(DST)/$(BIN)-linux-x86_64$(UNIXEXT): $(DST)/x86_64-unknown-linux-musl/release/$(BIN)$(UNIXEXT)
	upx --lzma --best -o $@ $<
$(DST)/$(BIN)-linux-aarch64$(UNIXEXT): $(DST)/aarch64-unknown-linux-musl/release/$(BIN)$(UNIXEXT)
	upx --lzma --best -o $@ $<
$(DST)/$(BIN)-linux-arm$(UNIXEXT): $(DST)/arm-unknown-linux-musleabihf/release/$(BIN)$(UNIXEXT)
	upx --lzma --best -o $@ $<
$(DST)/$(BIN)-darwin-aarch64$(UNIXEXT): $(DST)/aarch64-apple-darwin/release/$(BIN)$(UNIXEXT)
	upx --lzma --best --force-macos -o $@ $<
$(DST)/$(BIN)-darwin-x86_64$(UNIXEXT): $(DST)/x86_64-apple-darwin/release/$(BIN)$(UNIXEXT)
	upx --lzma --best --force-macos -o $@ $<
$(DST)/$(BIN)-windows-x86_64$(WINEXT): $(DST)/x86_64-pc-windows-gnu/release/$(BIN)$(WINEXT)
	upx --lzma --best -o $@ $<
