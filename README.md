## Terminality

A Sublime Text 3 Plugin for Sublime Text Internal Terminal

### What is Terminality
Terminality is a plugin to allows Sublime Text to be used as Terminal. This included input and output from/to Sublime Text's buffer. Although Terminality can run many commands, it **is not gurranteed** that it can be used for all commands.

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
You can create your own macro to be used with custom command by adding each macro to `macros` section in your execution unit (See command format aboves). Each macro is a key-value pairs which key indicated macro name (without `$`) to be used and value is a list of string or pre-defined macros.