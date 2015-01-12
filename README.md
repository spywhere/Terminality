## Terminality

A Sublime Text 3 Plugin for Sublime Text's Internal Console

```
.
.
.
.
.
.
.
. IMAGE GOES HERE
.
.
.
.
.
.
.
```

### What is Terminality
Terminality is a plugin to allows Sublime Text to be used as Terminal. This included input and output from/to Sublime Text's buffer. Although Terminality can run many commands, it **is not gurranteed** that it can be used for all commands.

The command is language-based. Current version support the following languages...

- Lua
  - Run
- Python
  - Run as Python 2.7
  - Run as Python 3
- Ruby
  - Run
- Swift
  - Run

Is that it? No, Terminality allows you to add your own commands to be used inside Sublime Text. Please see the section belows for more informations.

### How to use it?
Just pressing `Ctrl+Key+R` and the menu will show up, let's you select which command to run.

`Key` is `Alt` in Windows, Linux, `Cmd` in OS X

### How can I created my own command to be used with Terminality?
You can create your own command to be used with Terminality by open Terminality user's setting file and set the settings in following format...

```
{
	... Your other settings ...
	"additional_execution_units": {
		"<Language scope to be used with>": {
			"<Action Name such as Compile or Run>": {
				// All keys in here can be omitted except "command"
				"location": "<String or Macro for location path will be used to run command>",
				"required": [<List of macro that have to be set before run (without $)>]
				"command": "<String or Macro to define command>",
				"platforms": [<List of supported platforms (value must be from sublime.platform())>]
				"read_only": <Boolean indicated whether Terminal is read-only or not>,
				"close_on_exit" <Boolean indicated whether buffer will be closed after the Terminal is terminated>
				"macros": {<A dictionary contains custom macros (See Macros section belows)>}
			}
		}
	},
	... Your other settings ...
}
```

Every macro name (except inside `required`) should have `$` prefix.

See example inside Terminality's settings file

### Predefined Macros
`file`: Path to current working file

`file_name`: Current working file name

`working`: This will use `working_project` but if not found it will use `project` and if still not found it will use `parent`

`working_project`: Project folder contains current working file

`project`: First project folder

`parent`: Parent folder contains current working file

`parent_name`: Parent folder name

`packages_path`: Path to Sublime Text's packages folder

`sep`: Path separator (`/` or `\` depends on your operating system)

`$`: `$` symbol

### Custom Macros
You can create your own macro to be used with custom command by adding each macro to `macros` section in your execution unit (See command format aboves). Each macro is a key-value pairs which key indicated macro name (`a-zA-Z0-9_` without prefixed `$`) to be used and value is a list of any combination of following values...

- `"String and/or $macro"` This will be a parsed string (which must not contains self-recursion) if previous value is not found
- `["Start:End"]` This will substring the previous value (if any) from `start` to `end`
- `["RegEx Pattern", <Optional Capture Group>]` This will return a specified group (or default match if not specified) from previous value matching
- `["String and/or $macro", "Start:End"]` This will substring the specified string/macro from `start` to `end` if previous value is not found
- `["String and/or $macro", "RegEx Pattern", <Optional Capture Group>]` This will return a specified group (or default match if not specified) from specified string/macro matching if previous value is not found

Substring works just like Python's substring. You can omitted `start` or `end` as you like.

Macro works as a sequence, if current macro is not found it will look at the next macro.

Example:

```
"CustomMacro": [
	"$file_name",
	[":-3"],
	["$file", "\\w+"],
	""
]
```