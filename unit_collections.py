import sublime


class UnitCollections:

    @staticmethod
    def load_default_collections():
        execution_units = {}
        collections = sublime.find_resources("*.terminality-collections")
        for collection_file in collections:
            collection = sublime.decode_value(
                sublime.load_resource(collection_file)
            )
            if "execution_units" not in collection:
                continue
            for scope in collection["execution_units"]:
                scope_value = collection["execution_units"][scope]
                if not isinstance(scope_value, dict):
                    continue
                execution_units[scope] = UnitCollections.load_language_scopes(
                    scope_value,
                    execution_units[scope] if scope in execution_units else None
                )
        return execution_units

    @staticmethod
    def load_language_scopes(scope_value, scope=None):
        scope = scope or {}
        for command in scope_value:
            if not isinstance(scope_value[command], dict):
                continue
            scope[command] = scope_value[command]
        return scope
