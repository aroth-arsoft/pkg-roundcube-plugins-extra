get_orig_prefix() {
	echo "roundcube-plugins-extra_$(dpkg-parsechangelog | sed -n -e 's/^Version: \([^-]\+\)-.*$/\1/p').orig"
}

get_plugins() {
	awk '/^Plugin: / { print $2 }' debian/plugins.overview
}

get_plugin_field() {
	local plugin="$1"
	local field="$2"

	awk	-f debian/scripts/get-plugin-field.awk \
		-v "plugin=$plugin" \
		-v "field=$field" debian/plugins.overview
}

# Get a directory name for the given plugin
#
# The path is made of plugin name and version, mangled to be compatible with
# dpkg source format '3.0 (quilt)'.
get_plugin_dir() {
	local plugin="$1"
	local version

	version="$(get_plugin_field "$plugin" Version)"
	echo "$plugin" | sed -e 's/[^[:alnum:]-]/-/g'
}
