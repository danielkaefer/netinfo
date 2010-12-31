BIN = netinfo.py

install:
	cp $(BIN) /usr/bin/$(BIN)
	#chown root:root /usr/bin/$(BIN)
	#chmod u+s /usr/bin/$(BIN)

.PHONY: clean
clean:
	rm -f $(BIN)
