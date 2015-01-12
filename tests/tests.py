from ..macro import Macro


test_macros = {
    "test": "$custom",
    # "required": [],
    "required": ["test"],
    "macros": {
        "custom": [
            "$test ; $test;$test"
        ],
        "test": [
            ["$filex", "-2:"]
        ]
    }
}
print("%s" % (
    Macro.parse_macro(
        string=test_macros["test"],
        custom_macros=test_macros["macros"],
        required=test_macros["required"]
    ) or "None"
))
