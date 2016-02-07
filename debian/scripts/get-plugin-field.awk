/^Plugin: / {
	if ($2 == plugin) {
		in_plugin = 1
	}
	next
}
/^[A-z-]+:/ {
	if (in_field) {
		# print value in END
		exit 0
	}
	if (in_plugin) {
		if ($1 == field ":") {
			in_field = 1
			value = $2
		}
	}
}
/^ / {
	if (in_field) {
		if (value) {
			value = value "\n"
		}
		if ($1 != ".") {
			value = value substr($0, 2)
		}
	}
}
/^$/ {
	if (in_field) {
		# print value in END
		exit 0
	}
	if (in_plugin) {
		# print value in END
		exit 2
	}
	next
}
END {
	if (in_plugin) {
		if (value) {
			print value
			exit 0
		} else {
			print "Plugin `" plugin "' does not have field `" field "'." > "/dev/stderr"
			exit 2
		}
	}
	if (!in_plugin) {
		print "Plugin `" plugin "' not found." > "/dev/stderr"
		exit 1
	}
}
